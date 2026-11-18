import json
import os
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

from nazurin.models import Caption
from nazurin.utils import Request, logger
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from . import config
from .models import REFERER, XfolioIllust, XfolioImage, get_cookies


class Xfolio:
    @network_retry
    async def get_post(self, creator: str, work_id: str | int) -> tuple[dict, str]:
        """Fetch a work page and parse its metadata, image URLs, and CSRF token."""
        url = f"https://xfolio.jp/portfolio/{creator}/works/{work_id}"
        async with (
            Request(
                headers={"Referer": REFERER},
                cookies=get_cookies(),
            ) as request,
            request.get(url) as response,
        ):
            if response.status == HTTPStatus.NOT_FOUND:
                raise NazurinError("Work not found")
            response.raise_for_status()

            if response.url.path.startswith("/system/recaptcha"):
                if config.SESSION:
                    logger.warning("XFOLIO_SESSION is invalid or expired")
                    raise NazurinError("XFOLIO_SESSION is invalid or expired")
                raise NazurinError(
                    "Bot protection (reCAPTCHA) is enabled for this portfolio, "
                    "please configure XFOLIO_SESSION",
                )

            html = await response.text()
            post, csrf_token = self.parse_html(html, creator, int(work_id), url)
            if config.SESSION and not post.get("is_logged_in"):
                logger.warning("XFOLIO_SESSION is invalid or expired")
                raise NazurinError("XFOLIO_SESSION is invalid or expired")
            return post, csrf_token

    async def fetch(self, creator: str, work_id: str | int) -> XfolioIllust:
        post, csrf_token = await self.get_post(creator, work_id)
        if config.SESSION:
            if config.BOOKMARK:
                await self.bookmark(post, csrf_token)
            if config.LIKE:
                await self.like(post, csrf_token)
        imgs = self.get_images(post)
        caption = self.build_caption(post)
        return XfolioIllust(int(post["id"]), imgs, caption, post)

    @network_retry
    async def bookmark(self, post: dict, csrf_token: str) -> bool:
        """Add work to favorites (bookmarks) when logged in."""
        work_id = post["id"]
        if not post.get("is_logged_in") or not csrf_token:
            logger.warning("XFOLIO_SESSION is invalid or expired")
            raise NazurinError("XFOLIO_SESSION is invalid or expired")
        if post.get("is_favorited"):
            logger.info("Work {} is already bookmarked", work_id)
            return True

        async with (
            Request(
                headers={
                    "Referer": post["url"],
                    "X-Requested-With": "XMLHttpRequest",
                },
                cookies=get_cookies(),
            ) as request,
            request.put(
                "https://xfolio.jp/api/v1/favorite",
                json={
                    "content_id": int(work_id),
                    "content_type": "work",
                    "list_id": 0,
                    "csrf_token": csrf_token,
                },
            ) as response,
        ):
            response.raise_for_status()
            post["is_favorited"] = True
            logger.info("Bookmarked work {}", work_id)
            return True

    @network_retry
    async def like(self, post: dict, csrf_token: str) -> bool:
        """Like work when logged in."""
        work_id = post["id"]
        if not post.get("is_logged_in") or not csrf_token:
            logger.warning("XFOLIO_SESSION is invalid or expired")
            raise NazurinError("XFOLIO_SESSION is invalid or expired")
        if post.get("is_liked"):
            logger.info("Work {} is already liked", work_id)
            return True

        async with (
            Request(
                headers={
                    "Referer": post["url"],
                    "X-Requested-With": "XMLHttpRequest",
                },
                cookies=get_cookies(),
            ) as request,
            request.post(
                "https://xfolio.jp/api/v1/like",
                json={
                    "content_id": int(work_id),
                    "content_type": "work",
                    "csrf_token": csrf_token,
                },
            ) as response,
        ):
            response.raise_for_status()
            post["is_liked"] = True
            logger.info("Liked work {}", work_id)
            return True

    @staticmethod
    def parse_html(
        html: str,
        creator: str,
        work_id: int,
        url: str,
    ) -> tuple[dict, str]:
        """Parse work metadata, image URLs, and CSRF token from Xfolio work HTML."""
        soup = BeautifulSoup(html, "html.parser")
        detail = soup.select_one(".article--detailInfo")
        if not detail:
            raise NazurinError("Work not found")

        csrf_meta = soup.select_one('meta[name="csrf_token"]')
        csrf_token = csrf_meta.get("content", "") if csrf_meta else ""
        logged_in_meta = soup.select_one('meta[name="is_logged_in"]')
        is_logged_in = logged_in_meta.get("content") == "1" if logged_in_meta else False

        title_el = detail.select_one(".article--detailInfo__title")
        title = title_el.get_text(strip=True) if title_el else ""

        desc_el = detail.select_one(
            ".article--detailInfo__text .detailInfo__text_pg",
        ) or detail.select_one(".article--detailInfo__text")
        description = ""
        if desc_el:
            for br in desc_el.find_all("br"):
                br.replace_with("\n")
            description = desc_el.get_text().strip()

        creator_el = soup.select_one(".creator-info__mount") or soup.select_one(
            ".button--follow__mount",
        )
        portfolio_url = f"https://xfolio.jp/portfolio/{creator}"
        user = {
            "id": creator_el.get("data-creator-id", "") if creator_el else "",
            "user_id": creator_el.get("data-creator-user-id", "") if creator_el else "",
            "code": creator,
            "name": (
                creator_el.get("data-creator-name") or creator
                if creator_el
                else creator
            ),
            "profile": creator_el.get("data-creator-profile", "") if creator_el else "",
            "url": (
                creator_el.get("data-creator-portfolio-top-url") or portfolio_url
                if creator_el
                else portfolio_url
            ),
        }

        like_el = detail.select_one(".button--detail_like__mount")
        fav_el = detail.select_one(".button--detail_favorite__mount")
        likes_num = int(like_el.get("data-likes-num") or 0) if like_el else 0
        favorites_num = int(fav_el.get("data-favorites-num") or 0) if fav_el else 0
        is_liked = bool(like_el and like_el.get("data-is-liked") == "1")
        is_favorited = bool(fav_el and fav_el.get("data-is-favorited") == "1")

        tags: list[str] = []
        tag_el = detail.select_one(".list--detail_tag__mount")
        if tag_el and tag_el.get("data-tags"):
            try:
                raw_tags = json.loads(tag_el["data-tags"])
                tags = [
                    tag["name"]
                    for tag in raw_tags
                    if isinstance(tag, dict) and tag.get("name")
                ]
            except json.JSONDecodeError:
                tags = []

        series = None
        series_mount = soup.select_one(".button--series-watch__mount")
        series_link = soup.select_one(".article--pagination__title p a")
        if series_mount or series_link:
            series = {
                "id": series_mount.get("data-series-id", "") if series_mount else "",
                "title": series_link.get_text(strip=True) if series_link else "",
                "url": series_link.get("href", "") if series_link else "",
            }

        images = Xfolio.parse_images(soup, work_id)
        post = {
            "id": work_id,
            "title": title,
            "description": description,
            "url": url,
            "user": user,
            "tags": tags,
            "series": series,
            "likes_num": likes_num,
            "favorites_num": favorites_num,
            "is_liked": is_liked,
            "is_favorited": is_favorited,
            "is_logged_in": is_logged_in,
            "images": images,
        }
        return post, csrf_token

    @staticmethod
    def parse_images(soup: BeautifulSoup, work_id: int) -> list[dict]:
        """Extract preview and full-scale image URLs from work page DOM."""
        images: list[dict] = []
        for wrap in soup.select(".article--img__wrap .article__wrap_img"):
            img_el = wrap.select_one("img")
            if not img_el:
                continue
            preview_url = img_el.get("src") or img_el.get("data-src")
            if not preview_url:
                continue

            fullscale_url = None
            image_id = None
            open_link = wrap.select_one('a.openIcon[href*="fullscale_image"]')
            if open_link and open_link.get("href"):
                query = parse_qs(urlparse(open_link["href"]).query)
                image_id = query.get("image_id", [None])[0]
                if image_id:
                    fullscale_url = (
                        f"https://xfolio.jp/user_asset.php?id={image_id}"
                        f"&work_id={work_id}&work_image_id={image_id}&type=work_image"
                    )

            images.append(
                {
                    "url": fullscale_url or preview_url,
                    "thumbnail": preview_url if fullscale_url else None,
                    "filename": os.path.basename(urlparse(preview_url).path),
                    "image_id": image_id,
                },
            )

        if not images:
            raise NazurinError("No image found")
        return images

    @staticmethod
    def get_images(post: dict) -> list[XfolioImage]:
        """Build Image list from parsed post data."""
        images = post.get("images", [])
        if not images:
            raise NazurinError("No image found")

        imgs = []
        for index, img in enumerate(images):
            destination, filename = Xfolio.get_storage_dest(post, img, index)
            imgs.append(
                XfolioImage(
                    filename,
                    img["url"],
                    destination,
                    thumbnail=img.get("thumbnail"),
                ),
            )
        return imgs

    @staticmethod
    def get_storage_dest(
        post: dict,
        img: dict,
        index: int = 0,
    ) -> tuple[str, str]:
        """Format destination and filename."""
        filename, extension = os.path.splitext(img["filename"])
        context = {
            **post,
            # Original filename, without extension
            "filename": filename,
            "extension": extension,
            "index": index,
            "image_id": img.get("image_id"),
        }
        return (
            config.DESTINATION.format_map(context),
            config.FILENAME.format_map(context) + extension,
        )

    @staticmethod
    def build_caption(post: dict) -> Caption:
        user = post["user"]
        tags = post.get("tags", [])
        tag_string = " ".join(["#" + tag for tag in tags])
        return Caption(
            {
                "title": post["title"],
                "author": f"{user['name']} #{user['code']}",
                "url": post["url"],
                "text": post.get("description", ""),
                "tags": tag_string,
            },
        )
