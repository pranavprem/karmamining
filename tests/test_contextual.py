import pytest

from contextual import contextual


def test_cosine_edges():
    assert contextual.distance([1, 0], [1, 0]) == 1
    assert contextual.distance([1, 0], [0, 1]) == 0
    assert contextual.distance([0, 0], [1, 2]) == 0


def test_shared_words_rank_higher():
    model = contextual()
    comments = [
        "cats and dogs are great pets",
        "cats and dogs play outside",
        "the stock market crashed today",
    ]
    scores = model.score(comments)
    assert scores[comments[0]] > scores[comments[2]]
    assert scores[comments[1]] > scores[comments[2]]


def test_stopwords_only_score_zero():
    model = contextual()
    scores = model.score(["the and of", "cats purr loudly"])
    assert scores["the and of"] == 0
    assert scores["cats purr loudly"] == pytest.approx(1)


def test_duplicate_text_collapses_to_one_key():
    model = contextual()
    scores = model.score(["cats purr loudly", "cats purr loudly"])
    assert list(scores) == ["cats purr loudly"]
