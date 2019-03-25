#Library Imports

from flask import Flask, request, session, Response
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
from flask_session import Session
import re
import base64
import json
import requests


# Initial Setup


#Flask Setup
app = Flask(__name__)
api = Api(app)

#Session Setup
sess = Session()

#MongoDB Setup
app.config["MONGO_URI"] = "mongodb://localhost:27017/cc_db"
mongo = PyMongo(app)



# Functions


def convertCursor(info):
    data = []
    for x in info:
        data.append(x)
    return data	

def mergeDicts(dicts):
	data = {}
	for d in dicts:
		data.update(d)
	return data

def isBase64(s):
    pattern = re.compile("^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$")
    if not s or len(s) < 1:
        return False
    else:
        return pattern.match(s)

def stripList(l, lLimit, uLimit):
	l.reverse()
	data = []
	for i in range(lLimit-1 ,uLimit):
		data.append(l[i])
	return data

def incrementHTTP():
	mongo.db.http.insert_one({'http': 1})


# Category Class

class Cats(Resource):

	def get(self, cname=None):
		incrementHTTP()
		if(cname):
			return "", 405
		cursor = mongo.db.cats.find({}, {"_id": 0, "update_time": 0})
		if(not(cursor)):
			return "ERROR", 400
		else:
			data = convertCursor(cursor)
			if(data == []):
				return "There are no Categories", 204
			else:
				data = mergeDicts(data)
				return data, 200

	def post(self, cname=None):
		incrementHTTP()
		if(cname):
			return "", 405
		data = request.get_json()
		if(not(data)):
			return "ERROR", 400
		else:
			cname = data[0]
			if(cname=="" or cname==" "):
				return "Enter a Category Name", 400
			x = mongo.db.cats.distinct(cname)
			print(x)
			if(x!=[]):
				return "category already exists.", 405
			else:
				mongo.db.cats.insert_one({cname:0})
				return {}, 201

	def delete(self,cname=None):
		incrementHTTP()
		if(cname):
			x = mongo.db.cats.distinct(cname)
			if(x==[]):
				return 'category not found', 405
			else:
				r = mongo.db.cats.remove({cname: x[0]})
				r = mongo.db.acts.remove({"categoryName": cname})
				return {}, 200
		else:
			return "category missing", 400


# Acts Class

class Acts(Resource):

	def get(self, cname=None, actId=None):
		incrementHTTP()

		if(actId):
			return "",405

		startRange = request.args.get('start')
		endRange = request.args.get('end')
		
		if(cname==None):
			return "",405
		
		if(startRange==None and endRange==None):

			temp = mongo.db.cats.distinct(cname)
			if(temp == []):
				return "Category Name does not exist", 405

			elif(temp[0]>=100):
				return "Too many acts", 413

			cursor = mongo.db.acts.find({"categoryName": cname}, {"_id": 0, "update_time": 0})
			data = convertCursor(cursor)

			if(data == []):
				return "There are no acts in the category", 204

			l = []

			for d in data:
				l.append(d)

			return l, 200

		
		elif(startRange!=None and endRange!=None):

			startRange = int(startRange)
			endRange = int(endRange)

			temp = mongo.db.cats.distinct(cname)
			if(temp == []):
				return "Category Name does not exist", 405
			noActs = int(temp[0])

			if((startRange<1) or (endRange>noActs)):
				return "Give Valid Range", 400

			if((endRange-startRange+1)>100):
				return "Too many acts", 413

			cursor = mongo.db.acts.find({"categoryName": cname}, {"_id": 0, "update_time": 0})
			data = convertCursor(cursor)

			data = stripList(data, startRange, endRange)
			return data, 200

		
		else:
			return "ERROR", 400


	def post(self, cname=None, actId=None):
		incrementHTTP()

		if(actId):
			return "",405

		if(cname):
			return "",405

		data = request.get_json()
		if(not(data)):
			return "ERROR", 400

		try:
			actId = data["actId"]
			username = data["username"]
			timestamp = data["timestamp"]
			caption = data["caption"]
			categoryName = data["categoryName"]
			imgB64 = data["imgB64"]
		except:
			return "Key in all the details", 400

		cursor = mongo.db.acts.find({"actId": actId})
		temp = convertCursor(cursor)
		if(temp!=[]):
			return "Enter a valid act ID", 400

		temp = re.search("[0-3][0-9]-[0-1][0-9]-[0-9][0-9][0-9][0-9]:[0-5][0-9]-[0-5][0-9]-[0-2][0-9]", timestamp)
		if(not(temp)):
			return "Enter a valid timestamp", 400

		#cursor = mongo.db.user.find({"username": username})
		#temp = convertCursor(cursor)
		r = requests.get("http://3.209.1.133:8080/api/v1/users")
		temp = False
		if(r.status_code == 200):
			j = r.json()
			print(j)
			if(username in j):
				temp = True
		if(not(temp)):
			return "User does not exist", 405

		if(not(isBase64(imgB64))):
			return "Image not encoded", 400

		try:
			upvotes = data["upvotes"]
			return "Bad Request", 400
		except:
			temp = mongo.db.cats.distinct(categoryName)
			if(temp == []):
				return "Category Name does not exist", 405

		data = {"actId": actId, "username": username, "timestamp": timestamp, "caption": caption, "categoryName": categoryName, "upvotes": 0, "imgB64": imgB64}
		mongo.db.acts.insert_one(data)
		tot = temp[0] + 1
		r = mongo.db.cats.remove({categoryName: temp[0]})
		mongo.db.cats.insert_one({categoryName: tot})
		return {}, 201


	def delete(self,actId=None,cname=None):
		incrementHTTP()
		if(cname):
			return "",405
		if(not(actId)):
			return "Enter a valid actId", 405
		cursor = mongo.db.acts.find({"actId": actId})
		data = convertCursor(cursor)
		if(data == []):
			return "Act does not exist", 405
		r = mongo.db.acts.remove({"actId": actId})
		categoryName = data[0]["categoryName"]
		temp = mongo.db.cats.distinct(categoryName)
		tot = temp[0] - 1
		r = mongo.db.cats.remove({categoryName: temp[0]})
		mongo.db.cats.insert_one({categoryName: tot})
		return {}, 200


