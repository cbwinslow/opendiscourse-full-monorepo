import csv


def save_articles_to_csv(articles, filename="news_articles.csv"):
    if not articles:
        print("No articles to save.")
        return
    keys = articles[0].keys()  # Assumes all articles have similar structure
    with open(filename, "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(articles)
    print(f"Articles saved to {filename}")
