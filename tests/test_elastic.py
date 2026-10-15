import pytest

import elastic


def test_index_skips_deleted_bodies(tmp_path):
    path = tmp_path / "comments.jsonl"
    path.write_text(
        "\n".join(
            [
                '{"body": "hello there", "score": 3}',
                '{"body": "[deleted]", "score": 1}',
                '{"body": "this mentions [deleted] accounts", "score": 2}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    class FakeClient:
        def __init__(self):
            self.docs = []

        def index(self, *, index, document):
            self.docs.append((index, document))

    client = FakeClient()
    indexed = elastic.index_file(path, client)
    assert indexed == 1
    assert client.docs == [(elastic.INDEX, {"body": "hello there", "score": 3})]


def test_main_requires_a_url(monkeypatch):
    monkeypatch.delenv("ELASTICSEARCH_URL", raising=False)
    with pytest.raises(SystemExit) as exc:
        elastic.main()
    assert "ELASTICSEARCH_URL" in str(exc.value)
