<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


<!-- ======================= EDIT YOUR FILTER SETTINGS =================== -->

<!-- Specify what you consider a significant price *change*.
     Products with a significantly reduced price are listed separately (CHEAP_PRICE).
     Default: 2.00 -->
<xsl:variable name="SIGNIFICANT_PRICE_CUT" select="2.00" />

<!-- Specify what you consider a low book price, e.g., 
     less than 2 euro for a book -->
<xsl:variable name="CHEAP_PRICE">2.00</xsl:variable>

<xsl:variable name="CURRENCY">EUR </xsl:variable>




<!-- ===================================================================== -->



<xsl:template match="/amazon">
	<html lang="en">
		<head>
			<meta charset="utf-8" />
			<meta name="viewport" content="width=device-width, initial-scale=1.0" />
			
			<title>Amazon-Lists Used &amp; New</title>
			
			<link rel="stylesheet" href="wishlist.css" />
			
		</head>
		<body>
			<h1>Amazon-Lists Used &amp; New</h1>
			
			<a class="credits" href="https://github.com/andre-st/amazon-wishlist" target="_blank">GitHub</a>
			
			<section class="smartlist latest">
				<h2>Latest price-cut</h2>
				<xsl:apply-templates select="wishlist/product[@price &gt;= 0 and @price &lt;= @buyprice and @pricecut &gt;= $SIGNIFICANT_PRICE_CUT]">
					<xsl:sort select="@priority" data-type="number" order="descending" />
					<xsl:sort select="@price"    data-type="number" order="ascending" />
				</xsl:apply-templates>
			</section>
			
			<section class="smartlist higher">
				<h2>Higher priority</h2>
				<xsl:apply-templates select="wishlist/product[@price &gt;= 0 and @price &lt;= @buyprice and @priority &gt; 0]">
					<xsl:sort select="@priority" data-type="number" order="descending" />
					<xsl:sort select="@price"    data-type="number" order="ascending" />
				</xsl:apply-templates>
			</section>

			<section class="smartlist cheap">
				<h2>
					Products &#8804;
					<xsl:value-of select="$CURRENCY" />
					<xsl:value-of select="$CHEAP_PRICE" />
				</h2>
				<xsl:apply-templates select="wishlist/product[@price &gt;= 0 and @price &lt;= $CHEAP_PRICE and @priority &gt;= 0]">
					<xsl:sort select="@priority" data-type="number" order="descending" />
					<xsl:sort select="@price"    data-type="number" order="ascending" />
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
		<xsl:attribute name="class">
			<xsl:if test="@prime='True'">prime</xsl:if>
		</xsl:attribute>
		
		<xsl:attribute name="data-priority">
			<xsl:value-of select="@priority" />
		</xsl:attribute>
		

		
		<figure>
			<a target="_blank" class="product-link">
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
			<xsl:if test="by">
				<wl-by><xsl:value-of select="by" /></wl-by>
			</xsl:if>
			
			<a target="_blank" class="list-link">
				<xsl:attribute name="href"><xsl:value-of select="../url" />?sort=priority</xsl:attribute>
				visit list
			</a>
		</wl-info>
	</wl-product>
</xsl:template>



<xsl:template match="wishlist">
	<section class="wishlist">
		<h2>
			<a target="_blank">
				<xsl:attribute name="href">
					<xsl:value-of select="url" />?sort=priority
				</xsl:attribute>
				<xsl:value-of select="title" />
			</a>
			(&#8364;<xsl:value-of select="$CHEAP_PRICE" />&#8210;10.00)</h2> <!-- TODO: Max(@buyprice) only in Firefox-unsupported XSLT2 -->
		
		<xsl:apply-templates select="product[@price &gt; $CHEAP_PRICE and @price &lt;= @buyprice]">
			<xsl:sort select="@priority" data-type="number" order="descending" />
			<xsl:sort select="@price"    data-type="number" order="ascending" />
		</xsl:apply-templates>
		
	</section>
</xsl:template>



</xsl:stylesheet>
