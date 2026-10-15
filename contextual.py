"""Within-thread relevance scores.

Each comment is bag-of-words tokenized (lowercase, alphabetic tokens, English
stopwords removed). Its score is the sum of cosine similarities with every
comment in the thread, including itself. That is the 2018 context analyzer:
comments that share words with the rest of the thread rank higher.

Stemming is intentionally not applied here. Only the regressor stems.
"""

import math

from nltk import word_tokenize
from nltk.corpus import stopwords

from reddit_client import reddit_client

_NLTK_READY = False


def ensure_nltk():
    """Download the tokenizer and stopword lists once per process."""
    global _NLTK_READY
    if _NLTK_READY:
        return
    import nltk

    resources = {
        "punkt": "tokenizers/punkt",
        "punkt_tab": "tokenizers/punkt_tab",
        "stopwords": "corpora/stopwords",
    }
    for name, path in resources.items():
        try:
            nltk.data.find(path)
        except LookupError:
            downloaded = nltk.download(name, quiet=True)
            if not downloaded:
                raise RuntimeError(
                    f"NLTK data '{name}' is not available. "
                    f"Install it with: python -m nltk.downloader {name}"
                ) from None
    _NLTK_READY = True


class contextual:
    def __init__(self, reddit=None):
        self.reddit = reddit
        self._stop_words = None

    def _client(self):
        if self.reddit is None:
            self.reddit = reddit_client()
        return self.reddit

    def _stops(self):
        if self._stop_words is None:
            ensure_nltk()
            self._stop_words = set(stopwords.words("english"))
        return self._stop_words

    def fetch_comments(self, post_id):
        submission = self._client().submission(id=post_id)
        # limit is keyword-only on PRAW 8. limit=0 drops "load more" stubs
        # without extra requests, which is what the 2018 code did.
        submission.comments.replace_more(limit=0)
        bodies = []
        for comment in submission.comments:
            body = getattr(comment, "body", None)
            if body:
                bodies.append(body)
        return bodies

    def score(self, comments):
        stop_words = self._stops()
        filtered = []
        vocabulary = set()
        for comment in comments:
            tokens = word_tokenize(comment)
            tokens = [token.lower() for token in tokens]
            tokens = [token for token in tokens if token.isalpha()]
            tokens = [token for token in tokens if token not in stop_words]
            filtered.append(tokens)
            vocabulary.update(tokens)

        columns = sorted(vocabulary)
        matrix = []
        for tokens in filtered:
            matrix.append([tokens.count(word) for word in columns])

        distances = []
        for row in matrix:
            total = 0
            for other in matrix:
                total += self.distance(row, other)
            distances.append(total)

        scheme = {}
        for index, comment in enumerate(comments):
            scheme[comment] = distances[index]
        return scheme

    def build(self, post_id):
        return self.score(self.fetch_comments(post_id))

    @staticmethod
    def distance(list1, list2):
        numerator = 0
        sum_of_squares_a = 0
        sum_of_squares_b = 0
        for index in range(len(list1)):
            numerator += list1[index] * list2[index]
            sum_of_squares_a += list1[index] * list1[index]
            sum_of_squares_b += list2[index] * list2[index]
        denominator = math.sqrt(sum_of_squares_a) * math.sqrt(sum_of_squares_b)
        if denominator == 0.0:
            return 0
        return numerator / denominator
