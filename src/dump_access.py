import requests
import sys
import threading
import concurrent.futures
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY


def get_url(year, month):
    """
    Prints and returns URL of Wikipedia page view dumps given year and month.
    Parameters
    ----------
    year : str
        Desired year of page view stats.
    month : str
        Desired month in year of page view stats.
    Returns
    -------
    url : str
    """
    if not isinstance(year, str):
        raise ValueError("Input year as string YYYY.")
    elif len(month) != 2 or not isinstance(month, str):
        raise ValueError("Input month as string MM.")
    else:
        base_url = "https://dumps.wikimedia.org/other/pagecounts-raw/"
        url = base_url + str(year) + "/" + year + "-" + month + "/"
        print(url)
        return url


def get_files(url):
    """
    Parses Wikipedia dump download page for number of files, file names, and file sizes.
    Parameters
    ----------
    url : str
        URL of Wikipedia dump page with desired download links.
    Returns
    -------
    list_elements : list
    list_sizes : list
    """
    r = requests.get(url)
    bs = BeautifulSoup(r.content, "html.parser")
    list_tags = bs.find_all("li")
    sizes = [li.text.split(" ")[-1].replace("M", "") for li in list_tags if "pagecounts" in li.text]
    list_elements = [url + li.a.get("href") for li in list_tags if "pagecounts" in li.text]
    list_sizes = [int(float(x)) for x in sizes]
    return list_elements, list_sizes


def get_info(size_list):
    """
    Prints number of files and total file size to be downloaded.
    Parameters
    ----------
    size_list : list
        List containing integers representing each file size in MB.
    Returns
    -------
    Integer, Integer, String
    """
    sum_size = sum(size_list)
    gb_sum = round(sum_size / 1000, 1)
    num_of_files = len(size_list)

    if gb_sum > 1000:
        return num_of_files, gb_sum/1000, "TB"
    else:
        return num_of_files, gb_sum, "GB"


def fetch_and_download(url, save_path):
    """
    Downloads files prompted from given urls.
    Parameters
    ----------
    url : str
        URL to file download.
    save_path : str
        Path to desired directory for saved files.
    Returns
    -------
    None
    """
    thread_name = threading.currentThread().name
    f_name = url.split("/")[-1]
    file_path = save_path + f_name
    file_path = save_path + f_name
    print(thread_name, "fetch", url)
    r = requests.get(url, stream=True)

    print(f"Downloading {url}")

    with open(file_path, 'wb') as f:
        [f.write(chunk) for chunk in r.iter_content(1000) if chunk]


def use_threading(urls, save_path=dir_path, num_of_threads=None):
    """
    Initiates multi-threading.
    Parameters
    ----------
    urls : list
        List of URLS for file downloads.
    save_path : str
        Path to desired location for downloads.
    num_of_threads : int, optional
    Returns
    -------
    None
    """
    with concurrent.futures.ThreadPoolExecutor(num_of_threads) as pool:
        pool.map(fetch_and_download, urls, save_path)


def main():
    storage = sys.argv[1]
    tree = et.parse('config.xml')
    root = tree.getroot()
    start_year = root[0][0].text
    start_month = root[0][1].text
    end_year = root[1][0].text
    end_month = root[1][1].text

    if int(start_year) > 2015 or int(end_year) > 2015:
        print("Use API for data requests post-2015.")

    date_range = [start_year + '-' + start_month + '-01', end_year + '-' + end_month + '-01']
    start, end = [datetime.strptime(_, "%Y-%m-%d").date() for _ in date_range]

    date_list = [dt for dt in rrule(MONTHLY, dtstart=start, until=end)]
    list_files = []
    list_sizes = []
    for date in date_list:
        url = get_url(str(date.year), f'{date.month:02d}')
        files, sizes = get_files(url)
        list_files.extend(files)
        list_sizes.extend(sizes)

    num_of_files, total_size, unit = get_info(list_sizes)

    while True:
        confirmation = input(f"Total file count: {num_of_files}. Total size: {total_size} {unit}. Proceed? (Y/N): ")
        if confirmation == 'Y':
            use_threading(list_files, storage, root[2][0].text)
        elif confirmation == 'N':
            break
        else:
            print("Please type 'Y' or 'N'.")


if __name__ == '__main__':
    main()

