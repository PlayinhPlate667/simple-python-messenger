import utils.utilf as u
import pickle

LVL_ACCESS_USER = b"USER ACCESS LEVEL"
LVL_ACCESS_ADMIN = b"ADMINISTRATOR ACCESS LEVEL"
LVL_ACCESS_CREATOR = b"CREATOR ACCESS LEVEL"

class User:
    def __init__(self, name, password, accessLevel, groupName="all") -> None:
        self.name = name
        self.password = password
        self.accessLevel = accessLevel
        self.groupName = groupName


def to_bytes(obj): return pickle.dumps(obj)
def to_obj(b:bytes): return pickle.loads(b)

def join_list(l: list, s=""):
    result = ""
    for i in l: result += i + s if isinstance(i, str) else ""
    return result


class UserDataManager:
    def __init__(self, startpath:str):
        self.dataPath = join_list(startpath.split("\\")[:-1:], "\\")+"users\\"
        
    def get_user_data(self, userName:str):
        file = open(self.dataPath+userName+".dat", "rb")
        user = to_obj(file.read())
        if isinstance(user, User): return (user, True)
        else: return (user, False)
    
    def set_user_data(self, user:User):
        file = open(self.dataPath+user.name+".dat", "wb")
        file.write(to_bytes(user))
        file.close()
    
    def get_users_list(self):
        pathList = u.get_files(self.dataPath)
        result = []
        for p in pathList: result.append(p.split("\\")[-1].split(".")[0])
        return result