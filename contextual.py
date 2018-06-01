import string
from nltk.corpus import stopwords
from scipy import spatial
import praw
import math
from nltk import word_tokenize
import os

class contextual(object):
    def __init__(self):
        self.reddit = praw.Reddit(user_agent='Comment Extraction (by /u/pranavprem93)',
                     client_id='hZAxHcMgWrhJqg', client_secret=os.environ["client_secret"],
                     username='pranavprem93', password=os.environ["reddit_password"])
    def build(self, postid):
        submission = self.reddit.submission(id=postid)
        submission.comments.replace_more(limit=0)
        comments=[]
        for comment in submission.comments:
            comments.append(comment.body)
        stop_words = set(stopwords.words('english'))
        filtered=[]
        bag = set()
        for comment in comments:
            tokens= word_tokenize(comment)
            tokens = [w.lower() for w in tokens]
            tokens = [word for word in tokens if word.isalpha()]
            tokens = [w for w in tokens if w not in stop_words]
            filtered.append(tokens)
            bag |= set(tokens)
        matrix=[]
        for comment in filtered:
            temp=[]
            for word in bag:
                temp.append(comment.count(word))
            matrix.append(temp)
        
        distances=[]
        for row1 in matrix:
            temp=0
            for row2 in matrix:
                temp+=self.distance(row1,row2)
            distances.append(temp)
        
       
        scheme = dict()
        
        for i in range(0,len(distances)):
            scheme[comments[i]] = distances[i]
        
        
        return scheme
            
    
    def distance(self,list1,list2):
        numerator=0
        denominator=0
        s1=s2=0
        for i in range(0,len(list1)):
            numerator+=list1[i]*list2[i]
            s1+=list1[i]*list1[i]
            s2+=list2[i]*list2[i]
        s1=math.sqrt(s1)
        s2=math.sqrt(s2)
        denominator=s1*s2
        if denominator==0.0:
            return 0
        return numerator/denominator   