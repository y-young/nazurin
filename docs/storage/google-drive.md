# Google Drive

<https://drive.google.com/>

## Before Use

Google Drive storage works perfectly under either of the following conditions:

- You don't need more than **15GB space** for `STORAGE_DIR`
- You're using a folder on a **Team Drive** as `STORAGE_DIR`

This implementation uses _Service Account_ to access your drive. Due to the limits of Google API, the owner of the files uploaded will be the service account, and according to Shared Folder policy, the files uploaded to shared folders will occupy the storage space of the owner, unless the shared folder is on a Team Drive.

Thus, if you're using a shared folder on your **Personal Drive**, there'll will be a 15GB storage limit due to the quota of service account; but if you're using a **Team Drive**, then you have nothing to worry about.

## Instructions

1.  Log into [GCP Console](https://console.cloud.google.com/)
2.  Enable Google Drive API (<https://developers.google.com/drive/api/v3/enable-drive-api#enable_the_drive_api>)
3.  Create a service account and download key file (<https://cloud.google.com/iam/docs/creating-managing-service-account-keys#iam-service-account-keys-create-console>),
    you can reuse the service account of Firebase if you already have one
4.  Manually create a folder on your drive (Personal/Team)
5.  Share the folder with the service account you created before, be sure to set proper permissions
6.  Set all required environment variables

## Configuration

### STORAGE

Append `GoogleDrive`. For more information, see [Configuration](../getting-started/configuration.md/#storage).

### GD_FOLDER

:material-exclamation-thick: Required

Folder ID of `STORAGE_DIR` on your drive.

Enter the folder and find it in the URL, e.g.: `https://drive.google.com/drive/u/1/folders/{FOLDER_ID}`

### GD_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS

:material-exclamation-thick: Required

Path to the key file or the content of it.

`GD_CREDENTIALS` has higher priority than `GOOGLE_APPLICATION_CREDENTIALS`, if `GD_CREDENTIALS` is not set, then `GOOGLE_APPLICATION_CREDENTIALS` is used.

!!! tip

    If you're using [Firestore](../database/firestore.md) database and have already set `GOOGLE_APPLICATION_CREDENTIALS`, you don't need to do anything :)
