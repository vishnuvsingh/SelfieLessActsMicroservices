#Library Imports

from flask import Flask, request, session, Response
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
from flask_session import Session
import re
import base64
import json


# Initial Setup


#Flask Setup
app = Flask(__name__)
api = Api(app)

#Session Setup
sess = Session()

#MongoDB Setup
app.config["MONGO_URI"] = "mongodb://localhost:27017/cc_db"
mongo = PyMongo(app)

def convertCursor(info):
    data = []
    for x in info:
        data.append(x)
    return data	

def strip(data):
    temp = data[0]['username']
    passtemp = data[0]['password']
    d = {'username': temp, 'password': passtemp}
    return d

def checkSHA1(password):
    try:
        temp = int(password,16)
    except:
        return False
    if(len(password)==40):
        return True
    else:
        return False


#Login Class

class Login(Resource):

	def post(self):
		data = request.get_json()

		if(not(data)):
			return "ERROR", 400

		else:

			uname = data.get('username')
			password = data.get('password')

			if(not(uname and password)):
				return "Enter Valid Credentials", 400

			else:

				x = mongo.db.user.find({'username': uname, 'password': password})
				y = convertCursor(x)

				if(y==[]):
					return "Enter Valid Credential", 405

				else:
					return {}, 200


# User Class

class User(Resource):

	def get(self, uname=None):
		if(uname):
			return "", 405
		user_info = mongo.db.user.find({}, {"_id": 0, "update_time": 0})
		if(user_info == []):
			return "No Users", 204
		user_list = []
		for user in user_info:
			user_list.append(user["username"])
		return user_list, 200


	
	def post(self, uname=None):
		if(uname):
			return "", 405
		data = request.get_json()
		if(not(data)):
			return "ERROR", 400
		else:
		    uname = data.get('username')
		    password = data.get('password')
		    if(uname and password):
		        if(checkSHA1(password)):
		            x = mongo.db.user.find({'username': uname})
		            y = convertCursor(x)
		            if(y!=[]):
		                return "username already exists.", 405
		            else:
		                mongo.db.user.insert_one(data)
		                return {}, 201
		        else:
		        	return "password is not SHA", 400
		    else:
		    	return "username or password missing", 400
		        

	def delete(self, uname=None):
	    data = []
	    if(uname):
	        user_info = mongo.db.user.find({"username": uname})
	        data = convertCursor(user_info)
	        if(data==[]):
	            return 'user not found', 405
	        else:
	            data = strip(data)
	            r = mongo.db.user.remove({"username": uname})
	            return {}, 200
	    else:
	        return "username missing", 400



# Resources for User


api.add_resource(Login, "/api/v1/login", endpoint="login")

api.add_resource(User, "/api/v1/users", endpoint="add user")
api.add_resource(User, "/api/v1/users/<string:uname>", endpoint="delete")



# Run the App
if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'mongodb'

    sess.init_app(app)

    app.run(debug=True)