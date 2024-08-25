# This work is licensed under a Creative Commons Attribution 4.0 International License.
# You must give appropriate credit, provide a link to the license, and indicate if changes were made.
# Details: https://creativecommons.org/licenses/by/4.0/

import re
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.parse
import time
from collections import deque
import json
import logging
import os
from random import choice
from langdetect import detect
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from banner import display_banner

# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.INFO)

# User-agent rotation
user_agents = [
    # Chrome on Windows 11
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Safari/537.36',

    # Firefox on Windows 11
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0',

    # Safari on macOS Ventura
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Safari/537.36',

    # Edge on Windows 11
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/116.0.1938.76',

    # Chrome on Android 14
    'Mozilla/5.0 (Android 14; Mobile; rv:116.0) Gecko/116.0 Firefox/116.0',

    # Firefox on Android 14
    'Mozilla/5.0 (Android 14; Mobile; rv:118.0) Gecko/118.0 Firefox/118.0',

    # Safari on iOS 17
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',

    # Edge on Android 14
    'Mozilla/5.0 (Android 14; Mobile; rv:116.0) Gecko/116.0 Firefox/116.0',

    # Opera on Windows 11
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Safari/537.36 OPR/102.0.4843.38',

    # Samsung Internet on Android 14
    'Mozilla/5.0 (Android 14; Mobile; Samsung SM-G998B; rv:20.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/20.0 Safari/537.36',

    # Firefox on macOS Ventura
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_0; rv:118.0) Gecko/20100101 Firefox/118.0',

    # Chrome on Linux
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:116.0) Gecko/116.0 Firefox/116.0',
]

def sanitize_filename(url):
    # Replace non-alphanumeric characters with underscores, including colons and slashes.
    sanitized_name = re.sub(r'[\/:*?"<>|]', '_', url)  # Replace characters that are invalid in filenames
    sanitized_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', sanitized_name)  # Replace any remaining non-alphanumeric characters
    return sanitized_name

def get_with_random_user_agent(url):
    headers = {'User-Agent': choice(user_agents)}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None

