# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [Unreleased]

## [1.2.0] - 2019-09-18
### Added

- override default buy-prices by specifying a buy-price directly in a 
  product comment on an Amazon wishlist
  ([#2](https://github.com/andre-st/amazon-wishlist/issues/2))
- the XML-viewer only adds products to the "Latest" section if there was a 
  _significant_ price cut which can be configured in `wishlist.xslt`

### Changed

- the XML-viewer sorts products by priority first (highest to lowest) _and_ price second (lowest to highest), now
- new program dependency: `lxml` replaces the minidom library for internal XML operations


## [1.0.0] - 2019-09-07


