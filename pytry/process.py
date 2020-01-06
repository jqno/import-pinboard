import json
from dateutil.parser import parse

FOLDER = "/Users/jqno/Desktop/pinboard"


def process():
    bookmarks = determine_bookmarks()
    grouped_bookmarks = group_bookmarks(bookmarks)
    write_files(grouped_bookmarks)


def determine_bookmarks():
    in_file_name = f"{FOLDER}/pinboard_export.json"
    with open(in_file_name, "r") as in_file:
        return json.load(in_file)


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
            f"{bookmark['extended']}"
            f"{bookmark['time']}\n"
            f"{tags}\n\n")

