<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


<xsl:template match="/amazon">
	<html lang="en">
		<head>
			<meta charset="utf-8" />
			<meta name="viewport" content="width=device-width, initial-scale=1.0" />
			
			<title></title>
			
			<link rel="stylesheet" href="wishlist.css" />
			
		</head>
		<body>
			<h1>Amazon-Lists Used &amp; New</h1>

			<section class="latest">
				<h2>Latest</h2>
				<xsl:apply-templates select="wishlist/product[@isnew]" />
			</section>
			
			
			<section class="higher">
				<h2>Higher Priority</h2>
				<xsl:apply-templates select="wishlist/product[@priority &gt; 0]">
					<xsl:sort select="@priority" data-type="number" order="descending" />
				</xsl:apply-templates>
			</section>

			
			<xsl:apply-templates select="wishlist">
				<xsl:sort select="title" data-type="text" order="ascending" />
			</xsl:apply-templates>
			
		</body>
	</html>
</xsl:template>



<xsl:template match="product">
	<wl-product>
		<xsl:attribute name="data-priority">
			<xsl:value-of select="@priority" />
		</xsl:attribute>
		
		<figure>
			<a target="_blank">
				<xsl:attribute name="href">
					<xsl:value-of select="url" />
				</xsl:attribute>
				
				<img>
					<xsl:attribute name="src">
						<xsl:value-of select="picture" />
					</xsl:attribute>
				</img>
			</a>
		</figure>
		<wl-info>
			<wl-price><xsl:value-of select="price" /></wl-price>
			<wl-title><xsl:value-of select="title" /></wl-title>
		</wl-info>
	</wl-product>
</xsl:template>



<xsl:template match="wishlist">
	<section>
		<h2>
			<a target="_blank">
				<xsl:attribute name="href">
					<xsl:value-of select="url" />
				</xsl:attribute>
				<xsl:value-of select="title" />
			</a>
			&#8804; 
			<xsl:value-of select="@maxprice" />
			EUR</h2>
		
		<xsl:apply-templates select="product">
			<xsl:sort select="@priority" data-type="number" order="descending" />
		</xsl:apply-templates>
		
	</section>
</xsl:template>



</xsl:stylesheet>
