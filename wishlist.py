# -*- coding: utf-8 -*-

# Standard:
import locale
import scrapy
import os
import re

# Third party:
from scrapy.http.request import Request
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from lxml import etree as XML
from random import randint

# Ours:
import settings


# ----------------------------------------------------------------------------
class RandomUserAgentMiddleware( UserAgentMiddleware ):
	"""Bypass Amazon's 503 Service Unavailable"""
    
	def _get_rand_ua( self ):
		return 'Mozilla/5.{} (X11; Linux x86_64; rv:{}.{}) Gecko/20{}0101 Firefox/{}.{}'.format( 
			   randint( 0, 1000 ), 
			   randint( 10, 60 ), randint( 0, 1000 ), 
			   randint( 10, 20 ), 
			   randint( 10, 60 ), randint( 0, 1000 ))
	
	def process_request( self, request, spider ):
		request.headers.setdefault( b'User-Agent', self._get_rand_ua() )



# ----------------------------------------------------------------------------
class OfferListingItem:
	def __init__( self, row ):
		self.price      = 0.00
		self.ship_price = 0.00
		ship_price_str  = row.css( '.olpShippingPrice::text' ).get( default = '0' )  # "EUR 3,00" or missing if free shipping
		price_str       = row.css( '.olpOfferPrice::text'    ).get( default = '0' )  # "EUR 2,40"
		ship_price_mat  = re.match( '.*?(?P<amount>[0-9,.\']+)', ship_price_str )
		price_mat       = re.match( '.*?(?P<amount>[0-9,.\']+)', price_str      )
		
		if ship_price_mat:
			self.ship_price = locale.atof( ship_price_mat.group( 'amount' ))  # Comma vs dot
		
		if price_mat:
			self.price = locale.atof( price_mat.group( 'amount' ))   # Comma vs dot
		
		self.price = self.price + self.ship_price



# ----------------------------------------------------------------------------
class OfferListing:
	def __init__( self, response ):
		self.offers = [ OfferListingItem( row ) for row in response.css( '.olpOffer' )]
		self.best   = self.offers[0] if self.offers else None   # Amazon actually shows lowest price first



# ----------------------------------------------------------------------------
class Product:
	def __init__( self, li ):
		self.id = li.attrib['data-itemid']  # is not an ASIN
		
		# There's no attribute with a single ASIN value, always looks like "ASIN:1234567...|A1C2E3F..."
		actn_params     = li.attrib['data-reposition-action-params']  # JSON string
		actn_params_mat = re.match( '.*ASIN:(?P<asin>[0-9A-Za-z\-]+).*', actn_params )
		self.asin       = actn_params_mat.group( 'asin' ) if actn_params_mat else None
		
		# Misc values:
		rel_url         = li.css( 'a[id^=itemName]::attr(href)'        ).get( default = '' )
		self.imgurl     = li.css( 'img::attr(src)'                     ).get( default = '' )
		self.comment    = li.css( '#itemComment_' + self.id + '::text' ).get( default = '' )
		self.title      = li.css( '#itemName_'    + self.id + '::text' ).get( default = '' )
		self.url        = 'https://' + settings.AMAZON_HOST + rel_url
		self.offers_url = 'https://' + settings.AMAZON_HOST + '/gp/offer-listing/' + self.asin \
		                + '?f_new=true'           \
		                + '&f_usedLikeNew=true'   \
		                + '&f_usedVeryGood=true'  \
		                + '&f_usedGood=true'      \
		              # + '&f_usedAcceptable=true'
		
		# Creator: "by John Doe (Paperback)", "von: John Doe, Marie Jane", "in der Hauptrolle Maria C."
		self.by = li.css( '#item-byline-'  + self.id + '::text' ).get( default = '' )
		if self.by:
			self.by = re.sub( '^von: ',  '', self.by )
			self.by = re.sub( '^by ',    '', self.by )
			self.by = re.sub( '\(.*?\)', '', self.by )
		
		# Priority: Probably more reliable to check classes rather than (internal) values?
		# Try/except bc str() has no isnumeric() in Python 2, unicode() isnumeric can't negative values:
		prioNumOrLit = li.css( '#itemPriority_' + self.id + '::text' ).get( default = 'MEDIUM' )
		try:
			self.priority = int( prioNumOrLit )
		except:
			self.priority = { 'LOWEST' : -2, 'LOW' : -1, 'MEDIUM' : 0, 'HIGH' : 1, 'HIGHEST' : 2 }[ prioNumOrLit ]
		
		# Buy-price: Overrides default buy-price with specified one:
		# "yadda {BUY $50.23} yadda", "blabla { kaufe ab 21,45 EUR}", "{ab 77} yadda" 
		self.buyprice = settings.WISHLISTS_BUYPRICES[ self.priority ];  # Defaults
		buyprice_mat  = re.match( '{.*?(?P<amount>[0-9,.\']+).*?}', self.comment )
		if buyprice_mat:
			self.buyprice = locale.atof( buyprice_mat.group( 'amount' ))   # Comma vs dot
		
		# Price:
		self.price      = None
		self.price_l10n = 'n/a'
	
	
	def price_request( self ):
		return Request( self.offers_url, callback = self._parse_offers ) 
	
	def _parse_offers( self, offer_listing_response ):
		offers = OfferListing( offer_listing_response )
		if offers.best:
			self.price      = offers.best.price
			self.price_l10n = locale.currency( self.price )



