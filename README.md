# Amazon-Wishlists Export & Price-Monitor, v1.2

![Maintenance](https://img.shields.io/maintenance/yes/2019.svg)

I have over 60 Amazon wishlists and in some lists sometimes 100 products, mainly books. 
I often buy used books and checking all current, continuously changing 2nd hand prices 
against my budget is time consuming. 
This Amazon-wishlist scraper exports _all_ lists to a XML-file.
The XML-file is displayed with all items filtered and re-ordered according to price, priority etc.
[What's new?](CHANGELOG.md)


## Exported XML (web-browser view)

![Screenshot](README-screenshot.png?raw=true "Screenshot")


## Requirements

- GNU/Linux operating system (other platforms not tested)
- Python 2.7.16
- Scrapy 1.7.3 (web crawling framework)
- lxml (XML library)
- pip (package installer for Python) to install dependencies:
	`$ pip install scrapy lxml`
	(pip is usually available in your package manager)


## Getting started

GNU/Linux terminal:

```console
$ git clone https://github.com/andre-st/amazon-wishlist
$ cd amazon-wishlist
$ mv settings.py-example settings.py
$ vi settings.py        # vi or any other editor

Edit your wishlists settings
Edit your localization settings

$ scrapy runspider wishlist.py
$ firefox wishlist.xml
```


## Observations and limitations

- requires _public_ wishlists
- the second hand price shown by Amazon may be low, but the final price is
  _sometimes_ realized on frivolously high shipping prices. 
  Shipping prices are currently not taken into account
- runtime is okay (64 long lists or 230 requests < 30s), requests seem not throttled


## Customization

Components (uppercase and shaded), their inputs (cells upwards) and outputs (cells to the right):

```text
  settings.py       |  wishlist.xslt     |  wishlist.css      |                    |
  (filter-rules I,  |  (filter-rules II, |  (colors,fonts,    |                    |
   filenames)       |   headings,sort    |   margins)         |                    |
                    |   order,sections   |                    |                    |
  old wishlist.xml  |   in xml-viewer)   |                    |                    |
  (to id changes)   |                    |                    |                    |
                    |                    |                    |                    |
  amazon-website    |                    |                    |                    |
  (lists,priority)  |                    |                    |                    |
--------------------+--------------------+--------------------+--------------------|
::::::::::::::::::::|  wishlist.xml      |                    |                    |
::SCRAPER:::::::::::|  (semistructured   |                    |                    |
::::::::::::::::::::|   data)            |                    |                    |
::::::::::::::::::::|                    |                    |                    |
--------------------+--------------------+--------------------+--------------------|
::::::::::::::::::::|::::::::::::::::::::|                    |                    |
::::::::::::::::::::|::BROWSER-INTERN::::|  generated xhtml   |                    |
::::::::::::::::::::|::XSLT-PROCESSOR::::|  (in-memory)       |                    |
::::::::::::::::::::|::::::::::::::::::::|                    |                    |
--------------------+--------------------+--------------------+--------------------|
::::::::::::::::::::|::::::::::::::::::::|::::::::::::::::::::|                    |
::::::::::::::::::::|::::::::::::::::::::|::BROWSER:::::::::::|  pretty xml-viewer |
::::::::::::::::::::|::::::::::::::::::::|::::::::::::::::::::|  (see screenshot)  |
::::::::::::::::::::|::::::::::::::::::::|::::::::::::::::::::|                    |
```

XSLT is a declarative, Turing-complete language for transforming 
XML documents into other XML documents (XHTML in this case). 
XSLT runs queries against the XML-file and feeds the result into templates
with placeholders. The web-browser automatically loads and processes the XSLT and CSS files
for `wishlist.xml`. XML, XSLT and CSS are supported by modern web-browsers out of the box.

For your own XSLT-file just change the `WISHLISTS_XMLPATH` value in `settings.py`.


## Feedback

If you like this project, you can "star" it on GitHub.
Report bugs or suggestions [via GitHub](https://github.com/andre-st/amazon-wishlist/issues)
or see the [AUTHORS.md](AUTHORS.md) file.


## See also

- [Andre's Goodreads Toolbox](https://github.com/andre-st/goodreads/blob/master/README.md)


