from flask import Flask, request, json, Response, session, send_from_directory
from pymongo import MongoClient
from bson import json_util, objectid
from flask.ext.login import *

Flask.secret_key = "NotTheKeyUsedWhenDeployed"

app = Flask(__name__)

# DB connection
conn = MongoClient()
db = conn.test

#user auth
login_manager = LoginManager()
login_manager.setup_app(app)

#TODO: Endpoints for user creation
#TODO: Dates and times

class User(object):
  def __init__(self, username, userId, active=True):
    self.username = username
    self.userId = userId
    self.activeStatus = active
  
  def is_authenticated(self):
    return True
    
  def is_active(self):
    return self.activeStatus
    
  def is_anonymous(self):
    return False
    
  def get_id(self):
    if self.userId is not None:
      return unicode(self.userId)
    else:
      return None

@login_manager.user_loader
def load_user(userid):
  userDoc = db['users'].find_one({"_id":objectid.ObjectId(userid)})
  getUser = User(userDoc['username'], userDoc['_id'])
  return getUser

# getting entries jsonified
def jentries(coll, scope={}):
  entries = {"entries": []}
  for entry in coll.find(scope):
    entries["entries"].append(entry)
  return entries

def loginUser(username, password):
  userDict = db.users.find_one({'username':username})
  if (userDict is not None) and (userDict["password"] == password):
    user = User(userDict['username'], userDict['_id'])
    login_user(user)
    return True
  else:
    return False

# Routes

@app.route('/index')
def index():
  return send_from_directory('./', 'index.html')

@app.route('/login', methods = ['POST'])
def loginPerson():
  if request.method == 'POST':
    username = request.json['username']
    password = request.json['password']
    success = loginUser(username, password)
    if success:
      return 'successfully logged in'
    else:
      return 'error'
    
@app.route('/logout')
def logoutPerson():
  logout_user()
  return 'logged out'
    
@app.route('/session')
def put_session():
  js = json.dumps(session)
  resp = Response(js, status=200, mimetype='application/json')
  return resp

@app.route('/activities', methods = ['POST', 'GET'])
@login_required
def list_activities():
  user = current_user.username

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
        'measure': request.json['measure'],
        }
    oid = db[user].insert(entry)
    js = json.dumps(db[user].find_one({'_id': oid}), default=json_util.default)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/<activity>', methods = ['POST', 'GET'])
@login_required
def entries(activity):
  user = current_user.username
  
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
        'measurement': request.json['measurement']
        'datetime': request.json['datetime']
        }
    oid = db[user].insert(entry)
    js = json.dumps(db[user].find_one({'_id': oid}), default=json_util.default)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/<objectID>', methods = ['DELETE'])
@login_required
def delete_entry(objectID):
  user = current_user.username
  db[user].remove({"_id":objectid.ObjectId(objectID)})
  resp = Response('removed', status=200, mimetype='application/json')
  return resp
  
@app.route('/users', methods = ['POST'])
def create_user()
  if request.method == 'POST':
    new_user = {
      'username': request.json['username']
      'password': request.json['password']
    }
    db['users'].insert(new_user)
    return Response(status=200, mimetype='application/json')

if __name__ == '__main__':
  app.run(debug=True)
