# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

Version number 1.MINOR.PATCH, increments:
- MINOR version when functionality was added, removed, changed
- PATCH version when bug fixes were added


## [Unreleased]

- see [GitHub issues labeled "Soon"](https://github.com/andre-st/amazon-wishless/issues?q=is%3Aopen+is%3Aissue+label%3Asoon)



## [v1.4.3] - 2020-03-26
### Fixed
- `ValueError: invalid literal for int() with base 10: 'MEDIUM'`:
  Amazon encodes priorities either with literals ('MEDIUM', 'LOWEST' etc) now or numbers (0, -2 etc).

### Changed
- Amazon doesn't display alternative price offerings on its wishlists anymore.
  At least in the source code there's an alternative price for items not offered by Amazon.
  Unfortunately, this situation reduces the value of this project.



## [v1.4.1] - 2019-11-21
### Added
- Download-delay setting to handle 503 Service Unavailable from Amazon

### Fixed

- Scrapy settings in settings.py were ignored



## [v1.4.0] - 2019-10-31
### Added

- XML viewer indicates _free shipping_ option



## [v1.3.0] - 2019-10-04
### Added

- new XML-viewer section with products <= n EUR, you can confgure 'n' in the XSLT file

### Changed

- allows non-exact URls for wishlist exclusion in settings.py, it's sufficient if an url _starts with_ the given strings



## [v1.2.0] - 2019-09-18
### Added

- override default buy-prices by specifying a buy-price directly in a 
  product comment on an Amazon wishlist
  ([#2](https://github.com/andre-st/amazon-wishlist/issues/2))
- the XML-viewer only adds products to the "Latest" section if there was a 
  _significant_ price cut which can be configured in `wishlist.xslt`

### Changed

- the XML-viewer sorts products by priority first (highest to lowest) _and_ price second (lowest to highest), now
- new program dependency: `lxml` replaces the minidom library for internal XML operations



## [v1.0.0] - 2019-09-07


