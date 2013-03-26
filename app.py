from flask import Flask, request, json, Response, session
from pymongo import MongoClient
from bson import json_util, objectid
from flask.ext.login import *

Flask.secret_key = "p\xd2i\xe2\xf12@\x10Z\xc1^So+\xda\xf1\x01\xd6\n\xcd\xee1\xa6\x0c"

app = Flask(__name__)

# DB connection
conn = MongoClient()
db = conn.test

#user auth
login_manager = LoginManager()
login_manager.setup_app(app)


#TODO: add authentication
#TODO: Endpoints for user creation

class User:
  id = None
  def get(userid):
    user = db['users'].find_one({"_id":objectid.ObjectId(userid)})
  def get_id():
    return unicode(id)


@login_manager.user_loader
def load_user(userid):
  return User.get(userid)

# getting entries jsonified
def jentries(coll, scope={}):
  entries = {"entries": []}
  for entry in coll.find(scope):
    entries["entries"].append(entry)
  return entries


@app.route('/<user>/activities', methods = ['POST', 'GET'])
@login_required
def list_activities(user):

  #list activities
  if request.method == 'GET':
    coll = db[user]
    scope = {'activity': True}
    js = json.dumps(jentries(coll, scope), default=json_util.default)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

  #Create a new activity
  elif request.method == 'POST':
    entry = {
        'activity': True,
        'name': request.json['name']
        }
    oid = db[user].insert(entry)
    js = json.dumps(db[user].find_one({'_id': oid}), default=json_util.default)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/<user>/<activity>', methods = ['POST', 'GET'])
def entries(user, activity):
  #List an activity's entries
  if request.method == 'GET':
    coll = db[user]
    scope = {'activity': activity}
    js = json.dumps(jentries(coll, scope), default=json_util.default)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

  #Create a new entry
  elif request.method == 'POST':
    entry = {
        'activity': activity,
        'measure': request.json['measure'],
        'measurement': request.json['measurement']
        }
    oid = db[user].insert(entry)
    js = json.dumps(db[user].find_one({'_id': oid}), default=json_util.default)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/<user>/<objectID>', methods = ['DELETE'])
def delete_entry(user, objectID):
  db[user].remove({"_id":objectid.ObjectId(objectID)})
  resp = Response('removed', status=200, mimetype='application/json')
  return resp

if __name__ == '__main__':
  app.run(debug=True)
