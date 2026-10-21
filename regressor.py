"""Bayesian ridge regressor over stemmed TF-IDF comment text.

The model is trained at construction time from a JSONL file of
``{"body": "...", "score": 12}`` rows. The original project trained on about
1.2 million Reddit comments. That dump was never committed; the default file
is a small stand-in so the server can boot.
"""

import json

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import BayesianRidge

from reddit_client import reddit_client
from StemmedCountVectorizer import StemmedCountVectorizer

# The report describes trying 8,000 features. The code that shipped used 1,000.
FEATURE_COUNT = 1000


def load_training_rows(path):
    comments = []
    scores = []
    with open(path, encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number} is not valid JSON") from exc
            try:
                comments.append(data["body"])
                scores.append(data["score"])
            except KeyError as exc:
                raise ValueError(
                    f"{path}:{line_number} must include 'body' and 'score'"
                ) from exc
    if not comments:
        raise ValueError(f"No comments found in {path}")
    return comments, scores


class regressor:
    def __init__(self, file_name, reddit=None):
        self.reddit = reddit
        self.file_name = file_name
        comments, scores = load_training_rows(file_name)
        self.vect = StemmedCountVectorizer(stop_words="english")
        counts = self.vect.fit_transform(comments)
        self.tfidf = TfidfTransformer()
        transformed = self.tfidf.fit_transform(counts)
        feature_count = transformed.shape[1]
        if feature_count == 0:
            raise ValueError(
                f"Training comments in {file_name} produced no usable words"
            )
        # f_classif was the 2018 default and emits NaN scores when a karma
        # value appears only once. f_regression matches the model that is fit.
        k = min(FEATURE_COUNT, feature_count)
        self.reducer = SelectKBest(score_func=f_regression, k=k)
        reduced = self.reducer.fit_transform(transformed, scores)
        if hasattr(reduced, "toarray"):
            reduced = reduced.toarray()
        self.reg = BayesianRidge()
        self.reg.fit(reduced, scores)

    def _client(self):
        if self.reddit is None:
            self.reddit = reddit_client()
        return self.reddit

    def fetch_comments(self, post_id):
        submission = self._client().submission(id=post_id)
        submission.comments.replace_more(limit=0)
        bodies = []
        for comment in submission.comments:
            body = getattr(comment, "body", None)
            if body:
                bodies.append(body)
        return bodies

    def score(self, comments):
        if not comments:
            return {}
        transformed = self.tfidf.transform(self.vect.transform(comments))
        reduced = self.reducer.transform(transformed)
        if hasattr(reduced, "toarray"):
            reduced = reduced.toarray()
        predictions = self.reg.predict(reduced)
        scheme = {}
        for index, comment in enumerate(comments):
            scheme[comment] = float(predictions[index])
        return scheme

    def build(self, post_id):
        return self.score(self.fetch_comments(post_id))
