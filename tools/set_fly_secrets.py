import subprocess

from dotenv import dotenv_values

config = dotenv_values(".env")
secrets = " ".join([f'{k}="{v}"' for k, v in config.items()])
command = f"fly secrets set {secrets}"
print(command)  # noqa: T201
subprocess.run(command, shell=True, check=True)
