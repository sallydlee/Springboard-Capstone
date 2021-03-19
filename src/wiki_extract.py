import requests
import configparser
import logging
import threading
import concurrent.futures
from bs4 import BeautifulSoup
from pathlib import Path

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[0]}/config.cfg"))


class WikiPageViews:
    def __init__(self, year, month, day):
        self._year = year
        self._month = month
        self._day = day
        self._date = year + month + day
        self._save_path = config.get("BUCKET", "WORKING_ZONE")
        self._page_view_url = config.get("URLS", "PAGE_VIEWS")
        self._num_of_threads = config.get("THREADS", "PAGE_VIEWS")

    def get_url(self):
        """
        Prints and returns URL of Wikipedia page view dumps given year and month.

        Returns
        -------
        url : str
        """
        if not isinstance(self._year, str):
            error_message = "Year needs to be string YYYY. Check config file."
            logger.error(error_message)
            print(error_message)
        elif len(self._month) != 2 or not isinstance(self._month, str):
            error_message = "Month needs to be string MM. Check config file."
            logger.error(error_message)
        else:
            base_url = self._page_view_url
            url = base_url + self._year + "/" + self._year + "-" + self._month + "/"
            return url

    def get_files(self):
        """
        Parses Wikipedia dump download page for number of files, file names, and file sizes.

        Returns
        -------
        list_elements : list
        list_sizes : list
        """
        url = self.get_url()
        logger.debug(f"Parsing {url} for number of files.")
        r = requests.get(url)
        bs = BeautifulSoup(r.content, "html.parser")
        list_tags = bs.find_all("a")
        list_elements = [url + li.get("href") for li in list_tags
                         if "user" in li.get("href") and self._date in li.get("href")]
        logger.debug(f"Number of files to download: {len(list_elements)}")
        return list_elements

    def fetch_and_download(self, url):
        """
        Downloads files prompted from given urls.

        Returns
        -------
        None
        """
        thread_name = threading.currentThread().name
        f_name = url.split("/")[-1]
        file_path = self._save_path + f_name
        logger.debug(thread_name + "fetch" + url)
        r = requests.get(url, stream=True)

        with open(file_path, 'wb') as f:
            [f.write(chunk) for chunk in r.iter_content(1000) if chunk]

    def use_threading(self):
        """
        Initiates multi-threading.

        Returns
        -------
        None
        """
        if self._num_of_threads:
            threads = int(self._num_of_threads)
        else:
            threads = None

        logging.debug(f"Number of threads used: {threads}")
        urls = self.get_files()
        with concurrent.futures.ThreadPoolExecutor(threads) as pool:
            pool.map(self.fetch_and_download, urls)


