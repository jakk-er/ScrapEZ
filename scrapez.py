# This work is licensed under a Creative Commons Attribution 4.0 International License.
# You must give appropriate credit, provide a link to the license, and indicate if changes were made.
# Details: https://creativecommons.org/licenses/by/4.0/

import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from collections import deque
from banner import display_banner

display_banner()

def scrape_subdomain_links(url, visited_urls):
    queue = deque([url])
    visited_urls.add(url)

    print("\nSubdomains & related links:")

    while queue:
        current_url = queue.popleft()

        try:
            response = requests.get(current_url)
        except requests.exceptions.RequestException as e:
            print(f"\nError accessing {current_url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        for link in soup.find_all('a', href=True):
            link_url = link['href']
            if urllib.parse.urlparse(link_url).netloc != urllib.parse.urlparse(url).netloc and link_url.startswith("http"):
                if link_url not in visited_urls:
                    print(link_url)
                    visited_urls.add(link_url)
                    queue.append(link_url)

        time.sleep(1)  # A 1-second delay between requests

def scrape_pages_links(url, visited_urls, first_call=True):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        if first_call:
            print("\nPages Links:")

        links = []
        for link in soup.find_all('a', href=True):
            link_url = link['href']
            if urllib.parse.urlparse(link_url).netloc == urllib.parse.urlparse(url).netloc:
                if not urllib.parse.urlparse(link_url).netloc:
                    link_url = urllib.parse.urljoin(url, link_url)
                if link_url not in visited_urls:
                    links.append(link_url)
                    print(link_url)
                    visited_urls.add(link_url)

        for link in links:
            time.sleep(1)  # A 1-second delay between requests
            scrape_pages_links(link, visited_urls, first_call=False)

    except requests.exceptions.RequestException as e:
        print(f"\nError accessing {url}: {e}")


def scrape_robots_txt(url):
    robots_url = urllib.parse.urljoin(url, '/robots.txt')
    try:
        robots_response = requests.get(robots_url)
        print("\nRobots.txt:")
        print(robots_response.text)
    except requests.exceptions.RequestException as e:
        print(f"\nError fetching robots.txt: {e}")

def scrape_embedded_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        embedded_links = []
        for tag in soup.find_all(lambda tag: tag.has_attr('src')):
            embedded_link = tag['src']
            embedded_links.append(embedded_link)
            print(f"\nEmbedded link: {embedded_link}")
            
    except requests.exceptions.RequestException as e:
        print(f"\nError accessing {url}: {e}")

def main():
    while True:
        website_url = input("Enter the website URL: ").strip()

        if not website_url:
            print("Please enter a valid URL.")
            continue
        
        if not urllib.parse.urlparse(website_url).scheme:
            website_url = f"https://{website_url}"

        try:
            response = requests.get(website_url)
            if not response.ok:
                raise requests.exceptions.RequestException(f"Received status code {response.status_code}")
            break  # Valid URL, break out of the loop
        except requests.exceptions.RequestException as e:
            print(f"\nError accessing {website_url}: {e}\n\nPlease check the URL and try again.")

    print("Choose which scraping methods to use:")
    print("1. Scrape subdomain links & related links")
    print("2. Scrape pages links")
    print("3. Scrape robots.txt")
    print("4. Scrape embedded links")
    choices = input("Enter your choices (separated by commas): ")

    visited_urls = set()

    if '1' in choices:
        scrape_subdomain_links(website_url, visited_urls)
    if '2' in choices:
        scrape_pages_links(website_url, visited_urls)
    if '3' in choices:
        scrape_robots_txt(website_url)
    if '4' in choices:
        scrape_embedded_links(website_url)


if __name__ == "__main__":
    main()
