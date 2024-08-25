# This work is licensed under a Creative Commons Attribution 4.0 International License.
# You must give appropriate credit, provide a link to the license, and indicate if changes were made.
# Details: https://creativecommons.org/licenses/by/4.0/

import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from collections import deque
import json
import logging
from random import choice
from langdetect import detect
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from pyppeteer import launch
from banner import display_banner

# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.INFO)

# User-agent rotation
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    # Add more user-agent strings here
]

def sanitize_filename(url):
    # Replace non-alphanumeric characters with underscores
    return re.sub(r'[^a-zA-Z0-9]', '_', url) + '-js-content.json'

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
        return {}, ''

    soup = BeautifulSoup(response.content, 'html.parser')
    headers = {
        'h1': [h1.get_text() for h1 in soup.find_all('h1')],
        'h2': [h2.get_text() for h2 in soup.find_all('h2')]
    }
    main_content = ' '.join(p.get_text() for p in soup.find_all('p'))

    return headers, main_content

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
        return None, None
    
    load_time = time.time() - start_time
    page_size = len(response.content)
    
    print(f"Load Time: {load_time} seconds")
    print(f"Page Size: {page_size} bytes")
    
    return load_time, page_size

def get_js_content(url):
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
        logging.error(f"Playwright failed: {e}")

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
            logging.error(f"GeckoDriver failed: {e}")
            content = "Failed to retrieve content"

    if content:
        filename = sanitize_filename(url).replace('-js-content.json', '.html')
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"JavaScript content saved to {filename}")
        except IOError as e:
            logging.error(f"Failed to write content to file: {e}")

    return content

def store_data(data):
    choice = input("Do you want to save this scraped data into a file? (yes/no or y/n): ").strip().lower()
    if choice in ['yes', 'y']:
        while True:
            filename = input("Enter filename to save data (without extension): ").strip()
            if not filename:
                filename = 'data'
            filename = f"{filename}.md"  # Append .md extension
            if re.match(r'^[\w\-. ]+$', filename):
                break
            else:
                print("Invalid filename. Please enter a valid filename.")
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(f"# URL: {data.get('url', 'N/A')}\n\n")
                if 'robots_txt' in data:
                    file.write(f"## Robots.txt\n```\n{data['robots_txt']}\n```\n\n")
                if 'subdomain_links' in data:
                    file.write(f"## Subdomain Links\n" + "\n".join(f"- {link}" for link in data['subdomain_links']) + "\n\n")
                if 'pages_links' in data:
                    file.write(f"## Pages Links\n" + "\n".join(f"- {link}" for link in data['pages_links']) + "\n\n")
                if 'embedded_links' in data:
                    file.write(f"## Embedded Links\n" + "\n".join(f"- {link}" for link in data['embedded_links']) + "\n\n")
                if 'metadata' in data:
                    metadata = data['metadata']
                    file.write(f"## Metadata\n**Title:** {metadata.get('title', 'N/A')}\n**Description:** {metadata.get('description', 'N/A')}\n\n")
                if 'content_analysis' in data:
                    content_analysis = data['content_analysis']
                    file.write(f"## Content Analysis\n### Headers\n")
                    for header, texts in content_analysis['headers'].items():
                        file.write(f"#### {header.upper()}\n" + "\n".join(f"- {text}" for text in texts) + "\n")
                    file.write(f"\n### Main Content\n{content_analysis['content']}\n\n")
                if 'broken_links' in data:
                    file.write(f"## Broken Links\n" + "\n".join(f"- {link}" for link in data['broken_links']) + "\n\n")
                if 'performance_metrics' in data:
                    performance_metrics = data['performance_metrics']
                    file.write(f"## Performance Metrics\n**Load Time:** {performance_metrics.get('load_time', 'N/A')} seconds\n**Page Size:** {performance_metrics.get('page_size', 'N/A')} bytes\n\n")
                if 'cookies' in data:
                    file.write(f"## Cookies\n" + "\n".join(f"- {key}: {value}" for key, value in data['cookies'].items()) + "\n\n")
                if 'sitemap_urls' in data:
                    file.write(f"## Sitemap URLs\n" + "\n".join(f"- {url}" for url in data['sitemap_urls']) + "\n\n")
                if 'language' in data:
                    file.write(f"## Detected Language\n{data['language']}\n\n")
            print(f"Data saved to {filename}.")
        except IOError as e:
            logging.error(f"Failed to save data to file: {e}")
    elif choice in ['no', 'n']:
        print("Data not saved.")
    else:
        print("Invalid choice. Please enter 'yes', 'y', 'no', or 'n'.")

def main():
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

    if '1' in choices:
        data['subdomain_links'] = scrape_subdomain_links(website_url, visited_urls)

    if '2' in choices:
        data['pages_links'] = scrape_pages_links(website_url, visited_urls, first_call=True)

    if '3' in choices:
        data['robots_txt'] = scrape_robots_txt(website_url)

    if '4' in choices:
        data['embedded_links'] = scrape_embedded_links(website_url)

    if '5' in choices:
        title, description = get_metadata(website_url)
        data['metadata'] = {'title': title, 'description': description}

    if '6' in choices:
        headers, content = get_content_analysis(website_url)
        data['content_analysis'] = {'headers': headers, 'content': content}

    if '7' in choices:
        broken_links = check_links(website_url)
        data['broken_links'] = broken_links

    if '8' in choices:
        load_time, page_size = get_performance_metrics(website_url)
        data['performance_metrics'] = {'load_time': load_time, 'page_size': page_size}

    if '9' in choices:
        cookies = handle_cookies(website_url)
        data['cookies'] = cookies

    if '10' in choices:
        sitemap_urls = parse_sitemap(website_url)
        data['sitemap_urls'] = sitemap_urls

    if '11' in choices:
        content = retry_request(website_url).text
        language = detect(content)
        data['language'] = language

    if '12' in choices:
        get_js_content(website_url)  # Save JS content to file

    # Always ask to store data after processing all options
    store_data(data)

if __name__ == "__main__":
    display_banner()
    main()
