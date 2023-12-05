from example import Elasticsearch, helpers
import configparser

config = configparser.ConfigParser()
config.read("access.ini")

es = Elasticsearch(
    cloud_id=config["ELASTIC"]["cloud_id"],
    http_auth=(config["ELASTIC"]["user"], config["ELASTIC"]["password"]),
)

es.info()

es.index(
    index="lord-of-the-rings",
    document={"character": "Aragon", "quote": "It is not this day."},
)
