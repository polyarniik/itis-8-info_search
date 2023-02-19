import os
import shutil
import urllib.parse
from pathlib import Path
from typing import NoReturn

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry


class HabrArticalsCrowler:
    URL = "https://habr.com/"
    INDEX_FILE = Path(__file__).resolve().parent.joinpath("index.txt")

    def get_articles(self, count: int = 1) -> NoReturn:
        links = []
        n = 1
        while len(links) < count:
            page = self.get_page_content(urllib.parse.urljoin(self.URL, f"ru/all/page{n}"))
            links.extend(self.get_articles_link_from_page(page))
            n += 1

        self.save_articles_content(links[:count])

    def get_page_content(self, page_url) -> str:
        session = requests.Session()
        session.mount(
            "https://",
            HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])),
        )
        response = session.get(page_url)
        return response.text

    def get_articles_link_from_page(self, page_content):
        soup = BeautifulSoup(page_content, features="html.parser")
        links = []
        for link in soup.find_all("a", {"class": "tm-article-snippet__title-link"}, href=True):
            links.append(link["href"])
        return links

    def remove_tags(self, page_content, tags: list = ["style", "link", "script", "noscript"]):
        soup = BeautifulSoup(page_content, features="html.parser")
        for tag in soup.find_all(tags):
            tag.extract()

        return str(soup)

    def save_articles_content(self, links):
        number_len = len(str(len(links)))
        index_file_content = ""
        folder_path = Path(__file__).resolve().parent.joinpath("files/")
        shutil.rmtree(folder_path)
        for num, link in enumerate(links, 1):
            file_name = f"{str(num).zfill(number_len)}.txt"
            path = folder_path.joinpath(file_name)
            url = urllib.parse.urljoin(self.URL, link)
            index_file_content += f"{num}. {file_name} {url}\n"
            os.makedirs(folder_path, exist_ok=True)
            with open(path, "w") as file:
                file.write(self.remove_tags(self.get_page_content(url)))

        with open(self.INDEX_FILE, "w") as file:
            file.write(index_file_content)


if __name__ == "__main__":
    HabrArticalsCrowler().get_articles(100)
