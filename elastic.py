"""Load a local JSONL comment dump into Elasticsearch.

This is the 2018 exploration script (Kibana was used to look at the training
dump). It is not on the request path. The AWS endpoint that used to be
hardcoded here has been removed; set ELASTICSEARCH_URL yourself.

Rows whose body contains ``[deleted]`` are skipped, matching the old script.
"""

import json
import os
import sys

from elasticsearch import Elasticsearch

INDEX = "karmaminers"


def index_file(path, client, index=INDEX):
    indexed = 0
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "[deleted]" in obj.get("body", ""):
                continue
            client.index(index=index, document=obj)
            indexed += 1
    return indexed


def _client_from_env(url):
    kwargs = {}
    api_key = os.environ.get("ELASTICSEARCH_API_KEY")
    if api_key:
        kwargs["api_key"] = api_key
    username = os.environ.get("ELASTICSEARCH_USERNAME")
    password = os.environ.get("ELASTICSEARCH_PASSWORD")
    if username and password:
        kwargs["basic_auth"] = (username, password)
    return Elasticsearch(hosts=url, **kwargs)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    url = os.environ.get("ELASTICSEARCH_URL")
    path = os.environ.get("ELASTICSEARCH_COMMENTS_FILE", "data2.txt")
    if argv:
        path = argv[0]
    if not url:
        raise SystemExit(
            "Set ELASTICSEARCH_URL. The previous AWS endpoint was removed "
            "from this script; point this at a cluster you control."
        )
    if not os.path.isfile(path):
        raise SystemExit(
            f"Comments file not found: {path}. Pass a path or set "
            "ELASTICSEARCH_COMMENTS_FILE. The original data2.txt was never committed."
        )
    client = _client_from_env(url)
    indexed = index_file(path, client)
    print(f"Indexed {indexed} comments into {INDEX}")
    return indexed


if __name__ == "__main__":
    main()
