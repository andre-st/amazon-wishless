# Changelog

All notable changes to this project will be documented in this file.


## [1.2.0] - 2019-09-18
### Added

- override default buy-prices by specifying a buy-price directly in a 
  product comment on an Amazon wishlist
  ([#2](https://github.com/andre-st/amazon-wishlist/issues/2))
- the XML-viewer only adds products to the "Latest" section if there was a 
  _significant_ price cut which can be configured in `wishlist.xslt`

### Changed

- the XML-viewer sorts products by priority first (higest to lowest) _and_ price second (lowest to highest), now
- new program dependency `lxml` because the internal XML library (minidom) was replaced


## [1.0.0] - 2019-09-07


