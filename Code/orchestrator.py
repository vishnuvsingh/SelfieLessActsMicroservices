from flask import Flask, redirect, request
import requests
import docker
import time
from threading import *
import json

app = Flask(__name__)

ec2Url = "http://3.209.213.217"
localUrl = "http://localhost"

lock = Lock()

ports = []
idDict = {}
firstExists = False
start = True

requestCount = 0

timeInterval = 0
scaleRequests = 0

def initializeConfig():
	global timeInterval
	global scaleRequests
	info = json.loads(open('defaults.json').read())
	timeInterval = int(info['timeInterval'])
	scaleRequests = int(info['scaleRequests'])

def startInstance(portNo):
	global ports
	global idDict
	global lock
	client = docker.from_env()
	conId = client.containers.run("acts",detach=True,ports={'80/tcp': portNo})
	lock.acquire()
	ports.append(portNo)
	idDict[portNo] = conId.id
	lock.release()

def roundRobin():
	global ports
	try:
		temp = ports[1:]
	except:
		temp = []
	temp.append(ports[0])
	lock.acquire()
	ports = temp
	lock.release()


def startFaultThreads():
	while True:
		time.sleep(1)
		faultThread = Thread(target = faultTolerance) # thread that implements fault tolerance
		faultThread.start()


def faultTolerance():
	global ports
	global localUrl
	global lock
	global idDict
	if(len(ports) != 0):
		for portNo in ports:
			fullUrl = localUrl + ':' + str(portNo) + '/api/v1/_health'
			if(portNo in ports):
				r = requests.get(fullUrl)
				if(r.status_code!=200):
					print(r.text,r.status_code)
					lock.acquire()
					ports.remove(portNo)
					conId = idDict[portNo]
					lock.release()
					client = docker.from_env()
					conDel = client.containers.get(conId)
					print(portNo)
					conDel.kill()
					startInstance(portNo)
					time.sleep(3)
					print('Old Id: ' + conId + ' New Id: ' + idDict[portNo])



def startScaleThreads():
	global timeInterval
	time.sleep(3)
	while True:
		print("Scaling")
		scaleThread = Thread(target = autoScale)
		scaleThread.start()
		#time.sleep(120)
		time.sleep(timeInterval)


def autoScale():

	global requestCount
	temp = requestCount
	requestCount = 0    #resetting count

	global ports
	global idDict
	global scaleRequests

	#containerCount = int(temp/20) + 1
	containerCount = int(temp/scaleRequests) + 1
	if(containerCount>10):
		containerCount = 10
	extraContainers = containerCount - len(ports)
	print(extraContainers)

	if(extraContainers>0):
		for i in range(0,extraContainers):
			portNo = max(ports) + 1
			startInstance(portNo)
			print("New Instance " + str(i) + ": " + idDict[portNo] + " at " + str(portNo))
			print(ports)

	elif(extraContainers<0):
		x = -extraContainers
		for i in range(0,x):
			portNo = max(ports)
			lock.acquire()
			ports.remove(portNo)
			conId = idDict[portNo]
			del idDict[portNo]
			lock.release()
			client = docker.from_env()
			conDel = client.containers.get(conId)
			print(portNo)
			conDel.kill()



@app.route("/api/v1/<path:url>",methods=["GET","POST","DELETE"])
def actsAPI(url):

	global ports
	global ec2Url
	global localUrl
	global threadFaultFun
	global threadScaleFun
	global requestCount
	global firstExists

	if(url!='_health' and url!='_crash'):
		requestCount += 1
		print(requestCount)

	if(len(ports)==0):
		startInstance(8000)
		time.sleep(3)
	#if(not(firstExists)):
		firstExists = True
		threadFaultFun.start()  #start polling
		threadScaleFun.start()

	portNo = ports[0]
	roundRobin()
	#fullUrl = ec2Url + ':' + str(portNo) + '/api/v1/' + url
	fullUrl = localUrl + ':' + str(portNo) + '/api/v1/' + url
	print(fullUrl)
	'''
	if(request.method == 'GET'):
		return redirect(fullUrl)
	elif(request.method == 'POST' or request.method == 'DELETE'):
		return redirect(fullUrl,code=307)
	return ""
	'''
	try:
		temp = request.json
		try:
			temp = dict(request.json)
		except:
			temp = list(request.json)
	except:
		temp = {}
	headers = {"Content-Type": "application/json", "Accept": "application/json"}
	if request.method == "GET":
		r = requests.get(fullUrl, data=json.dumps(temp), headers=headers)
		print(r.text)
	elif request.method == "POST":
		r = requests.post(fullUrl, data=json.dumps(temp), headers=headers)
		print(r.text)
		print(temp)
	else:
		r = requests.delete(fullUrl, data=json.dumps(temp), headers=headers)
		print(r.text)
	return r.text, r.status_code



'''
def startFirst():
	global start
	global threadFaultFun
	if(start):
		startInstance(8000)
		time.sleep(3)
		threadFaultFun.start()  #start polling
		start = False
'''

if __name__ == "__main__":
	initializeConfig()
	#threadStartFirst = Thread(target = startFirst)
	threadFaultFun = Thread(target = startFaultThreads) #thread that makes a new fault torelance thread every 1 second
	threadScaleFun = Thread(target = startScaleThreads)
	#threadStartFirst.start()
	app.debug = False
	app.run(port=80,host='0.0.0.0')





