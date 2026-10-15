from main import DEFAULT_DATA
from regressor import load_training_rows, regressor
from StemmedCountVectorizer import StemmedCountVectorizer


def test_stemmer_collapses_inflections():
    vectorizer = StemmedCountVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(["running runs", "run"])
    assert matrix.shape == (2, 1)


def test_sample_model_is_deterministic_and_separates_phrases():
    model = regressor(DEFAULT_DATA)
    comments = [
        "This excellent explanation made the algorithm clear.",
        "What a pile of garbage nonsense.",
    ]
    first = model.score(comments)
    second = model.score(comments)
    assert first == second
    assert set(first) == set(comments)
    assert first[comments[0]] > first[comments[1]]


def test_empty_comment_list():
    model = regressor(DEFAULT_DATA)
    assert model.score([]) == {}


def test_training_file_requires_body_and_score(tmp_path):
    path = tmp_path / "broken.jsonl"
    path.write_text('{"body": "only a body"}\n', encoding="utf-8")
    try:
        load_training_rows(path)
    except ValueError as exc:
        assert "body" in str(exc) and "score" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_empty_training_file(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("\n", encoding="utf-8")
    try:
        load_training_rows(path)
    except ValueError as exc:
        assert "No comments" in str(exc)
    else:
        raise AssertionError("expected ValueError")
