# Amazon-Wishlists Export & Price-Monitor, v1.4.3

![Maintenance](https://img.shields.io/maintenance/yes/2020.svg)

I have over 60 Amazon wishlists and in some lists sometimes 100 products, mainly books. 
I often buy used books and checking all current, continuously changing 2nd hand prices 
against my budget is time consuming. 
This Amazon-wishlist scraper exports _all_ lists to a XML-file.
The XML-file is displayed with all items filtered and re-ordered according to price, priority etc.
[What's new?](CHANGELOG.md)


## Exported XML (web-browser view)

![Screenshot](README-screenshot.png?raw=true "Screenshot")


## Requirements

- tested on the GNU/Linux operating system but might work on everything which runs Scrapy
- Python 2.7.16
- Scrapy 1.7.3 (web crawling framework)
- lxml (XML library)
- pip (package installer for Python) to install dependencies 
  (pip is usually available in the package manager of your Linux distribution)


## Getting started

GNU/Linux terminal:

```console
$ pip install scrapy lxml        # Install dependencies
$ git clone https://github.com/andre-st/amazon-wishless
$ cd amazon-wishless
$ mv settings.py-example settings.py
$ vi settings.py                 # vi or any other editor

Edit your wishlists settings
Edit your localization settings

$ scrapy runspider wishlist.py   # Get latest prices
$ firefox wishlist.xml           # View results
```


## Observations and limitations

**Latest version:**
- requires _public_ wishlists on Amazon
- the second hand price shown by Amazon may be low, but the final price is
  _sometimes_ realized on frivolously high shipping prices. 
  Shipping prices are currently not taken into account
- runtime is okay (53 long lists or 230 requests < 30 seconds)
- if many lists fail with "503 Service Unavailable" you need to 
  increase `SCRAPY_SETTINGS.DOWNLOAD_DELAY` in settings.py

**Amazon wishlists without used prices:**
- in some countries, Amazon no longer displays the used prices (Germany since March 2020):  
  ![Wishlist Item](README-amazon.png?raw=true "Wishlist Item")  
- although invisible, the used price can at least be read for items _not_ delivered by Amazon
- I had played with [another program-version](https://github.com/andre-st/amazon-wishless/tree/feat-offerlist-abandoned) that loads prices from the separate Offer-Listing page for each product
  (which would have included the shipping price too).  
  Given the amount of products and requests, this failed due to Amazon's rate limiting 
  (more and more '503 Service Unavailable' errors).
  Download-delay or faking request headers didn't do much.
  And the cost to send requests from different IP addresses in sufficient quantity would be 
  inconsistent with the project idea of finding _cheap_ deals.   
- unfortunately, this situation reduces the value of this project, 
  although our viewer still shows more information and is clearer

**Firefox 68+ XSLT CORS-issue:**
- Firefox doesn't load the local XSLT file anymore, which is referenced by the XML file and located in the same directory ("Cross Origin" and file URIs).
  It's required to transform the raw XML data into an useful report. You would have to...
	- visit `about:config` and disable `privacy.file_unique_origin`,
	- or access the files through a web-server



## Customization

Components (uppercase and shaded), their inputs (cells upwards) and outputs (cells to the right):

![Screenshot](README-custom.png?raw=true "Customization")

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


