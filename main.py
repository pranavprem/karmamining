import json
import os
from contextual import contextual
from regressor import regressor
from flask import Flask

app = Flask(__name__)
cont = contextual()
regr = regressor("data1.txt")

@app.route("/context_analyze/<post_id>")
def onlycontext(post_id):
    print("hit flask" + post_id)
    comments = sorted(cont.build(post_id).iteritems(),  key=lambda kv: (kv[1],kv[0]),reverse=True)
    comms=[]
    for comment in comments:
        temp=dict()
        temp["comment"]=comment
        temp["score"]=comments[comment]
        comms.append(temp)    
    return json.dumps(comms)


@app.route("/regressor1/<post_id>")
def onlyregressor1(post_id):
    print("hit flask" + post_id)
    comments = sorted(regr.build(post_id).iteritems(), key=lambda kv: (kv[1],kv[0]),reverse=True)
    return json.dumps(comments)

@app.route("/combined/<post_id>")
def combined(post_id):
    print("hit flask" + post_id)
    com1=cont.build(post_id)
    com2=regr.build(post_id)
    comments=dict()
    for key in com1:
        comments[key] = int(com1[key] * com2[key])
    comments = sorted(comments.iteritems(), key=lambda kv: (kv[1],kv[0]),reverse=True)
    comms=[]
    for comment in comments:
        temp=dict()
        temp["comment"]=comment[0]
        temp["score"] = comment[1]
        comms.append(temp)
    print "Completed"
    return json.dumps(comms)
        

if __name__ == "__main__":
    heroku_port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=heroku_port)