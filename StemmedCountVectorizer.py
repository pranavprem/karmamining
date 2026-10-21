from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer


class StemmedCountVectorizer(CountVectorizer):
    """Count vectorizer that snowball-stems English tokens.

    ``stop_words='english'`` uses scikit-learn's list, not NLTK's, matching
    the original regressor.
    """

    def build_analyzer(self):
        stemmer = SnowballStemmer("english", ignore_stopwords=True)
        analyzer = super().build_analyzer()
        return lambda doc: [stemmer.stem(word) for word in analyzer(doc)]
