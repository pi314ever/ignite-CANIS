import json
import pandas as pd
from collections import defaultdict
import re

DATA = "../data/data1.json"


def update_word_counts(word_counts, posts):
    for post in posts:
        # Remove links
        post["post"] = re.sub(r"http\S+", "", post["post"])
        # Grab chinese characters
        chinese = re.findall(r"[\u4e00-\u9fff]", post["post"])
        # Grab english words
        english = re.findall(r"[a-zA-Z'-]+", post["post"])

        # Add chinese words to word_counts
        for word in chinese:
            word_counts[word] += 1

        # Add english words to word_counts
        for word in english:
            word_counts[word.lower()] += 1
    return word_counts


def main():
    json_data = json.load(open(DATA))
    word_counts = defaultdict(int)
    for account in json_data:
        word_counts = update_word_counts(word_counts, json_data[account])

    word_counts_df = pd.DataFrame(
        {"word": word_counts.keys(), "count": word_counts.values()}, index=None
    )
    # Remove common words
    blacklist = [
        "the",
        "with",
        "for",
        "on",
        "is",
        "s",
        "的",
        "of",
        "in",
        "and",
        "a",
        "to",
        "-",
        "from",
        "at",
        "has",
        "as",
        "http",
        "by",
        "在",
        "it",
        "will",
        "its",
        "was",
        "are",
    ]
    for w in blacklist:
        word_counts_df = word_counts_df[word_counts_df["word"] != w]

    mean = word_counts_df["count"].mean()
    word_counts_df = word_counts_df[word_counts_df["count"] > mean]
    word_counts_df = word_counts_df.sort_values(by="count", ascending=False)
    print(word_counts_df.head(20))
    word_counts_df[: min(len(word_counts_df), 500)].to_csv(
        "../data/word_counts.csv", index=False
    )


if __name__ == "__main__":
    main()