def retry_request(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = get_with_random_user_agent(url)
            if response:
                return response
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(delay)
    logging.error(f"All {retries} attempts to access {url} failed.")
    return None

def handle_cookies(url):
    session = requests.Session()
    response = retry_request(url)
    if response:
        cookies = session.cookies.get_dict()
        return cookies
    return {}

def scrape_subdomain_links(url, visited_urls):
    queue = deque([url])
    visited_urls.add(url)

    subdomain_links = set()
    while queue:
        current_url = queue.popleft()
        logging.info(f"Scraping subdomains from {current_url}")
        response = retry_request(current_url)
        if not response:
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a', href=True):
            link_url = link['href']
            parsed_link = urllib.parse.urlparse(link_url)
            if parsed_link.netloc != urllib.parse.urlparse(url).netloc and link_url.startswith("http"):
                if link_url not in visited_urls:
                    print(link_url)
                    visited_urls.add(link_url)
                    queue.append(link_url)
        time.sleep(1)
    print("\nSubdomains & related links:")
    for link in subdomain_links:
        print(link)
    
    return list(subdomain_links)

def scrape_pages_links(url, visited_urls, first_call=True):
    logging.info(f"Scraping page links from {url}")
    response = retry_request(url)
    if not response:
        logging.error(f"Failed to retrieve {url}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        link_url = link['href']
        if urllib.parse.urlparse(link_url).netloc == urllib.parse.urlparse(url).netloc:
            if not urllib.parse.urlparse(link_url).netloc:
                link_url = urllib.parse.urljoin(url, link_url)
            if link_url not in visited_urls:
                links.append(link_url)
                visited_urls.add(link_url)
    if first_call:
        print("\nPages Links:")
        for link in links:
            print(link)
            
    for link in links:
        time.sleep(1)
        links.extend(scrape_pages_links(link, visited_urls, first_call=False))
    return links

def scrape_robots_txt(url):
    robots_url = urllib.parse.urljoin(url, '/robots.txt')
    response = retry_request(robots_url)
    robots_txt_content = response.text if response else 'No robots.txt found'

    print("\nRobots.txt:")
    print(robots_txt_content)
    
    return robots_txt_content

def scrape_embedded_links(url):
    response = retry_request(url)
    if not response:
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    embedded_links = []
    for tag in soup.find_all(lambda tag: tag.has_attr('src')):
        embedded_link = tag['src']
        embedded_links.append(embedded_link)

    print("\nEmbedded links:")
    for link in embedded_links:
        print(link)
    
    return embedded_links

def get_metadata(url):
    response = retry_request(url)
    if not response:
        return 'No title', 'No description'
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.title.string if soup.title else 'No title'
    description = soup.find('meta', attrs={'name': 'description'})
    description_content = description['content'] if description else 'No description'

    return title, description_content

def get_content_analysis(url):
    response = retry_request(url)
    if not response:
        return {}, '', [], [], [], [], [], [], [], [], [], [], []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Headers
    headers = {
        'h1': [h1.get_text() for h1 in soup.find_all('h1')],
        'h2': [h2.get_text() for h2 in soup.find_all('h2')],
        'h3': [h3.get_text() for h3 in soup.find_all('h3')],
        'h4': [h4.get_text() for h4 in soup.find_all('h4')],
        'h5': [h5.get_text() for h5 in soup.find_all('h5')],
        'h6': [h6.get_text() for h6 in soup.find_all('h6')]
    }

    # Main Content
    main_content = ' '.join(p.get_text() for p in soup.find_all('p'))

    # Lists
    lists = {
        'ul': [li.get_text() for ul in soup.find_all('ul') for li in ul.find_all('li')],
        'ol': [li.get_text() for ol in soup.find_all('ol') for li in ol.find_all('li')]
    }

    # Blockquotes
    blockquotes = [blockquote.get_text() for blockquote in soup.find_all('blockquote')]

    # Tables
    tables = []
    for table in soup.find_all('table'):
        table_data = {
            'headers': [th.get_text() for th in table.find_all('th')],
            'rows': [[td.get_text() for td in row.find_all('td')] for row in table.find_all('tr')]
        }
        tables.append(table_data)

    # Links
    links = [{'text': a.get_text(), 'url': a.get('href')} for a in soup.find_all('a', href=True)]

    # Images
    images = [{'src': img.get('src'), 'alt': img.get('alt')} for img in soup.find_all('img')]

    # Meta Tags
    meta_tags = {meta.get('name', meta.get('property', 'unknown')): meta.get('content') for meta in soup.find_all('meta')}

    # Scripts
    scripts = [{'src': script.get('src'), 'content': script.string} for script in soup.find_all('script')]

    # Forms
    forms = [{'action': form.get('action'), 'method': form.get('method'), 'inputs': [{'name': input.get('name'), 'type': input.get('type')} for input in form.find_all('input')]} for form in soup.find_all('form')]

    # IFrames
    iframes = [{'src': iframe.get('src')} for iframe in soup.find_all('iframe')]

    # Comments
    comments = [str(comment) for comment in soup.find_all(string=lambda text: isinstance(text, Comment))]

    # Email Addresses
    email_addresses = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', main_content))

    # Phone Numbers
    phone_numbers = set(re.findall(r'\+?\d[\d\s-]{7,}\d', main_content))

    return headers, main_content, lists, blockquotes, tables, links, images, meta_tags, scripts, forms, iframes, comments, email_addresses, phone_numbers

def check_links(url):
    response = retry_request(url)
    if not response:
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    broken_links = []
    for link in links:
        link_response = retry_request(link)
        if link_response and link_response.status_code != 200:
            broken_links.append(link)
        elif not link_response:
            broken_links.append(link)

    return broken_links

def parse_sitemap(url):
    sitemap_url = urllib.parse.urljoin(url, '/sitemap.xml')
    response = retry_request(sitemap_url)
    if not response:
        print(f"Failed to retrieve sitemap from {sitemap_url}")
        return []

    sitemap_urls = []
    try:
        soup = BeautifulSoup(response.content, 'xml')
        for loc in soup.find_all('loc'):
            sitemap_urls.append(loc.get_text())
    except Exception as e:
        logging.error(f"Error parsing sitemap: {e}")
    
    return sitemap_urls

def get_performance_metrics(url):
    start_time = time.time()
    print(f"Fetching URL for performance metrics: {url}")
    response = retry_request(url)
    if not response:
        logging.error(f"Failed to fetch the URL for performance metrics: {url}")
        return {'load_time': 'N/A', 'page_size': 'N/A'}
    
    load_time = time.time() - start_time
    page_size = len(response.content)
    
    print(f"Load Time: {load_time} seconds")
    print(f"Page Size: {page_size} bytes")
    
    return {'load_time': load_time, 'page_size': page_size}

def get_js_content(url, directory):
    content = None
    try:
        # Try to get the JS content using Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector('body')
            content = page.content()
            browser.close()
    except Exception as e:
        logging.error(f"Playwright failed: {e}", exc_info=True)

    if content is None:
        try:
            # Fallback to GeckoDriver if Playwright fails
            options = Options()
            options.add_argument("--headless")

            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.get(url)
            content = driver.page_source
            driver.quit()
        except Exception as e:
            logging.error(f"GeckoDriver failed: {e}", exc_info=True)
            content = "Failed to retrieve content"

    if content:
        # Sanitize the filename for JS content
        filename = sanitize_filename(url) + '-js-content.html'
        filepath = os.path.join(directory, filename)  # Save in the specified directory
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"JavaScript content saved to {filepath}")
        except IOError as e:
            logging.error(f"Failed to write content to file: {e}", exc_info=True)

    return content

def write_section(file, title, content, bullet_points=False):
    """Writes a section to the file."""
    file.write(f"## {title}\n")
    if bullet_points:
        file.write("\n".join(f"- {item}" for item in content) + "\n\n")
    else:
        file.write(f"{content}\n\n")

def store_data(data, directory, file_suffix):
    """Stores scraped data into a markdown file."""
    os.makedirs(directory, exist_ok=True)
    filename = f"scraped_data_{file_suffix}.md"
    filepath = os.path.join(directory, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f"# URL: {data.get('url', 'N/A')}\n\n")
            
            if 'robots_txt' in data:
                write_section(file, "Robots.txt", data['robots_txt'])
                
            if 'subdomain_links' in data:
                write_section(file, "Subdomain Links", data['subdomain_links'], bullet_points=True)
                
            if 'pages_links' in data:
                write_section(file, "Pages Links", data['pages_links'], bullet_points=True)
                
            if 'embedded_links' in data:
                write_section(file, "Embedded Links", data['embedded_links'], bullet_points=True)
                
            if 'metadata' in data:
                metadata = data['metadata']
                file.write(f"## Metadata\n**Title:** {metadata.get('title', 'N/A')}\n**Description:** {metadata.get('description', 'N/A')}\n\n")
                
            if 'broken_links' in data:
                write_section(file, "Broken Links", data['broken_links'], bullet_points=True)
                
            if 'performance_metrics' in data:
                metrics = data['performance_metrics']
                file.write(f"## Performance Metrics\n**Load Time:** {metrics.get('load_time', 'N/A')} seconds\n**Page Size:** {metrics.get('page_size', 'N/A')} bytes\n\n")
                
            if 'cookies' in data:
                cookies = data['cookies']
                write_section(file, "Cookies", [f"{key}: {value}" for key, value in cookies.items()])
                
            if 'sitemap_urls' in data:
                write_section(file, "Sitemap URLs", data['sitemap_urls'], bullet_points=True)
                
            if 'language' in data:
                file.write(f"## Detected Language\n{data['language']}\n\n")
                
            if 'js_content' in data:
                file.write(f"## JavaScript Content\n```\n{data['js_content']}\n```\n\n")
                
        print(f"Data saved to {filepath}.")
        
    except IOError as e:
        logging.error(f"Failed to save data to file: {e}")

def write_content_analysis(file, content_analysis):
    """Writes the content analysis section to the file."""
    file.write(f"## Content Analysis\n")
    
    # Headers
    file.write(f"### Headers\n")
    for header, texts in content_analysis['headers'].items():
        file.write(f"#### {header.upper()}\n" + "\n".join(f"- {text}" for text in texts) + "\n")
    
    # Main Content
    file.write(f"\n### Main Content\n{content_analysis['content']}\n\n")

    # Lists
    file.write(f"### Lists\n")
    for list_type, items in content_analysis['lists'].items():
        file.write(f"#### {list_type.upper()}\n" + "\n".join(f"- {item}" for item in items) + "\n")
    
    # Blockquotes
    file.write(f"\n### Blockquotes\n" + "\n".join(f"- {quote}" for quote in content_analysis['blockquotes']) + "\n")
    
    # Tables
    file.write(f"\n### Tables\n")
    for table in content_analysis['tables']:
        file.write(f"**Headers:** " + ", ".join(table['headers']) + "\n")
        for row in table['rows']:
            file.write(f"**Row:** " + ", ".join(row) + "\n")
    
    # Links
    file.write(f"\n### Links\n")
    for link in content_analysis['links']:
        file.write(f"- **Text:** {link['text']}\n  **URL:** {link['url']}\n")
    
    # Images
    file.write(f"\n### Images\n")
    for img in content_analysis['images']:
        file.write(f"- **SRC:** {img['src']}\n  **ALT:** {img['alt']}\n")
    
    # Meta Tags
    file.write(f"\n### Meta Tags\n")
    for name, content in content_analysis['meta_tags'].items():
        file.write(f"- **{name}:** {content}\n")
    
    # Scripts
    file.write(f"\n### Scripts\n")
    for script in content_analysis['scripts']:
        file.write(f"- **SRC:** {script['src']}\n  **Content:** {script['content']}\n")
    
    # Forms
    file.write(f"\n### Forms\n")
    for form in content_analysis['forms']:
        file.write(f"- **Action:** {form['action']}\n  **Method:** {form['method']}\n  **Inputs:**\n")
        for input in form['inputs']:
            file.write(f"  - **Name:** {input['name']}  **Type:** {input['type']}\n")
    
    # IFrames
    file.write(f"\n### IFrames\n")
    for iframe in content_analysis['iframes']:
        file.write(f"- **SRC:** {iframe['src']}\n")
    
    # Comments
    file.write(f"\n### Comments\n")
    for comment in content_analysis['comments']:
        file.write(f"- {comment}\n")
    
    # Email Addresses
    file.write(f"\n### Email Addresses\n")
    for email in content_analysis['email_addresses']:
        file.write(f"- {email}\n")
    
    # Phone Numbers
    file.write(f"\n### Phone Numbers\n")
    for phone in content_analysis['phone_numbers']:
        file.write(f"- {phone}\n")

def store_analysis(data, directory):
    """Stores content analysis results into a markdown file."""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, 'url_analysis.md')

    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f"# URL: {data.get('url', 'N/A')}\n\n")
            
            if 'content_analysis' in data:
                write_content_analysis(file, data['content_analysis'])
                
        print("Analysis saved to url_analysis.md.")
        
    except IOError as e:
        logging.error(f"Failed to save analysis to file: {e}")

