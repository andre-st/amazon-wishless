# -*- coding: utf-8 -*-

# Standard:
import locale
import scrapy
import os
import re

# Third party:
from scrapy.http.request import Request
from lxml import etree as XML

# Ours:
import settings



# ----------------------------------------------------------------------------
class Product:
	def __init__( self, li ):
    		self.id        = li.attrib['data-itemid']  # is not an ASIN
		used_price_str =      li.css( '.itemUsedAndNewPrice::text'          ).get( None )
		rel_url        =      li.css( 'a[id^=itemName]::attr(href)'         ).get( default = '' )
		self.imgurl    =      li.css( 'img::attr(src)'                      ).get( default = '' )
		self.priority  = int( li.css( '#itemPriority_' + self.id + '::text' ).get( default = 0  ))
		self.comment   =      li.css( '#itemComment_'  + self.id + '::text' ).get( default = '' )
		self.title     =      li.css( '#itemName_'     + self.id + '::text' ).get( default = '' )
		self.by        =      li.css( '#item-byline-'  + self.id + '::text' ).get( default = '' )
		self.is_prime  = bool( li.css( '.a-icon-prime' ));
		self.url       = 'https://' + settings.AMAZON_HOST + rel_url
		self.price     = float( li.attrib['data-price'] )                # "-Infinity" or "123.5" (always US-locale)
		self.buyprice  = settings.WISHLISTS_BUYPRICES[ self.priority ];  # Defaults
		
		# Override default buy-price with specified one:
		# "yadda {BUY $50.23} yadda", "blabla { kaufe ab 21,45 EUR}", "{ab 77} yadda" 
		buyprice_mat = re.match( '{.*?(?P<amount>[0-9,.\']+).*?}', self.comment )
		if buyprice_mat:
			self.buyprice = locale.atof( buyprice_mat.group( 'amount' ))   # Comma vs dot
		
		if used_price_str is not None:
			used_price_mat = re.match( '(?P<amount>[0-9,.\']+)', used_price_str )
			self.price     = locale.atof( used_price_mat.group( 'amount' ))   # Comma vs dot
			self.is_prime  = False;
		
		if self.by:
			# "by John Doe (Paperback)", "von: John Doe, Marie Jane", "in der Hauptrolle Maria C."
			self.by = re.sub( '^von: ',  '', self.by )
			self.by = re.sub( '^by ',    '', self.by )
			self.by = re.sub( '\(.*?\)', '', self.by )
		
		self.price_l10n = locale.currency( self.price )
	


# ----------------------------------------------------------------------------
class Wishlist:
	def __init__( self, response ):
		self.url            = response.url
		self.title          = response.css( '#profile-list-name::text' ).get( default = '' )
		self.products       = []
		self.first_more_url = self.add_response( response )
	
	def __iter__( self ):
		return iter( self.products )
	
	def __len__( self ):
		return len( self.products )
		
	def add_response( self, response ):
		"""Returns URL for next HTML part of successively loaded wishlist (infinite scrolling)"""
		prods = [ Product( li ) for li in response.css( 'li[data-price]' )]
		self.products.extend( prods )
		lek = response.css( 'input[name="lastEvaluatedKey"]::attr(value)' ).get()
		return self.url + '?lek=' + lek if lek else None



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
						'price'    : str( product.price    ),  # US-format and w/o currency for comparison etc
						'priority' : str( product.priority ),
						'buyprice' : str( product.buyprice ),
						'prime'    : str( product.is_prime ),
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
	name       = 'wishlists'
	start_urls = [ settings.WISHLISTS_URL_ANY ]
	
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
	def parse_wl( self, response, wishlist = None ):
		if wishlist:
			more_url = wishlist.add_response( response )
		else:
			wishlist = Wishlist( response )
			more_url = wishlist.first_more_url
			self._lists.append( wishlist )
		
		# Infinite scroll "pagination"
		if more_url:
			yield Request( more_url, callback = self.parse_wl, cb_kwargs = { 'wishlist': wishlist })




