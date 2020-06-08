#!/usr/bin/env bash

DEFAULT_BROWSER=${BROWSER:-firefox}
DEFAULT_BROWSEROPTS=""

scrapy runspider wishlist.py || exit 1

$DEFAULT_BROWSER $DEFAULT_BROWSEROPTS wishlist.html



