import praw
import json
import sklearn
import os
from sklearn import linear_model
from StemmedCountVectorizer import StemmedCountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer



class regressor(object):
    def __init__(self, fileName):
        self.reddit = praw.Reddit(user_agent='Comment Extraction (by /u/pranavprem93)',
                     client_id='hZAxHcMgWrhJqg', client_secret=os.environ["client_secret"],
                     username='pranavprem93', password=os.environ["reddit_password"])
        file = open(fileName)
        comments = []
        scores =[]
        for line in file:
            data = json.loads(line)
            comments.append(data["body"])
            scores.append(data["score"])
        self.vect = StemmedCountVectorizer(stop_words='english')
        self.trainer = self.vect.fit_transform(comments)
        self.tfidf = TfidfTransformer()
        self.trainer2 = self.tfidf.fit_transform(self.trainer)
        self.reducer = sklearn.feature_selection.SelectKBest(k=1000)
        reduced_data = self.reducer.fit_transform(self.trainer2, scores)
        self.reg = linear_model.BayesianRidge()
        self.reg.fit(reduced_data.toarray(), scores)
    
    def build(self, post_id):
        submission = self.reddit.submission(id=post_id)
        submission.comments.replace_more(limit=0)
        comments=[]
        for comment in submission.comments:
            comments.append(comment.body)
        test = self.vect.transform(comments)
        test = self.tfidf.transform(test)
        reduced=self.reducer.transform(test)
        predictions=self.reg.predict(reduced)
        scheme=dict()
        for i in range(0,len(predictions)):
            scheme[comments[i]] = predictions[i]
        return scheme
