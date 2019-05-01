from flask import Flask, request, session, Response, redirect, stream_with_context
from flask_restful import Api, Resource
import docker
import json
import requests
import time
from threading import Lock
from threading import *

#Flask Setup
app = Flask(__name__)
api = Api(app)

globalUrl = "http://3.209.213.217"

def roundRobin():
	global actsList
	try:
		new = actsList[1:]
	except:
		new = []
	new.append(actsList[0])
	actsList = new


@app.route("/")
def server():
    return ""

@app.route("/api/v1/<path:url>",methods=['GET','POST','DELETE'])
def categories(url):
    global globalUrl
    global actsList
    global requestCount
    if(url!="_health" and url!="_crash"):
        requestCount += 1
    if(start == False):
        start = True
        start_time = time.time()
    portNumber = str(actsList[0])
    roundRobin()
    if(request.method == 'GET'):
        print(request.host)
        path = globalUrl+":"+portNumber+"/api/v1/"+url
        print(path)
        return redirect(path)
    elif(request.method == 'POST'):
        path = globalUrl+":"+portNumber+"/api/v1/"+url
        print(path)
        return redirect(path,code=307)
    elif(request.method == 'DELETE'):
        path = globalUrl+":"+portNumber+"/api/v1/"+url
        print(path)
        return redirect(path,code=307)
    return ""

def poll():
   global actsList
   global conDict
   global requestCount
   global lock
   global start
   global start_time
   global globalUrl
   while True:
       if(round(time.time()-start_time)!=120):
           for p in actsList:
               resp = requests.get(globalUrl+":"+str(p)+"/api/v1/_health")
               if(resp.status_code == 500):
                   lock.acquire()
                   index = actsList.index(p)
                   actsList.remove(p)
                   lock.release()
                   client = docker.from_env()
                   reCon = client.containers.get(container_id[str(p)])
                   reCon.kill()
                   newContainer = client.containers.run("acts",detach=True,ports={'80/tcp': p})
                   time.sleep(5)
                   lock.acquire()
                   conDict[str(p)] = newContainer.id
                   try:
                   	actsList.insert(index,p)
                   except:
                   	actsList.append(p)
                   lock.release()
       else:
           container_count =int((requestCount/20)+1)
           extra_container = container_count - len(actsList)
           if(extra_container>0):
               for i in range(0,extra_container):
                   next_available_port = str(max(actsList)+1)
                   client = docker.from_env()
                   scaled_container = client.containers.run("acts",detach=True,ports={'80/tcp': next_available_port})
                   time.sleep(5)
                   conDict[next_available_port] = scaled_container.id
                   lock.acquire()
                   actsList.append(int(next_available_port))
                   lock.release()
               requestCount = 0
               start = True
               start_time = time.time()
           else:
               for i in range(extra_container,0):
                   remove_port = str(max(actsList))
                   client = docker.from_env()
                   del_container = client.containers.get(container_id[str(remove_port)])
                   del_container.kill()
                   time.sleep(5)
                   lock.acquire()
                   actsList.remove(int(remove_port))
                   del conDict[remove_port]
                   lock.release()
               start = True
               requestCount = 0
               start_time = time.time()

if __name__ == "__main__":
    requestCount = 0
    lock = Lock()
    start_time = 0
    start = False
    client = docker.from_env()
    mongo = client.containers.run("mongo",detach=True,ports={'27017/tcp': 27017})
    time.sleep(5)
    container1 = client.containers.run("acts",detach=True,ports={'80/tcp': 8000})
    time.sleep(5)
    actsList = [8000]
    conDict = {'8000':container1.id}
    t = Timer(1.0, poll)
    t.start()
    app.run(debug=True)






