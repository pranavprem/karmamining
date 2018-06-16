import json
from elasticsearch import Elasticsearch, RequestsHttpConnection

esEndPoint = "search-url-shortener-t76w2u5nrhzsacc3n2oy3lvozi.us-west-1.es.amazonaws.com"

try:
    esClient = Elasticsearch(
        hosts=[{'host': esEndPoint, 'port': 443}],
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
        )


    file = open("data2.txt")
    for line in file:
        obj = json.loads(line)
        if "[deleted]" not in obj["body"]:
            esClient.index(index="karmaminers", doc_type="hit", body=json.dumps(obj))
except Exception as exception:
    print exception