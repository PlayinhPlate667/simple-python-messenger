class GetConfigError(Exception): pass
class ParseConfigError(Exception): pass

FROM_CONFIG = 0b01100111 # 1 byte used

class ConfigManager:
    def prepare_string(self, string:str):
        if string[0]==" ": string=string[1::]
        if string[-1]==" ": del string[-1]
        return string

    def __init__(self, confPath="conf.txt") -> None:
        self.__CONFIG__ = {}

        file = open(confPath, "r")
        data = file.read()
        file.close()
        
        data = data.split("\n")
        for line in data:
            l = line.split(":")
            if len(l) == 2: 
                if l[0] in self.__CONFIG__.keys(): raise ParseConfigError(f"key '{l[0]}' defined a second time")
                else: self.__CONFIG__[l[0]] = self.prepare_string(l[1])
    
    def get(self, key:str) -> str:
        if key in self.__CONFIG__.keys(): return self.__CONFIG__[key]
        else: raise GetConfigError(f"key '{key}' undefined in this config")