# Other Classes

class numberActs(Resource):

	def get(self,cname):
		incrementHTTP()
		temp = mongo.db.cats.distinct(cname)
		if(temp == []):
			return "Category Name does not exist", 405
		temp = temp[0]
		temp = int(temp)
		x = 0
		if(temp == 0):
			return [x], 204
		else:
			return [temp], 200


class upvote(Resource):

	def post(self):
		incrementHTTP()
		data = request.get_json()
		try:
			actId = data[0]
			actId = int(actId)
		except:
			return "Enter an Act Id", 400
		cursor = mongo.db.acts.find({"actId": actId})
		data = convertCursor(cursor)
		if(data == []):
			return "Enter a valid Act Id", 405
		d = data[0]
		x = d.pop("upvotes")
		d["upvotes"] = x + 1
		r = mongo.db.acts.remove({"actId": actId})
		mongo.db.acts.insert_one(d)
		return {}, 200

class actCount(Resource):

	def get(self):
		incrementHTTP()
		count = mongo.db.acts.count()
		if(count>=0):
			return [count], 200
		else:
			return "Method not Allowed", 405

class httpCount(Resource):

	def get(self):
		count = mongo.db.http.count()
		if(count>=0):
			return [count], 200
		else:
			return "Method not Allowed", 405

	def delete(self):
		r = mongo.db.http.drop()
		return {}, 200

# Resources for Categories

api.add_resource(Cats, "/api/v1/categories", endpoint="nocname")
api.add_resource(Cats, "/api/v1/categories/<string:cname>", endpoint="cname")

# Resources for Acts

api.add_resource(Acts,"/api/v1/categories/<string:cname>/acts",endpoint="allActs")
api.add_resource(Acts,"/api/v1/acts/<int:actId>",endpoint="removeAct")
api.add_resource(Acts,"/api/v1/acts",endpoint="addAct")

# Additional Resources

api.add_resource(numberActs,"/api/v1/categories/<string:cname>/acts/size",endpoint="noActs")
api.add_resource(upvote,"/api/v1/acts/upvote",endpoint="upvote")
api.add_resource(actCount,"/api/v1/acts/count",endpoint="actcount")

#HTTP Resource

api.add_resource(httpCount,"/api/v1/_count",endpoint="httpcount")


# Run the App
if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'mongodb'

    sess.init_app(app)

    app.run(debug=True)