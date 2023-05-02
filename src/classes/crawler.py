import re
import random
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode


class Crawler():
    def __init__(self, s3_connection):
        self.S3 = s3_connection

    def sanitize(self, text):
        text = text.lower()    
        # Remove any non-word characters from text
        text = re.sub(r'\W+', ' ', text)
        # remove all single characters
        text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)
        
        #Normalize
        text = unidecode(text)
        list_text = text.split()
        text = ' '.join([word for word in list_text if word.isalpha()])
        return text

    def is_link_to_file(self, link: str):
        extensions = [
            ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".txt",
            ".html", ".htm", ".css", ".js", ".xml", ".json", ".csv", ".tsv",
            ".zip", ".tar", ".gz", ".rar", ".7z", ".bz2", ".apk", ".exe",
            ".bmp", ".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".svg",
            ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".mp4", ".avi",
            ".mkv", ".mov", ".wmv", ".flv", ".webm", ".srt", ".sub", ".ass",
            ".pdf", ".epub", ".mobi", ".azw", ".azw3", ".djvu", ".fb2", ".ibook"
        ]
        return any(ext in link for ext in extensions)
        
    def filter_link(self, link: str):
        if not link:
            return None
        
        if not (link.startswith('http://') or link.startswith('https://')):
            return None
        
        filter_list = ['facebook', 'twitter', 'youtube', 'instagram', 'linkedin', 'github']
        if (any(site in link for site in filter_list)):
            return None
        
        if self.is_link_to_file(link):
            return None
        
        return link


    def get_external_links(self, url):
        url = self.filter_link(url)
        if not url:
            return '', set([])
        
        # Send a GET request to the URL
        try:
            response = requests.get(url)
        except Exception as err:
            print(f'Failed to send request to: {url}.\nError: {err}')
            return '', set([])

        # Parse the HTML content of the response with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <a> tags with an href attribute that starts with 'http' or 'https'
        external_links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            filtered_link = self.filter_link(link=href)
            if filtered_link:
                external_links.append(filtered_link)

        all_text = soup.get_text(strip=True, separator=' ')
        all_text = self.sanitize(all_text)
        # Return the list of external links
        return all_text, set(external_links)


    def crawl(self, url: str):
        # First website to crawl
        all_text, links = self.get_external_links(url)
        destination_fpath = f"html_content/{url.replace('https://', '').replace('http://', '').strip('/')}.txt"
        self.S3.save_html(content=all_text, fpath=destination_fpath)
        
        unique_links = list(set(links))
        if len(unique_links) < 1:
            print('Did not find links to crawl')
            return 
        
        self.crawl_children(urls=unique_links, n_sites=5, depth=2)
        return
        
    def crawl_children(self, urls: list[str], n_sites: int, depth: int):
        # Crawl N children websites until depth == 0
        if depth == 0:
            return 
        
        try:
            urls = random.sample(urls, n_sites) 
        except:
            pass
        
        print(f'Urls to download: {urls}')
        for idx,url in enumerate(urls):
            print('\nIdx: ', idx)
            all_text, links = self.get_external_links(url)
            destination_fpath = f"html_content/{url.replace('https://', '').replace('http://', '').strip('/')}.txt"
            self.S3.save_html(content=all_text, fpath=destination_fpath)
            print('\n')
            unique_links = list(set(links))
            #pprint(unique_links)
            print(f'Save content at: {destination_fpath}')
            self.crawl_children(urls=unique_links, n_sites=5, depth=depth-1)