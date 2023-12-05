import mechanicalsoup as ms
import redis
import configparser
from elasticsearch import Elasticsearch, helpers

config = configparser.ConfigParser()
config.read("access.ini")

es = Elasticsearch(
    cloud_id=config["ELASTIC"]["cloud_id"],
    http_auth=(config["ELASTIC"]["user"], config["ELASTIC"]["password"]),
)
print(es.info())

result = es.search(index="webpage", query={"match": {"html": "html"}})
print(result)


def write_to_elastic(es, url, html):
    es.index(index="webpages", document={"url": url.decode("utf-8"), "html": html})


def crawl(browser, r, es, url):
    browser.open(url)

    # cache to elasticsearch
    write_to_elastic(es, url, str(browser.page))

    # Parse more urls
    print("Parsing for more links")
    a_tags = browser.page.find_all("a")
    hrefs = [a.get("href") for a in a_tags]
    # Get specifically wikipedia URLs
    wikipedia_domain = "https://en.wikipedia.org"
    links = [wikipedia_domain + a for a in hrefs if a and a.startswith("/wiki/")]

    # Place URLs in Redis queue
    # Created Redis linkedlist -> links
    print("Pushing links onto Redis")
    r.lpush("links", *links)


browser = ms.StatefulBrowser()
redis_conn = redis.Redis()

start_url = "https://en.wikipedia.org/wiki/Redis"
redis_conn.lpush("links", start_url)

while link := redis_conn.rpop("links"):
    if "jesus" in str(link).lower():
        break
    crawl(browser, redis_conn, es, link)
