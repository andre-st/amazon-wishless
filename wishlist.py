# -*- coding: utf-8 -*-

# Standard:
import locale
import scrapy
import os
import re
import logging

# Third party:
from scrapy.http.request import Request
from lxml import etree as XML

# Ours:
import settings


# ----------------------------------------------------------------------------
def is_captcha( response ):
	return response.css( '#captchacharacters' )


def listid_from_url( url ):
	# wishlist/genericItemsPage/XXXXXXXXXXXXX
	# wishlist/ls/XXXXXXXXXXXXXX
	# lid=XXXXXXXXXXXXX
	mat = re.match( '.*?(wishlist/genericItemsPage/|wishlist/ls/|lid=)(?P<id>[a-zA-Z0-9]+).*', url )
	return mat.group( 'id' ) if mat else None


def log_page_error( name, response, logger ):
	reason = "*** CAPTCHA bot block ***" if is_captcha( response ) else "Reason unknown"
	logger.error( " Failed loading {}: {} ({})".format( name, reason, response.url ))



# ----------------------------------------------------------------------------
class Product:
	def __init__( self, li ):
		self.id        = li.attrib['data-itemid']  # is not an ASIN
		used_price_str = li.css( '.itemUsedAndNewPrice::text'  ).get( None         )
		rel_url        = li.css( 'a[id^=itemName]::attr(href)' ).get( default = '' ).strip()
		self.imgurl    = li.css( 'img::attr(src)'              ).get( default = '' ).strip()
		
		# Since 2020-03-19 priorities are either literals ('MEDIUM') -OR- numeric (0),
		# We need them as numbers in order to sort items etc.
		# TODO: Probably more reliable to check classes rather than (internal) values
		prioNumOrLit = li.css( '#itemPriority_' + self.id + '::text' ).get( default = 'MEDIUM' ).strip();
		try:  # str() has no isnumeric() in Python 2, unicode() isnumeric can't negative values; this is rly recommended, sigh:
			self.priority = int( prioNumOrLit )
		except:
			self.priority = { 'LOWEST' : -2,'LOW' : -1, 'MEDIUM' : 0, 'HIGH' : 1, 'HIGHEST' : 2 }[ prioNumOrLit ]
		
		self.comment   = li.css( '#itemComment_' + self.id + '::text' ).get( default = '' ).strip()
		self.title     = li.css( '#itemName_'    + self.id + '::text' ).get( default = '' ).strip()
		self.by        = li.css( '#item-byline-' + self.id + '::text' ).get( default = '' ).strip()
		self.is_prime  = bool( li.css( '.a-icon-prime' ));
		self.url       = settings.AMAZON_BASEURL + rel_url
		
		# Amazon doesn't display alternative price offerings anymore since 2020-03-23.
		# At least the lowest price for products not available from Amazon is still 
		# present in the page source code:
		self.price     = float( li.attrib['data-price'] )                # "-Infinity" or "123.5" (always US-locale)
		self.buyprice  = settings.WISHLISTS_BUYPRICES[ self.priority ]   # Defaults
		
		# Override default buy-price with specified one:
		# "yadda {BUY $50.23} yadda", "blabla { kaufe ab 21,45 EUR}", "{ab 77} yadda" 
		buyprice_mat = re.search( '.*?{.*?(?P<amount>[0-9,.\']+).*?}.*', self.comment )  # multiline as opposed to re.match()
		if buyprice_mat:
			self.buyprice = locale.atof( buyprice_mat.group( 'amount' ))   # Comma vs dot
		
		if used_price_str is not None:
			self.is_prime  = False;
			used_price_mat = re.search( '.*?(?P<amount>[0-9,.\']+).*', used_price_str )   # mulitline as opposed to re.match()
			if used_price_mat:
				self.price = locale.atof( used_price_mat.group( 'amount' ))   # Comma vs dot
		
		if self.by:
			# "by John Doe (Paperback)", "von: John Doe, Marie Jane", "in der Hauptrolle Maria C."
			self.by = re.sub( '^von: ',  '', self.by )
			self.by = re.sub( '^by ',    '', self.by )
			self.by = re.sub( '\(.*?\)', '', self.by )
		
		self.price_l10n = locale.currency( self.price )


