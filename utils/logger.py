from utils import utilf as u
import colorama
colorama.init(autoreset=False)

class Logger:
    def __init__(self):
        self.__LOGS__ = ""
    
    def log(self, msg):
        current = u.get_current_time()
        out = f"[{current} | LOG]: {msg}"
        self.__LOGS__ += out + "\n"
        print(out)
    
    def info(self, msg):
        current = u.get_current_time()
        out = f"[{current} | INFO]: {msg}"
        self.__LOGS__ += out + "\n"
        print(colorama.Fore.GREEN + out + colorama.Fore.RESET)
    
    def warning(self, msg):
        current = u.get_current_time()
        out = f"[{current} | WARNING]: {msg}"
        self.__LOGS__ += out + "\n"
        print(colorama.Fore.YELLOW + out + colorama.Fore.RESET)
    
    def fatal(self, msg):
        current = u.get_current_time()
        out = f"[{current} | FATAL]: {msg}"
        self.__LOGS__ += out + "\n"
        print(colorama.Fore.RED + out + colorama.Fore.RESET)
    
    def dump(self, filename="latest.txt"):
        file = open(filename, "w")
        file.write(self.__LOGS__)
        file.close()