# Amazon-Wishlists Scraper, v1.0

I have over 60 Amazon wishlists and in some lists sometimes 100 products, mainly books. 
I often buy used books and checking all current (2nd hand) prices is time consuming. 
This scraper exports _all_ lists to a XML-file, 
with the items filtered according to price, priority etc.


## This

![Screenshot](README-screenshot.png?raw=true "Screenshot")


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

Components, inputs and outputs:

```text
                  |                  |
settings.py       | wishlist.xslt    | wishlist.css
wishlist.xml      |                  |
------------------+------------------+-----------------
::::::::::::::::::|                  |
::SCRAPER:::::::::| wishlist.xml*    |
::::::::::::::::::|                  |
------------------+------------------+-----------------
                  |::::::::::::::::::|
                  |::BROWSER-INTERN::| html
                  |::XSLT-PROCESSOR::|
------------------+------------------+-----------------
                  |                  |:::::::::::::::::
                  |                  |::BROWSER::::::::
                  |                  |:::::::::::::::::

top-to-bottom: inputs
left-to-right: outputs
```

The scraper exports to `wishlist.xml`, which is generated based on:
- the filter rules in `settings.py` (MAXPRICE, EXCLUDES, MINPRIORITY etc)
- the old `wishlist.xml` (if exists) in order to identify changes

Modern web-browsers don't just display the exported XML-file but can format it based on:
- the HTML document structure rules in `wishlist.xslt` (headings, sections, ...)
- the HTML document presentation rules in `wishlist.css` (colors, fonts, ...)

The `wishlist.xslt` currently declares:
- a section that only displays changes (newcomers)
- a section that only displays the most important items from all lists together
- multiple sections for all individual lists with their items

XSLT is a declarative, Turing-complete language for transforming 
XML documents into other XML documents (HTML in this case). 
XSLT runs queries against the XML-file and feeds the result into templates
with placeholders. 

CSS is a stylesheet language used to describe how elements should be rendered
on screen etc.

XML, XSLT and CSS are supported by modern web-browsers out of the box.

**Remarks:**

One could do the filtering through the XSLT-file too, 
but tracking changes wouldn't work properly anymore (with just 1 XML-file at least).



## Feedback

If you like this project, you can "star" it on GitHub.
Report bugs or suggestions [via GitHub](https://github.com/andre-st/amazon-wishlist/issues)
or see the [AUTHORS.md](AUTHORS.md) file.



## See also

- [Andre's Goodreads Toolbox](https://github.com/andre-st/goodreads/blob/master/README.md)


