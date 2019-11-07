"""
Utility function definitions goes here.
"""

import datetime

def dateformatter(timestamp):
    """
        formats timestamp like "dd:MM:YY HH:mm:ss"
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")