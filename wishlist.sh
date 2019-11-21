#!/usr/bin/env bash

#scrapy runspider --nolog wishlist.py > output.html
scrapy runspider wishlist.py  &&  firefox --new-tab wishlist.xml