# ----------------------------------------------------------------------------
class Wishlist:
	_last_response = None
	
	def __init__( self, response ):
		self.url      = response.url
		self.title    = response.css( '#profile-list-name::text' ).get( default = '' )
		self.products = []
		self._add_response( response )
		
	def __iter__( self ):
		return iter( self.products )
	
	def __len__( self ):
		return len( self.products )
	
	def _add_response( self, response ):
		prods = [ Product( li ) for li in response.css( 'li[data-price]' )]
		self.products.extend( prods )
		self._last_response = response
		
	def extend_request( self ):
		# Infinite scroll "pagination":
		lek = self._last_response.css( 'input[name="lastEvaluatedKey"]::attr(value)' ).get()
		return Request( self.url + '?lek=' + lek,  callback = self._add_response ) if lek else None



# ----------------------------------------------------------------------------
class YourLists:
	def __init__( self, response ):
		rel_urls  = response.css( '#your-lists-nav a[href^="/hz/wishlist/ls/"]::attr(href)' ).getall()
		self.urls = [ 'https://' + settings.AMAZON_HOST + u for u in rel_urls ]
	
	def __iter__( self ):
		return iter( self.filtered() )
	
	def __len__( self ):
		return len( self.filtered() )
	
	def filtered( self ):
		return [ u for u in self.urls if not u.startswith( tuple( settings.WISHLISTS_EXCLUDES ))]



# ----------------------------------------------------------------------------
class XmlWishlistReader:
	def __init__( self, filename = settings.WISHLISTS_XMLPATH ):
		self._xml = XML.parse( filename ) 
		
	def get_pricecut( self, product_id, new_price ):
		old_price = self._xml.xpath( "/amazon/wishlist/product[@id='" + product_id + "']/@price" )
		pricecut  = float(old_price[0]) - new_price if old_price else 0
		return pricecut if pricecut >= 0 else 0



# ----------------------------------------------------------------------------
class XmlWishlistWriter:
	def __init__( self, filename = settings.WISHLISTS_XMLPATH ):
		self.filename = filename
		self._old     = None
		if os.path.exists( filename ):
			try:
				self._old = XmlWishlistReader( filename )
			except:
				print( "[WARN] Old {} is corrupt and will be recreated".format( filename ))
	
	def __enter__( self ):
		self._xml = XML.ElementTree( XML.Element( 'amazon' ))
		base, ext = os.path.splitext( self.filename )
		xsl_path  = base + '.xslt'  # Dynamic name eases customization
		pi_xsl    = XML.ProcessingInstruction( 'xml-stylesheet', 'type="text/xsl" href="' + xsl_path + '"' )
		self._xml.getroot().addprevious( pi_xsl )
		return self
	
	def __exit__( self, type, value, traceback ):
		self._xml.write( self.filename, xml_declaration = True, pretty_print = True )
	
	def write_wl( self, wishlists ):
		for wl in wishlists:
			if len( wl ) > 0:
				wl_elem = XML.SubElement( self._xml.getroot(), 'wishlist' )
				XML.SubElement( wl_elem, 'title' ).text = wl.title
				XML.SubElement( wl_elem, 'url'   ).text = wl.url
				for product in wl:
					p_attr = {
						'id'       : product.id,
						'asin'     : product.asin,
						'price'    : str( product.price    ),  # US-format and w/o currency for comparison etc
						'priority' : str( product.priority ),
						'buyprice' : str( product.buyprice ),
						'pricecut' : str( self._old and self._old.get_pricecut( product.id, product.price ))
					}
					p_elem = XML.SubElement( wl_elem, 'product', p_attr )
					XML.SubElement( p_elem, 'url'     ).text = product.url
					XML.SubElement( p_elem, 'picture' ).text = product.imgurl
					XML.SubElement( p_elem, 'title'   ).text = product.title
					XML.SubElement( p_elem, 'by'      ).text = product.by
					XML.SubElement( p_elem, 'comment' ).text = product.comment
					XML.SubElement( p_elem, 'price'   ).text = product.price_l10n  # Localized format with currency



# ----------------------------------------------------------------------------
class WishlistsSpider( scrapy.Spider ):
	# Spider:
	name            = 'wishlists'
	start_urls      = [ settings.WISHLISTS_URL_ANY ]
	custom_settings = settings.SCRAPY_SETTINGS
	
	# My:
	_lists = [];
	
	# Spider:
	def closed( self, reason ):
		with XmlWishlistWriter() as w:
			w.write_wl( self._lists )
	
	def parse( self, response ):
		for url in YourLists( response ):
			yield Request( url, callback = self.parse_wl )
	
	# My:
	def parse_wl( self, response ):
		wl = Wishlist( response );
		while True:
			req = wl.extend_request()
			if not req: 
				break
			yield req
		
		for product in wl:
		    yield product.price_request()
			
		self._lists.append( wl )

