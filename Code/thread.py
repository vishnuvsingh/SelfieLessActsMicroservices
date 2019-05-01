from threading import *
import time

def fun():
	while True:
		time.sleep(2)
		threadFun = Thread(target = fun2)
		threadFun.start()

def fun2():
	print('hi')
	time.sleep(2)

def st():
	global thread
	thread.start()

if __name__ == '__main__':
	thread = Thread(target = fun)
	st()
	while True:
		print('Hello')
		time.sleep(10)
