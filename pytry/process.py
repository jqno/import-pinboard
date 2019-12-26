import json


def process():
    with open("/Users/jqno/Desktop/pinboard_export.json", "r") as in_file, \
         open("/Users/jqno/Desktop/results.md", "w") as out_file:
        decoded = json.load(in_file)
        for bookmark in decoded:
            if bookmark["description"] != "Twitter":
                out_file.write(format_bookmark(bookmark))


def format_bookmark(bookmark):
    return (f"# {bookmark['description']}\n"
            f"{bookmark['href']}\n"
            f"{bookmark['time']}\n"
            f"{format_tags(bookmark['tags'])}\n\n")


def format_tags(tags):
    hashtags = []
    for tag in tags.split():
        hashtags.append(f"#{tag}")
    result = " ".join(hashtags)
    if len(result) == 0:
        return ""
    return result + "\n"
