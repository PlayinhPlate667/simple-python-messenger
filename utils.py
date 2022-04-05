from colorama import Fore
import datetime
import random
import os

SYMBOLS = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890"

def get_current_time(): return datetime.datetime.now()

def generate_ID(IDlen:int):
    ID = ""
    for _ in range(IDlen): ID += SYMBOLS[random.randint(0, len(SYMBOLS)-1)]
    return ID

# returns the directory, from which the script was launched
def getCurrentDir():
    return os.path.dirname(os.path.realpath(__file__))

# return directories in dir
def getDirs(rootDirectory): 
    return [f for f in os.listdir(rootDirectory) if os.path.isdir(os.path.join(rootDirectory, f))]

# return files in dir
def getFiles(rootDirectory):
    return [f for f in os.listdir(rootDirectory) if os.path.isfile(os.path.join(rootDirectory, f))]
