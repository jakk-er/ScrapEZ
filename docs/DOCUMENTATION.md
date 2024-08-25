# ScrapEZ Documentation

**Overview**
-----------
ScrapEZ is a comprehensive web scraping tool designed to extract various types of data from websites. The tool provides multiple scraping methods, including:

- **Scraping Subdomain & Related Links**
- **Scraping Pages Links**
- **Scraping Robots.txt**
- **Scraping Embedded Links**
- **Extracting Metadata**
- **Analyzing Content**
- **Checking Links**
- **Measuring Performance Metrics**
- **Handling Cookies**
- **Parsing Sitemaps**
- **Detecting Language**
- **Getting JavaScript Content**

**How it Works**
---------------
ScrapEZ utilizes several libraries and tools to perform its functions:
- **requests** and **beautifulsoup4** for sending HTTP requests and parsing HTML.
- **playwright**, **selenium**, **webdriver-manager**, and **pyppeteer** for handling JavaScript-heavy websites.
- **langdetect** for detecting the language of the content.

**Scraping Methods**
-------------------

### 1. **Scrape Subdomain Links**
Extracts all subdomain links from the target website. Outputs a list of URLs in the format `subdomain.example.com`.

### 2. **Scrape Pages Links**
Extracts all page links from the target website. Outputs a list of URLs in the format `example.com/page`.

### 3. **Scrape Robots.txt**
Retrieves the contents of the target website's `robots.txt` file.

### 4. **Scrape Embedded Links**
Extracts all embedded links (e.g., images, scripts, stylesheets) from the target website. Outputs a list of URLs in the format `example.com/resource`.

### 5. **Extract Metadata**
Extracts the title and description meta tags from the webpage.

### 6. **Analyze Content**
Analyzes the webpage's content, extracting headers (`h1`, `h2`) and main content paragraphs.

### 7. **Check Links**
Checks for broken links on the webpage.

### 8. **Measure Performance Metrics**
Measures the load time and page size of the webpage.

### 9. **Handle Cookies**
Handles cookies from the target website and returns them.

### 10. **Parse Sitemap**
Parses the sitemap of the website to extract URLs.

### 11. **Detect Language**
Detects the language of the webpage content.

### 12. **Get JavaScript Content**
Retrieves and saves JavaScript-rendered content using Playwright, Selenium, or Pyppeteer.

**Configuration Options**
-------------------------
Currently, there are no additional configuration options. The script can be modified for custom behaviors or additional features.

**Troubleshooting Tips**
-------------------------
### **Common Issues**
* **Timeout Errors**: Increase the timeout or check your internet connection.
* **HTML Parsing Errors**: Update **beautifulsoup4** or verify the website's HTML structure.

### **Debugging**
Use print statements or a debugger like **pdb** for troubleshooting.

**Customization Possibilities**
-----------------------------
Possible modifications include:
* Adding new scraping methods
* Customizing output formats
* Integrating with other tools or services
* Improving performance

**License and Disclaimer**
-------------------------
## License and Disclaimer

ScrapEZ is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/legalcode).

This software is intended for educational purposes only. You agree to use the software solely for educational, research, or academic purposes, and not for any commercial or malicious activities.

You are free to:
- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- **No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

You acknowledge that you are solely responsible for any misuse of the software, including but not limited to using it to target websites or systems without their permission. The authors and copyright holders shall not be liable for any damages or claims arising from such misuse.

**Dependencies**
----------------
ScrapEZ requires the following Python libraries:
- `requests`
- `beautifulsoup4`
- `urllib3`
- `langdetect`
- `playwright`
- `selenium`
- `webdriver-manager`
- `pyppeteer`

**Author**
---------
jakk-er

**Version**
----------
2.0
