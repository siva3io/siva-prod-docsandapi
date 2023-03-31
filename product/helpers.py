import os
from urllib.parse import urljoin
from selectorlib import Formatter, Extractor
import requests
import json
from .custom_formatters import PriceFormatter, HTMLFormatter
from bs4 import SoupStrainer, BeautifulSoup


formatters = Formatter.get_all()
# Create an Extractor by reading from the YAML file
dir_path = os.path.dirname(os.path.realpath(__file__))
# data_dir_path = os.path.join(dir_path, '../product_data')
e = Extractor.from_yaml_file(os.path.join(dir_path, 'selectors.yml'), formatters=formatters)
headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.in/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }


def error_handler(func):
    def inner(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            return response
        except Exception as e:
            print("Exception while processing!\n", e.__str__())
    return inner


def scrape(url):

    # Download the page using requests
    print("Downloading %s" % url)
    r = requests.get(url, headers=headers)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d" % (url, r.status_code))
        return None
    # Pass the HTML of the page and create
    selectorlib_output = e.extract(r.text)
    # breakpoint()
    return selectorlib_output



@error_handler
def scrape_and_save(link):
    data = scrape(link)
    if data:
        yield data
        # json_data = json.dumps(data, indent=4, ensure_ascii=True)
        # file.write(json_data)
        # file.write("\n")


# with open("urls.txt", 'r') as url_list, open('output.jsonl', 'w') as outfile:
def scrape_url(url: list):
    processed_urls = []
    links = [*url]
    while len(links) != 0:
        link = links.pop()
        # print(links)
        if "/dp/" in link and link not in processed_urls:
            # scrape_and_save(link)
            data = scrape(link)
            processed_urls.append(link)
            yield data
        else:
            r = requests.get(link, headers=headers)
            if r.status_code > 500:
                print("Some error in the url or is blocked by Amazon")
            soup = BeautifulSoup(r.text, features="html.parser")
            # container = soup.find('div', attrs={"class": "a-container"})
            # if container is None:
            #     continue
            a_tags = soup.findAll("a")
            for a_tag in a_tags:
                if a_tag.has_attr("href"):
                    href = a_tag["href"]
                    # if a_tag.string is not None and "See" in a_tag.string:
                    #     print(a_tag.string)
                    if href is not None:
                        if "/dp/" in href:
                            href = href.split("?")[0]
                            href = href.split("/ref=")[0]
                        elif "/s/" in href or "/category/" in href:
                            print(href)
                            print("The title is ", a_tag.string)
                        else:
                            continue
                        if href.startswith("/"):
                            href = urljoin("https://www.amazon.in", href)
                        if href in processed_urls or href in links:
                            # print("Already processed the url", href)
                            continue
                        links.append(href)
                        print("Number of links to be processed is", len(links))