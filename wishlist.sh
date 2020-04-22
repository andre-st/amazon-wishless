#!/usr/bin/env bash

BROWSER="firefox"
BROWSEROPTS=""


scrapy runspider wishlist.py || exit 1


if xsltproc --version > /dev/null
then
	echo "NOTE: Generating 'wishlist.html' from wishlist.xslt and wishlist.xml ..."
	xsltproc wishlist.xslt wishlist.xml > wishlist.html \
		&& $BROWSER $BROWSEROPTS wishlist.html
else
	echo "WARN: If displayed incorrectly, either install 'xsltproc' or visit 'about:config' and disable 'privacy.file_unique_origin'"
	$BROWSER $BROWSEROPTS wishlist.xml
fi


