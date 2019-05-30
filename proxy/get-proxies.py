#!/usr/bin/env python3
# import fcntl
import logging
import os
import sys
from multiprocessing.pool import ThreadPool

import requests
from lxml import html

# from crawl import settings
# from .discord import discord


# Logging config
LOG_LEVEL_STR = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
LOG_LEVEL = logging.getLevelName(LOG_LEVEL_STR)

FORMAT = '[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s'

logger = logging.getLogger('app')
logging.basicConfig(stream=sys.stderr, level=LOG_LEVEL, format=FORMAT)

logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

# Basic config
# BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def get_free_proxies():
    page = requests.get('https://free-proxy-list.net/')
    tree = html.fromstring(page.content)

    rows = tree.xpath("//tr")

    proxies = []
    for row in rows:
        try:
            ip = row.xpath("td/text()")[0]
            port = row.xpath("td/text()")[1]
            proxies.append("http://{}:{}".format(ip, port))
        except Exception:
            pass
    return proxies


def check_proxy(proxy):
    logger.debug(f'Check proxy: {proxy}')
    try:
        requests.get("https://example.org",
                     proxies={'https': proxy}, timeout=3)
        return proxy
    except Exception as e:
        logger.error(f'Error: {e}')
        return None


def get_proxies():
    """
    Get list proxies from cms

    :return: list
    """
    proxies = get_free_proxies()

    pool = ThreadPool(50)
    active_proxies = pool.map(check_proxy, proxies)
    active_proxies = [x for x in active_proxies if x is not None]

    if not active_proxies:
        # discord.send_message("No proxy to use")
        raise Exception("No proxy to use")

    return active_proxies


def main():
    logger.info('Get proxies')
    proxies = get_proxies()

    logger.info(f'Result: {len(proxies)}')

    for proxy in proxies:
        print(proxy)

    with open('proxy_result.txt', 'w') as f:
        f.write('\n'.join(proxies))


if __name__ == '__main__':
    main()
