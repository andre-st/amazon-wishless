# Amazon-Wishlists Scraper, v1.0

I have over 60 Amazon wishlists and in some lists sometimes 100 products, mainly books. 
I often buy used books and checking all current (2nd hand) prices is time consuming. 
This scraper exports _all_ lists to a XML-file, 
with the items filtered according to a maximum price.


## This




## Requirements

- GNU/Linux operating system (other platforms not tested)
- Python 2.7.16
- Scrapy 1.7.3 (web crawling framework)
- pip (package installer for Python) to install Scrapy:
	`$ pip install scrapy`
	(pip is usally available in your package manager)



## Getting started

GNU/Linux terminal:

```sh
$ git clone https://github.com/andre-st/amazon-wishlist
$ cd amazon-wishlist
$ mv settings.py-example settings.py
$ vi settings.py        # vi or any other editor
	# Edit your wishlists settings
	# Edit your localization settings

$ ./wishlist.sh
$ firefox wishlist.xml
```


## Customization

Your wishlists are exported to `wishlist.xml`, which is generated based on:
- the filter rules in `settings.py` (MAXPRICE, EXCLUDES etc)
- the old `wishlist.xml` (if exists) in order to identify newcomers

Modern web-browsers display the exported XML-file based on:
- the HTML document structure rules in `wishlist.xslt` (headings, sections, ...)
- the HTML document presentation rules in `wishlist.css` (colors, fonts, ...)

The `wishlist.xslt` currently describes:
- a section that only displays newcomers
- a section that only displays the most important items from all lists together
- multiple sections for all individual lists with their items

XSLT is a declarative, Turing-complete language for transforming 
XML documents into other XML documents (HTML in this case). 
XSLT runs queries against the XML-file and feeds the result into templates
with placeholders. 

CSS is a stylesheet language used to describe how elements should be rendered
on screen etc.

XML, XSLT and CSS are supported by modern web-browsers out of the box.