# ----------------------------------------------------------------------------
class Wishlist:
	def __init__( self, response ):
		self.logger   = logging.getLogger( __name__ )
		self.url      = response.url
		self.id       = response.css( '#listId::attr(value)' ).get( default = '' ).strip()
		self.products = []
		if self.id:
			self.title          = response.css( '#profile-list-name::text' ).get( default = '' ).strip()
			self.first_more_url = self.add_response( response )
		else:
			self.title          = '[Error title for ' + self.url + ']'
			self.first_more_url = None;
			log_page_error( 'wishlist', response, self.logger )
	
	def __iter__( self ):
		return iter( self.products )
	
	def __len__( self ):
		return len( self.products )
	
	def __str__( self ):
		return "Wishlist '{}' ({} items, atm)".format( self.title.encode( 'ascii', 'ignore' ), len( self ))
	
	def add_response( self, response ):
		"""Returns URL for next HTML part of successively loaded wishlist (infinite scrolling)"""
		prods = [ Product( li ) for li in response.css( 'li[data-price]' )]
		self.products.extend( prods )
		self.logger.debug( self )
		
		# Last showMoreUrl of the last page just gets us the first 10 items again
		# lastEvaluatedKey, however, is empty, therefore we use this as exit condition
		#
		next_rel_url = response.xpath( "(//input[@name='showMoreUrl'])[last()]/@value"      ).get()
		lek          = response.xpath( "(//input[@name='lastEvaluatedKey'])[last()]/@value" ).get()
		
		return settings.AMAZON_BASEURL + next_rel_url if lek and next_rel_url else None



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
	def __init__( self, filename = settings.WISHLISTS_XMLPATH, xsl_outfname = settings.WISHLISTS_XSLOUTPATH ):
		self.filename     = filename
		self.xsl_outfname = xsl_outfname
		self._old         = None
		if os.path.exists( filename ):
			try:
				self._old = XmlWishlistReader( filename )
			except:
				print( "[WARN] Old {} is corrupt and will be recreated".format( filename ))
	
	def __enter__( self ):
		self._xml = XML.ElementTree( XML.Element( 'amazon' ))
		return self
	
	def __exit__( self, type, value, traceback ):
		self._xml.write( self.filename, xml_declaration = True, pretty_print = True )  # Always required to id changes
		if self.xsl_outfname:
			base, ext = os.path.splitext( self.xsl_outfname )
			xsl_path  = base + '.xslt'  # Dynamic name eases customization
			xsl       = XML.parse( xsl_path )
			tran      = XML.XSLT( xsl )
			xnew      = tran( self._xml )
			xnew.write( self.xsl_outfname, xml_declaration = True, pretty_print = True )
	
	def write_wl( self, wishlists ):
		for wl in wishlists:
			if len( wl ) > 0:
				wl_elem = XML.SubElement( self._xml.getroot(), 'wishlist', { 'id' : wl.id })
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
	name            = 'wishlists'
	start_urls      = [ wl[0] for wl in settings.WISHLISTS ]
	custom_settings = settings.SCRAPY_SETTINGS
	
	# My:
	_lists = []
	
	# Spider:
	def closed( self, reason ):
		if any( self._lists ):  # All lists empty => Scraping or config error
			with XmlWishlistWriter() as w:
				w.write_wl( self._lists )
	
	# My:
	def parse( self, response, wishlist = None ):
		if wishlist:
			more_url = wishlist.add_response( response )
		else:
			wishlist = Wishlist( response )
			more_url = wishlist.first_more_url
			self._lists.append( wishlist )
		
		# Infinite scroll "pagination"
		if more_url:
			yield Request( more_url, callback = self.parse, cb_kwargs = { 'wishlist': wishlist })




