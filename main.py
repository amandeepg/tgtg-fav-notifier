import argparse
import configparser
import os
import pprint
import subprocess
from argparse import ArgumentParser
from configparser import ConfigParser
from sys import platform
from typing import Any

import yaml
from plyer import notification
from tgtg import TgtgClient

if platform == "linux" or platform == "linux2":
    if os.getenv("XDG_RUNTIME_DIR") is None:
        xdg_runtime_dir: str = f'/run/user/{subprocess.check_output("id -u", shell=True).strip().decode("utf-8")}'
        os.environ["XDG_RUNTIME_DIR"] = xdg_runtime_dir

parser: ArgumentParser = argparse.ArgumentParser(
    description="Too Good To Go Favorites Notifier."
)
parser.add_argument("--login", action="store")

args = parser.parse_args()
config: ConfigParser = configparser.ConfigParser()
home_dir: str = os.path.expanduser("~")
config_file_name: str = f"{home_dir}/.tgtg-fav-notifier.ini"
prev_items_file_name: str = f"{home_dir}/.tgtg-fav-notifier-items"
optional_command = f"{home_dir}/.tgtg-fav-notifier-hook.sh"

CONFIG_FILE_SECTION: str = "DEFAULT"
pp = pprint.PrettyPrinter(indent=4)

if args.login:
    print(f"Logging into the TGTG account for {args.login}.")
    credentials: dict[str, Any] = TgtgClient(email=args.login).get_credentials()
    config[CONFIG_FILE_SECTION] = {
        "access_token": credentials["access_token"],
        "refresh_token": credentials["refresh_token"],
        "user_id": credentials["user_id"],
        "cookie": credentials["cookie"],
    }
    with open(config_file_name, "w") as configfile:
        config.write(configfile)
    print("Done logging in, you can now run without --login")
else:
    config.read(config_file_name)
    client: TgtgClient = TgtgClient(
        access_token=config[CONFIG_FILE_SECTION]["access_token"],
        refresh_token=config[CONFIG_FILE_SECTION]["refresh_token"],
        user_id=config[CONFIG_FILE_SECTION]["user_id"],
        cookie=config[CONFIG_FILE_SECTION]["cookie"],
    )
    items = client.get_items()
    available_items = filter(lambda item: (item["items_available"] > 0), items)
    available_items_names = list(
        map(lambda item: (item["display_name"]), available_items)
    )

    prev_available_items_names = None
    if os.path.exists(prev_items_file_name):
        with open(prev_items_file_name) as file:
            prev_available_items_names = yaml.full_load(file)

    with open(prev_items_file_name, "w") as file:
        yaml.dump(available_items_names, file)

    print("Currently available: ")
    pp.pprint(available_items_names)
    print("Previously available: ")
    pp.pprint(prev_available_items_names)

    for available_items_name in available_items_names:
        if (
            prev_available_items_names is None
            or available_items_name not in prev_available_items_names
        ):
            notification.notify(
                title="TGTG Fav Notifier",
                message=f"{available_items_name} has food available now",
                app_icon="",
                timeout=10,
            )

            subprocess.call(
                f'{optional_command} "TGTG Fav Notifier" "{available_items_name} has food available now"',
                shell=True,
            )
