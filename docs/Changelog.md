# This work is licensed under a Creative Commons Attribution 4.0 International License.
# You must give appropriate credit, provide a link to the license, and indicate if changes were made.
# Details: https://creativecommons.org/licenses/by/4.0/

Changelog
==========

All notable changes to this project will be documented in this file.

**Unreleased**
--------------

* No changes yet.

**2.0**
--------

* **Enhanced User-Agent Rotation**: 
  - Added support for rotating user-agents to reduce the risk of being blocked by websites.
  - Introduced a `user_agents` list and a function (`get_with_random_user_agent`) to randomize user-agent headers in requests.
  
* **Error Handling and Logging**: 
  - Implemented comprehensive error handling and logging for better tracking of request issues and script errors. Logs are now written to `scraper.log`.
  - Added retry logic with configurable parameters to handle transient request failures more robustly.

* **New Scraping Features**:
  - **Extract Metadata**: Added functionality to extract and display the title and description meta tags from a webpage (`get_metadata` function).
  - **Analyze Content**: Added a feature to analyze and extract headers (`h1`, `h2`) and main content paragraphs (`get_content_analysis` function).
  - **Check Broken Links**: Added a method to check and report broken links found on a page (`check_links` function).
  - **Performance Metrics**: Added performance metrics to measure page load time and page size (`get_performance_metrics` function).
  - **Handle Cookies**: Added functionality to handle and retrieve cookies (`handle_cookies` function).
  - **Parse Sitemap**: Added support to parse and retrieve URLs from the sitemap (`parse_sitemap` function).
  - **Detect Language**: Added language detection using `langdetect` based on the content of the page (`detect` function).
  - **Get JavaScript Content**: Added functionality to retrieve and save the JavaScript-rendered content using Playwright and Selenium (`get_js_content` function).

* **Data Storage**: 
  - Enhanced the `store_data` function to allow saving of a variety of scraped data, including metadata, content analysis, broken links, performance metrics, cookies, and sitemap URLs. Data is saved in a Markdown file.

* **Updated User Interface**:
  - Expanded the menu to include new scraping options.
  - Improved user prompts and input handling for better user experience.

**1.0.1**
--------

* **Fixed Banner Display Issue**: 
  - Resolved an issue where the application banner (`banner.py`) was displaying multiple times upon import or execution. Implemented a solution to ensure the banner displays only once when the `display_banner()` function is called.
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
