from flask import Flask, request, json, Response
from pymongo import MongoClient
from bson import json_util, objectid

app = Flask(__name__)

#TODO: add authentication
#TODO: Endpoints for user creation

# DB connection
conn = MongoClient()
db = conn.test

# getting entries jsonified
def jentries(coll, scope={}):
  entries = {"entries": []}
  for entry in coll.find(scope):
    entries["entries"].append(entry)
  return entries

#list all activities a user has
@app.route('/<user>/activities', methods = ['POST', 'GET'])
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
