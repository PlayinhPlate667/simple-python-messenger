import datetime
import random
import os

SYMBOLS = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890"

def get_current_time(): return datetime.datetime.now()

def join_list(l: list, s=""):
    result = ""
    for i in l: result += i + s if isinstance(i, str) else ""
    return result

def generate_ID(IDlen:int):
    ID = ""
    for _ in range(IDlen): ID += SYMBOLS[random.randint(0, len(SYMBOLS)-1)]
    return ID

# returns the directory, from which the script was launched
def get_current_dir():
    return os.path.dirname(os.path.realpath(__file__))

# return directories in dir
def get_dirs(rootDirectory): 
    return [f for f in os.listdir(rootDirectory) if os.path.isdir(os.path.join(rootDirectory, f))]

# return files in dir
def get_files(rootDirectory):
    return [f for f in os.listdir(rootDirectory) if os.path.isfile(os.path.join(rootDirectory, f))]
