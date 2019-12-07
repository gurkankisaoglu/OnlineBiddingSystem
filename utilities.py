"""
Utility function definitions goes here.
"""
import pickle
from socket import *
import datetime
from threading import *
import json
import time

def verf(email):
    with open("verification.json", "r") as f:
        data = json.load(f)
        print(data[email]["number"])
        return data[email]["number"]

def connect(lock):
    with open("port.txt", "r") as f:
        port = int(f.readline())

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('localhost', port))
    Thread(target=handler, args=(lock, sock,)).start()
    return sock

def handler(lock, sock):
    try:
        while 1:
            req = pickle.loads(sock.recv(1000))
            with lock:
                print("sock",req)
    except:
        print("exception")
        return

def dateformatter(timestamp):
    """
        formats timestamp like "dd:MM:YY HH:mm:ss"
    """
    if timestamp is None:
        return None
    return datetime.datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")


def Singleton(cls):
	'''generic python decorator to make any class
	singleton.'''
	_instances = {}	  # keep classname vs. instance
	def getinstance():
		'''if cls is not in _instances create it
		and store. return the stored instance'''
		if cls not in _instances:
			_instances[cls] = cls()
		return _instances[cls]
	return getinstance


@Singleton
class NotificationModule:
    def __init__(self):
        self.callbacks = {}
        self.lock = Lock()
    def register(self,itemtype,watchmethod):
        with self.lock:
            if itemtype not in self.callbacks:
                self.callbacks[itemtype] = []
            if watchmethod in self.callbacks[itemtype]:
                raise Exception("This method already added to callbacks!")
            self.callbacks[itemtype].append(watchmethod)
    
    def notify(self,itemtype,descr):
        # if itemtype is not in the dict it gives key error
        with self.lock:
            if not itemtype in self.callbacks:
                return
            for method in self.callbacks[itemtype]:
                method(descr)
