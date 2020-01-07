import json
import os
import string
from dateutil.parser import parse
from bs4 import BeautifulSoup

FOLDER = "/Users/jqno/Desktop/pinboard"
VALID_CHARS = "-_.() %s%s" % (string.ascii_letters, string.digits)


def process():
    bookmarks = determine_bookmarks()
    twitter_favs = determine_twitter_favs()
    filtered_bookmarks = filter_bookmarks(bookmarks, twitter_favs)
    processed_bookmarks = process_bookmarks(filtered_bookmarks)
    write_files(processed_bookmarks)


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


def process_bookmarks(bookmarks):
    for bookmark in bookmarks:
        bookmark['processed_tags'] = process_tags(bookmark['tags'])
    return bookmarks


def process_tags(tags):
    hashtags = []
    for tag in tags.split():
        if tag == "delicious":
            hashtags.append("source:delicious")
        else:
            hashtags.append(tag)
    if "source:delicious" not in hashtags:
        hashtags.append("source:pinboard")
    return hashtags


def write_files(bookmarks):
    for bookmark in bookmarks:
        year = parse(bookmark["time"]).year
        sanitized = sanitize(bookmark["description"])
        out_file_name = f"{FOLDER}/{year}/{sanitized}.md"

        create_dir(year)
        with open(out_file_name, "w") as out_file:
            formatted = format_bookmark(bookmark)
            out_file.write(formatted)


def sanitize(text):
    return "".join(c for c in text if c in VALID_CHARS)


def create_dir(year):
    try:
        os.mkdir(f"{FOLDER}/{year}")
    except FileExistsError:
        pass


def format_bookmark(bookmark):
    tags = " ".join(bookmark['processed_tags'])
    if len(tags) > 0:
        tags += "\n"
    time = parse(bookmark["time"])
    return (f"{bookmark['href']}\n"
            f"{tags}\n"
            f"{bookmark['description']}\n"
            f"{bookmark['extended']}"
            f"{time.date()}\n")

