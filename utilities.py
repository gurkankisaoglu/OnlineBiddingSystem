"""
Utility function definitions goes here.
"""

import datetime

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

    def register(self,itemtype,watchmethod):
        if itemtype not in self.callbacks:
            self.callbacks[itemtype] = []
        self.callbacks[itemtype].append(watchmethod)
    
    def notify(self,itemtype,descr):
        # if itemtype is not in the dict it gives key error
        if not itemtype in self.callbacks:
            return
        for method in self.callbacks[itemtype]:
            method(descr)
