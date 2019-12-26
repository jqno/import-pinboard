import json
from dateutil.parser import parse


def process():
    in_file_name = "/Users/jqno/Desktop/pinboard_export.json"
    with open(in_file_name, "r") as in_file:
        decoded = json.load(in_file)
        years = []
        grouped = {}

        for bookmark in decoded:
            year = parse(bookmark['time']).year
            formatted = format_bookmark(bookmark)
            if year not in grouped:
                years.append(year)
                grouped[year] = []
            grouped[year].append(formatted)

        for year in sorted(years):
            out_file_name = f"/Users/jqno/Desktop/results-{year}.md"
            with open(out_file_name, "w") as out_file:
                for bookmark in grouped[year]:
                    out_file.write(bookmark)


def format_bookmark(bookmark):
    return (f"# {bookmark['description']}\n"
            f"{bookmark['href']}\n"
            f"{bookmark['time']}\n"
            f"{format_tags(bookmark['tags'])}\n\n")


def format_tags(tags):
    hashtags = []
    for tag in tags.split():
        hashtags.append(tag)
    if "delicious" not in hashtags:
        hashtags.append("pinboard")
    result = " ".join(hashtags)
    if len(result) == 0:
        return ""
    return result + "\n"

