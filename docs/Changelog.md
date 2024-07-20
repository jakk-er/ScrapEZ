# This work is licensed under a Creative Commons Attribution 4.0 International License.
# You must give appropriate credit, provide a link to the license, and indicate if changes were made.
# Details: https://creativecommons.org/licenses/by/4.0/

Changelog
==========

All notable changes to this project will be documented in this file.

**Unreleased**
--------------

* No changes yet.

**1.0.1**
--------

* **Fixed Banner Display Issue**: 
  - Resolved an issue where the application banner (`banner.py`) was displaying multiple times upon import or execution. Implemented a solution to ensure the     banner displays only once when the `display_banner()` function is called.
  - Added a boolean flag (`banner_displayed`) to track whether the banner has already been displayed, preventing redundant displays.

**1.0**
--------

* Initial release of ScrapEZ web scraping tool.
* Implemented four scraping methods: scrape subdomain links, scrape pages links, scrape robots.txt, and scrape embedded links.
* Added installation instructions and usage guidelines.
* Licensed under the MIT License.

**Changes planned for future releases**
--------------------------------------

* Improve performance and efficiency of the scraping methods.
* Add support for more advanced scraping techniques.
* Enhance user interface and experience.
* Fix any bugs or issues reported by users.

**Contributing to ScrapEZ**
---------------------------

If you'd like to contribute to ScrapEZ, please fork the repository and submit a pull request. You can also report issues or suggest new features on the GitHub issues page.

**License**
---------

ScrapEZ is licensed under a Creative Commons Attribution 4.0 International License.
