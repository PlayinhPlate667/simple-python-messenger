import rsa
import pickle

class Cryptor:
    def __init__(self, keylen):
        self.__KEYLEN__ = keylen
        self.__pubkeyGetted__ = False
        self.__PUBLIC__, self.__PRIVATE__ = rsa.newkeys(keylen)

    def get_public_key(self):
        self.__pubkeyGetted__ = True
        return self.__PUBLIC__
    
    def set_public_key(self, public):
        if self.__pubkeyGetted__:
            if isinstance(public, rsa.PublicKey):
                self.__PUBLIC__ = public
            else: raise TypeError("arg 'public' is not rsa.PublicKey")
        else: raise RuntimeError("call 'get_public_key' before this function")
    
    def to_bytes(self, obj):
        return pickle.dumps(obj)
    
    def to_obj(self, b):
        if isinstance(b, bytes):
            return pickle.loads(b)
        else: raise TypeError("arg 'b' is not bytes")
    
    def encrypt(self, msg):
        if isinstance(msg, bytes):
            return rsa.encrypt(msg, self.__PUBLIC__)
        else: raise TypeError("arg 'msg' is not bytes")
    
    def decrypt(self, msg):
        if isinstance(msg, bytes):
            return rsa.decrypt(msg, self.__PRIVATE__)
        else: raise TypeError("arg 'msg' is not bytes")
