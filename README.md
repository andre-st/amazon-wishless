# Amazon-Wishlists Scraper, v1.1

![Maintenance](https://img.shields.io/maintenance/yes/2019.svg)

I have over 60 Amazon wishlists and in some lists sometimes 100 products, mainly books. 
I often buy used books and checking all current (2nd hand) prices is time consuming. 
This scraper exports _all_ lists to a XML-file, 
with the items filtered according to price, priority etc.


## Sample output

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


## Customization

Components (uppercase), their inputs (cells upwards) and outputs (cells to the right):

```text
  settings.py       |  wishlist.xslt     |  wishlist.css      |                    |
  (filter-rules,    |  (headings,sort    |  (colors,fonts,    |                    |
   filenames)       |   order,sections)  |   margins)         |                    |
                    |                    |                    |                    |
  wishlist.xml      |                    |                    |                    |
  (to id changes)   |                    |                    |                    |
                    |                    |                    |                    |
  amazon-website    |                    |                    |                    |
  (lists,           |                    |                    |                    |
   priorities)      |                    |                    |                    |
--------------------+--------------------+--------------------+--------------------|
::::::::::::::::::::|  wishlist.xml*     |                    |                    |
::SCRAPER:::::::::::|  (semistructured   |                    |                    |
::::::::::::::::::::|   data)            |                    |                    |
::::::::::::::::::::|                    |                    |                    |
--------------------+--------------------+--------------------+--------------------|
                    |::::::::::::::::::::|                    |                    |
                    |::BROWSER-INTERN::::|  generated html    |                    |
                    |::XSLT-PROCESSOR::::|  (in-memory)       |                    |
                    |::::::::::::::::::::|                    |                    |
--------------------+--------------------+--------------------+--------------------|
                    |                    |::::::::::::::::::::|                    |
                    |                    |::BROWSER:::::::::::|  rendered webpage  |
                    |                    |::::::::::::::::::::|                    |
```


XSLT is a declarative, Turing-complete language for transforming 
XML documents into other XML documents (HTML in this case). 
XSLT runs queries against the XML-file and feeds the result into templates
with placeholders. The web-browser automatically loads and processes the XSLT and CSS files
for `wishlist.xml`. XML, XSLT and CSS are supported by modern web-browsers out of the box.

**Remarks:**

One could do the filtering through the XSLT-file too, 
but tracking changes wouldn't work properly anymore (with just 1 XML-file at least).



## Feedback

If you like this project, you can "star" it on GitHub.
Report bugs or suggestions [via GitHub](https://github.com/andre-st/amazon-wishlist/issues)
or see the [AUTHORS.md](AUTHORS.md) file.



## See also

- [Andre's Goodreads Toolbox](https://github.com/andre-st/goodreads/blob/master/README.md)


