import pytest

from main import DEMO_POST_ID, combine_scores, create_app, ranked_comments


class FakeContext:
    def fetch_comments(self, post_id):
        if post_id == "missing":
            raise RuntimeError("Missing Reddit credentials: REDDIT_CLIENT_ID")
        if post_id == "boom":
            raise RuntimeError("should not be used")
        return ["alpha", "beta"]

    def score(self, comments):
        return {comments[0]: 2.0, comments[1]: 4.0}


class FakeRegressor:
    def score(self, comments):
        return {comments[0]: 3.0, comments[1]: 1.5}


@pytest.fixture
def fake_client():
    app = create_app(context_model=FakeContext(), regression_model=FakeRegressor())
    app.config.update(TESTING=True)
    return app.test_client()


def test_combine_truncates_toward_zero():
    combined = combine_scores({"a": 2.9}, {"a": 2})
    assert combined == {"a": 5}


def test_tie_breaks_on_reverse_text_order():
    ranked = ranked_comments({"alpha": 6, "beta": 6})
    assert [row["comment"] for row in ranked] == ["beta", "alpha"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_debug_routes_return_comment_objects(fake_client):
    for path in ("/context_analyze/abc123", "/regressor1/abc123"):
        response = fake_client.get(path)
        assert response.status_code == 200
        payload = response.get_json()
        assert payload
        assert set(payload[0]) == {"comment", "score"}


def test_combined_sorts_product(fake_client):
    response = fake_client.get("/combined/abc123")
    assert response.status_code == 200
    payload = response.get_json()
    # alpha = int(2 * 3) = 6, beta = int(4 * 1.5) = 6, so text order wins.
    assert [row["comment"] for row in payload] == ["beta", "alpha"]
    assert [row["score"] for row in payload] == [6, 6]


def test_missing_credentials_are_a_client_error(fake_client):
    response = fake_client.get("/combined/missing")
    assert response.status_code == 400
    assert "credential" in response.get_json()["error"].lower()


def test_demo_route_scores_sample_without_reddit(client):
    response = client.get(f"/combined/{DEMO_POST_ID}")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload
    assert set(payload[0]) == {"comment", "score"}
    scores = [row["score"] for row in payload]
    assert scores == sorted(scores, reverse=True)
    assert any(score != scores[0] for score in scores)