def main():
    # Ensure the "Results" directory exists
    main_directory = 'Results'
    os.makedirs(main_directory, exist_ok=True)

    while True:
        website_url = input("Enter the website URL: ").strip()

        if not website_url:
            print("Please enter a valid URL.")
            continue
        
        if not urllib.parse.urlparse(website_url).scheme:
            website_url = f"https://{website_url}"

        response = retry_request(website_url)
        if response:
            break
        else:
            print(f"\nError accessing {website_url}. Please check the URL and try again.")

    # Create a directory based on the sanitized URL inside the "Results" directory
    directory = os.path.join(main_directory, sanitize_filename(website_url))
    os.makedirs(directory, exist_ok=True)

    print("Choose which scraping methods to use:")
    print("1. Scrape subdomain & related links")
    print("2. Scrape pages links")
    print("3. Scrape robots.txt")
    print("4. Scrape embedded links")
    print("5. Extract metadata")
    print("6. Analyze content")
    print("7. Check links")
    print("8. Performance metrics")
    print("9. Handle cookies")
    print("10. Parse sitemap")
    print("11. Detect language")
    print("12. Get JS content")
    choices = input("Enter your choices (separated by commas): ").strip()

    choices = [choice.strip() for choice in choices.split(',')]
    visited_urls = set()
    data = {'url': website_url}

    # Collect data based on user choices
    if '1' in choices:
        data['subdomain_links'] = scrape_subdomain_links(website_url, visited_urls)
        store_data({'url': website_url, 'subdomain_links': data['subdomain_links']}, directory, 'subdomain_links')

    if '2' in choices:
        data['pages_links'] = scrape_pages_links(website_url, visited_urls, first_call=True)
        store_data({'url': website_url, 'pages_links': data['pages_links']}, directory, 'pages_links')

    if '3' in choices:
        data['robots_txt'] = scrape_robots_txt(website_url)
        store_data({'url': website_url, 'robots_txt': data['robots_txt']}, directory, 'robots_txt')

    if '4' in choices:
        data['embedded_links'] = scrape_embedded_links(website_url)
        store_data({'url': website_url, 'embedded_links': data['embedded_links']}, directory, 'embedded_links')

    if '5' in choices:
        title, description = get_metadata(website_url)
        data['metadata'] = {'title': title, 'description': description}
        store_data({'url': website_url, 'metadata': data['metadata']}, directory, 'metadata')

    if '6' in choices:
        (headers, content, lists, blockquotes, tables, links, images, meta_tags, scripts, forms,
         iframes, comments, email_addresses, phone_numbers) = get_content_analysis(website_url)
        data['content_analysis'] = {
            'headers': headers,
            'content': content,
            'lists': lists,
            'blockquotes': blockquotes,
            'tables': tables,
            'links': links,
            'images': images,
            'meta_tags': meta_tags,
            'scripts': scripts,
            'forms': forms,
            'iframes': iframes,
            'comments': comments,
            'email_addresses': email_addresses,
            'phone_numbers': phone_numbers
        }
        store_analysis(data, directory)

    if '7' in choices:
        data['broken_links'] = check_links(website_url)
        store_data({'url': website_url, 'broken_links': data['broken_links']}, directory, 'broken_links')

    if '8' in choices:
        data['performance_metrics'] = get_performance_metrics(website_url)
        store_data({'url': website_url, 'performance_metrics': data['performance_metrics']}, directory, 'performance_metrics')

    if '9' in choices:
        data['cookies'] = handle_cookies(website_url)
        store_data({'url': website_url, 'cookies': data['cookies']}, directory, 'cookies')

    if '10' in choices:
        data['sitemap_urls'] = parse_sitemap(website_url)
        store_data({'url': website_url, 'sitemap_urls': data['sitemap_urls']}, directory, 'sitemap_urls')

    if '11' in choices:
        content = retry_request(website_url).text
        data['language'] = detect(content)
        store_data({'url': website_url, 'language': data['language']}, directory, 'language')

    if '12' in choices:
        js_content = get_js_content(website_url, directory)
        if js_content:
            data['js_content'] = js_content
        store_data({'url': website_url, 'js_content': data['js_content']}, directory, 'js_content')

if __name__ == "__main__":
    display_banner()
    main()
