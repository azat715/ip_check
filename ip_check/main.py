import ipaddress
from collections import namedtuple
from os import environ
from urllib.parse import urljoin

import fire
import requests

from .db import add_item, show_items

env = environ

TOKEN = env["TOKEN"]

BASE_URL = "https://ipinfo.io"

PAYLOAD = {
    "token": TOKEN,
}

Record = namedtuple("Record", ["ip", "city", "region", "country"])


def create_record(obj):
    return Record(obj["ip"], obj["city"], obj["region"], obj["country"])


def validate_ip(ip):
    try:
        ip = ipaddress.ip_address(ip)
    except ValueError:
        print("address/netmask is invalid: %s" % ip)
        raise Exception


def check_ip(ip):
    validate_ip(ip)
    url = urljoin(BASE_URL, str(ip))
    r = requests.get(url, params=PAYLOAD).json()
    if r.get("status"):
        print(f"Не валидный ip: {ip}")
        print(r)
        raise Exception
    elif r.get("bogon"):
        print(f"Немаршрутизируемый(bogon) ip: {ip}")
        print(r)
        raise Exception
    else:
        return create_record(r)


def add(ip):
    res = check_ip(ip)
    add_item(res)


def show(limit=5):
    for index, item in enumerate(show_items()):
        print(item)
        if index == limit:
            break
    # for item in show_items():
    #     print(item)


def cli():
    fire.Fire(
        {
            "add": add,
            "show": show,
        }
    )
