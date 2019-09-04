# -*- coding: utf-8 -*-

import locale
import scrapy
import os
import re
import settings
from scrapy.http.request import Request
from xml.dom import minidom



# ----------------------------------------------------------------------------
class Product:
	def __init__( self, li ):
    		self.id        = li.attrib['data-itemid']  # is not an ASIN
		used_price_str =      li.css( '.itemUsedAndNewPrice::text'          ).get()    
		rel_url        =      li.css( 'a[id^=itemName]::attr(href)'         ).get( default = '' )
		self.imgurl    =      li.css( 'img::attr(src)'                      ).get()
		self.priority  = int( li.css( '#itemPriority_' + self.id + '::text' ).get( default = 0  ))
		self.comment   =      li.css( '#itemComment_'  + self.id + '::text' ).get( default = '' ).encode( 'utf-8' )
		self.title     =      li.css( '#itemName_'     + self.id + '::text' ).get( default = '' ).encode( 'utf-8' )
		self.url       = 'https://' + settings.AMAZON_HOST + rel_url
		self.price     = float( li.attrib['data-price'] )  # "-Infinity" or "123.5" (always US-locale)
		
		if used_price_str is not None:
			used_price_mat = re.match( '(?P<amount>[0-9,.\']+)', used_price_str )
			self.price     = locale.atof( used_price_mat.group( 'amount' ))   # Comma vs dot
		
		self.price_l10n = locale.currency( self.price )



# ----------------------------------------------------------------------------
class Wishlist:
	def __init__( self, response, filter_maxprice = settings.WISHLISTS_MAXPRICE, filter_minpriority = settings.WISHLISTS_MINPRIORITY ):
		self.url            = response.url
		self.title          = response.css( '#profile-list-name::text' ).get( default = '' ).encode( 'utf-8' )
		self.products       = []
		self.maxprice       = filter_maxprice
		self.minpriority    = filter_minpriority
		self.first_more_url = self.add_response( response )
	
	def __iter__( self ):
		return iter( self.filtered() )
	
	def __len__( self ):
		return len( self.filtered() )
	
	def filtered( self ):
		return [ p for p in self.products if p.price >= 0 and p.price <= self.maxprice and p.priority >= self.minpriority ]
		
	def add_response( self, response ):
		"""Returns URL for next HTML part of successively loaded wishlist (infinite scrolling)"""
		prods = [ Product( li ) for li in response.css( 'li[data-price]' )]
		self.products.extend( prods )
		lek = response.css( 'input[name="lastEvaluatedKey"]::attr(value)' ).get()
		return self.url + '?lek=' + lek if lek else None



# ----------------------------------------------------------------------------
class YourLists:
	def __init__( self, response, excludes = settings.WISHLISTS_EXCLUDES ):
		self.excludes = excludes    
		rel_urls      = response.css( '#your-lists-nav a[href^="/hz/wishlist/ls/"]::attr(href)' ).getall()
		self.urls     = [ 'https://' + settings.AMAZON_HOST + u for u in rel_urls ]
	
	def __iter__( self ):
		return iter( self.filtered() )
	
	def __len__( self ):
		return len( self.filtered() )
	
	def filtered( self ):
		return [ u for u in self.urls if u not in self.excludes ]



# ----------------------------------------------------------------------------
class XmlWishlistReader:
	def __init__( self, filename = settings.WISHLISTS_XMLPATH ):
		self._doc = minidom.parse( filename ) 
	
	def get_product_ids( self ):
		return [ x.attributes['id'].value for x in self._doc.getElementsByTagName( 'product' )]



# ----------------------------------------------------------------------------
class XmlWishlistWriter:
	def __init__( self, filename = settings.WISHLISTS_XMLPATH ):
		self.filename = filename
		self.isfirst  = True
		self._old_ids = []
		if os.path.exists( filename ):
			try:
				self._old_ids = XmlWishlistReader( filename ).get_product_ids()
				self.isfirst = False
			except:
				print( "[WARN] Old {} is corrupt and will be recreated".format( filename ))
	
	def __enter__( self ):
		self._doc = minidom.Document()
		self._doc.appendChild( self._doc.createProcessingInstruction( 'xml-stylesheet', 'type="text/xsl" href="wishlist.xslt"' ))
		self._doc.appendChild( self._doc.createElement( 'amazon' ))
		return self
	
	def __exit__( self, type, value, traceback ):
		f = open( self.filename, 'w' )
		self._doc.writexml( f, indent = "\t", addindent = "\t", newl = "\n" )
		self._doc.unlink()
		f.close()
	
	def write_wl( self, wishlists ):
		for wl in wishlists:
			if len( wl ) == 0: continue
			
			wnode    = self._doc.createElement( 'wishlist' )
			wtitnode = self._doc.createElement( 'title'    )
			wurlnode = self._doc.createElement( 'url'      )
			
			wnode.setAttribute( 'maxprice', str( wl.maxprice ))
			wurlnode.appendChild( self._doc.createTextNode( wl.url   ))
			wtitnode.appendChild( self._doc.createTextNode( wl.title ))
			wnode   .appendChild( wurlnode )
			wnode   .appendChild( wtitnode )
			
			for product in wl:
				pnode = self._doc.createElement( 'product' )
				pnode.setAttribute( 'id',       product.id )
				pnode.setAttribute( 'price',    str( product.price ))
				pnode.setAttribute( 'priority', str( product.priority ))
				
				if not self.isfirst and product.id not in self._old_ids:
					pnode.setAttribute( 'isnew', 'yes' )
				
				urlnode = self._doc.createElement( 'url'      )
				picnode = self._doc.createElement( 'picture'  )
				titnode = self._doc.createElement( 'title'    )
				prcnode = self._doc.createElement( 'price'    )
				cmtnode = self._doc.createElement( 'comment'  )
				urlnode.appendChild( self._doc.createTextNode( product.url        ))
				picnode.appendChild( self._doc.createTextNode( product.imgurl     ))
				titnode.appendChild( self._doc.createTextNode( product.title      ))
				prcnode.appendChild( self._doc.createTextNode( product.price_l10n ))
				cmtnode.appendChild( self._doc.createTextNode( product.comment    ))
				pnode  .appendChild( urlnode )
				pnode  .appendChild( picnode )
				pnode  .appendChild( titnode )
				pnode  .appendChild( prcnode )
				pnode  .appendChild( cmtnode )
				wnode  .appendChild( pnode   )
			
			self._doc.documentElement.appendChild( wnode )



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
	def parse_wl( self, response ):
		if 'wishlist' in response.meta:
			wl       = response.meta['wishlist']
			more_url = wl.add_response( response )
		else:
			wl       = Wishlist( response )
			more_url = wl.first_more_url
			self._lists.append( wl )
		
		# Infinite scroll "pagination"
		if more_url:
			yield Request( more_url, callback = self.parse_wl, meta = { 'wishlist': wl })




