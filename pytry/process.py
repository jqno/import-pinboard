import json
from bs4 import BeautifulSoup
from dateutil.parser import parse

FOLDER = "/Users/jqno/Desktop/pinboard"


def process():
    bookmarks = determine_bookmarks()
    twitter_favs = determine_twitter_favs()
    filtered_bookmarks = filter_bookmarks(bookmarks, twitter_favs)
    processed_bookmarks = process_bookmarks(filtered_bookmarks)
    grouped_bookmarks = group_bookmarks(processed_bookmarks)
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


def group_bookmarks(bookmarks):
    years = []
    grouped = {}

    for bookmark in bookmarks:
        year = parse(bookmark['time']).year
        if year not in grouped:
            years.append(year)
            grouped[year] = []
        grouped[year].append(bookmark)

    return grouped


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
            f"{bookmark['extended']}"
            f"{bookmark['time']}\n"
            f"{tags}\n\n")

