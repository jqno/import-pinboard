import datetime
import json
from dateutil.parser import parse
import requests
from bs4 import BeautifulSoup

FOLDER = "/Users/jqno/Desktop/pinboard"


def process():
    bookmarks = determine_bookmarks()
    twitter_favs = determine_twitter_favs()
    filtered_bookmarks = filter_bookmarks(bookmarks, twitter_favs)
    pinged_bookmarks = ping_bookmarks(filtered_bookmarks)
    grouped_bookmarks = group_bookmarks(pinged_bookmarks)
    write_files(grouped_bookmarks)


def determine_bookmarks():
    in_file_name = f"{FOLDER}/pinboard_export.json"
    with open(in_file_name, "r") as in_file:
        return json.load(in_file)


def determine_twitter_favs():
    result = []
    for i in [1, 2, 3]:
        file_name = f"{FOLDER}/from-twitter-favs-{i}.html"
        with open(file_name, "r") as in_file:
            html = BeautifulSoup(in_file.read(), "html.parser")
            links = [link.get("href")
                     for link in html.find_all("a")
                     if link_has_correct_class(link)]
            result = result + links
    return result


def link_has_correct_class(link):
    html_class = link.get("class")
    return html_class is not None and "bookmark_title" in html_class


def filter_bookmarks(bookmarks, links_to_remove):
    result = []
    for bookmark in bookmarks:
        if bookmark['href'] not in links_to_remove:
            result.append(bookmark)
    return result


def ping_bookmarks(bookmarks):
    number = 0
    now = datetime.date.today().ctime()
    for bookmark in bookmarks:
        if number % 10 == 0:
            print(f"Checking link #{number}...")
        try:
            req = requests.get(bookmark["href"])
            if req.status_code >= 400:
                bookmark["dead_link"] = f"[link dead with HTTP {req.status_code} as of {now}]"
        except Exception as err:
            bookmark["dead_link"] = f"[link dead with error {err} as of {now}]"
        number = number + 1
    return bookmarks


def group_bookmarks(bookmarks):
    years = []
    grouped = {}

    for bookmark in bookmarks:
        year = parse(bookmark['time']).year
        bookmark['processed_tags'] = process_tags(bookmark['tags'])
        if year not in grouped:
            years.append(year)
            grouped[year] = []
        grouped[year].append(bookmark)

    return grouped


def process_tags(tags):
    hashtags = []
    for tag in tags.split():
        hashtags.append(tag)
    if "delicious" not in hashtags:
        hashtags.append("pinboard")
    return hashtags


def write_files(grouped_bookmarks):
    years = grouped_bookmarks.keys()
    for year in sorted(years):
        out_file_name = f"{FOLDER}/results-{year}.md"
        with open(out_file_name, "w") as out_file:
            for bookmark in grouped_bookmarks[year]:
                formatted = format_bookmark(bookmark)
                out_file.write(formatted)


def format_bookmark(bookmark):
    tags = " ".join(bookmark['processed_tags'])
    if len(tags) > 0:
        tags += "\n"
    return (f"# {bookmark['description']}\n"
            f"{bookmark['href']}\n"
            f"{bookmark['dead_link']}\n"
            f"{bookmark['extended']}\n"
            f"{bookmark['time']}\n"
            f"{tags}\n\n")


def format_dead_link(bookmark):
    if bookmark["dead_link"] is True:
        return f"[link appears dead as of {datetime.date.today().ctime()}]\n"
    return ""

