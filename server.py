# v 1.4.2 - not stable, latest
from utils.usersdatamanager import LVL_ACCESS_ADMIN, LVL_ACCESS_CREATOR, LVL_ACCESS_USER, UserDataManager, User
from utils.configmanager import ConfigManager, FROM_CONFIG
from utils.cryptor import Cryptor
from utils.logger import Logger, colorama
import asyncio
import socket
import utils.utilf as u

class Server:
    def __init__(self) -> None:
        self.connected = {}
        self.logger = Logger()
        self.config = ConfigManager(confPath="conf.txt")
        self.__LAUNCH_DIR__ = u.get_current_dir()
        self.usrDataManager = UserDataManager(startpath=u.get_current_dir())

    def add_user_to_list(self, ID, sock, addr):
        self.connected[ID] = {
            "socket" : sock, "address" : addr, "cryptor" : None,
            "name" : ID, "isReg":False, "access":LVL_ACCESS_USER, "group":"all"
        }

    def delete_user_from_list(self, ID):
        if ID in self.connected.keys(): del self.connected[ID]

    def sendall(self, msg):
        for key in self.connected.keys():
            self.send(key, msg)

    def sendgroup(self, groupName:str, msg:str):
        for key in self.connected.keys():
            if self.connected[key]["group"] == groupName:
                self.send(key, msg)

    def search_user(self, name:str):
        for key in self.connected.keys():
            if self.connected[key]["name"] == name: return key
        else: return False

    def send(self, ID, msg):
        usrCryptor = self.connected[ID]["cryptor"]
        usrSocket = self.connected[ID]["socket"]
        if isinstance(usrCryptor, Cryptor) and isinstance(usrSocket, socket.socket):
            sendMsg = usrCryptor.encrypt(usrCryptor.to_bytes(msg))
            usrSocket.send(sendMsg)

    async def save(self, timeout=FROM_CONFIG):
        if timeout==FROM_CONFIG: timeout=float(self.config.get("SAVE TIMEOUT"))
        while True:
            await asyncio.sleep(timeout)
            self.logger.info("save logs")
            self.logger.dump("latest.txt")

    def terminal(self, ID:str, msg:str):
        retMsg = msg
        cmd = msg.split(" ")
        name = self.connected[ID]["name"]
        if "/" in cmd[0]:
            # register command for users
            if cmd[0] == "/reg":
                #if user with this name registered in base
                if cmd[1] in self.usrDataManager.get_users_list():
                    self.logger.warning(f"user {name} tryed register account {cmd[1]} second time")
                # if user has been registered
                if self.connected[ID]["isReg"]:
                    self.send(ID, colorama.Fore.RED+f"you are registered"+colorama.Fore.RESET)
                    self.logger.warning(f"{name} trying registered second time")
                # if cmd '/reg' bad-structured
                if len(cmd) != 3:
                    self.send(ID, colorama.Fore.RED+f"unparsing command structure. use '/reg <name> <password>' structure for register"+colorama.Fore.RESET)
                    self.logger.warning(f"entered bad-struct cmd '/reg': {retMsg}")
                    return False

                if "." in cmd[1]:
                    self.send(ID, colorama.Fore.RED+f"expected '.' in name, you are not registered"+colorama.Fore.RESET)
                    return False
                user = User(cmd[1], cmd[2], LVL_ACCESS_USER, "all")
                self.connected[ID]["name"] = user.name
                self.connected[ID]["isReg"] = True
                self.connected[ID]["group"] = user.groupName
                self.usrDataManager.set_user_data(user)
                self.send(ID,  colorama.Fore.GREEN+f"you are sucsess registered as {cmd[1]}"+colorama.Fore.RESET)
                return True
            # login command for registered users
            if cmd[0] == "/login":
                # if cmd '/login' bad-structured
                if len(cmd) != 3:
                    self.send(ID, colorama.Fore.RED+f"unparsing command structure. use '/login <name> <password>' structure for logining"+colorama.Fore.RESET)
                    self.logger.warning(f"entered bad-struct cmd '/login': {retMsg}")
                    return False

                nameList = self.usrDataManager.get_users_list()
                # if user has been registered
                if cmd[1] in nameList:
                    user, _ = self.usrDataManager.get_user_data(cmd[1])
                    # if user bad saved
                    if not _:
                        self.logger.warning(f"{ID} tryed login in bad-saved user account {cmd[1]}.dat")
                        self.send(colorama.Fore.RED+f"this account data bad-saved"+colorama.Fore.RESET)
                        return False
                    
                    # if password True
                    if cmd[2] == user.password:
                        self.connected[ID]["name"] = user.name
                        self.connected[ID]["isReg"] = True
                        self.connected[ID]["access"] = user.accessLevel
                        self.connected[ID]["group"] = user.groupName
                        self.logger.info(f"{ID} sucsess logined at {user.name}")
                        self.send(ID, colorama.Fore.GREEN+f"you are sucsess logined at {user.name}"+colorama.Fore.RESET)
                        return True
                    else: # if password False
                        self.logger.info(f"{ID} tryed login at {user.name}, but not input True password")
                        self.send(ID, colorama.Fore.YELLOW+f"password isn't True"+colorama.Fore.RESET)
                        return False
                else: # if user with this name not registered
                    self.logger.info(f"{ID} tryed login at not-founded user: {cmd[1]}")
                    self.send(ID, colorama.Fore.YELLOW+f"user not founded"+colorama.Fore.RESET)
                    return False
            
            if cmd[0] == "/msg":
                # if cmd '/msg' bad-structured
                if len(cmd) < 3:
                    self.send(ID, colorama.Fore.RED+f"unparsing command structure. use '/msg <handler_name> *<message text>' structure for send private message"+colorama.Fore.RESET)
                    self.logger.warning(f"entered bad-struct cmd '/msg': {retMsg}")
                    return False

                # search user in connection users
                for key in self.connected.keys():
                    if self.connected[key]["name"] == cmd[1]:
                        sendMsg = u.join_list(cmd[2::], " ")
                        self.send(key, colorama.Fore.MAGENTA+f"$[{name}->this]: {sendMsg}"+colorama.Fore.RESET)
                        self.send(ID, colorama.Fore.MAGENTA+f"$[this->{cmd[1]}]: {sendMsg}"+colorama.Fore.RESET)
                        self.logger.log(f"user {name}, {ID} send private message to {cmd[1]}, {key}")
                        return True
                # if user net searched
                else: 
                    if cmd[1] in self.usrDataManager.get_users_list():
                        self.logger.warning(f"user {name}, {ID} trying send private message to user {cmd[1]}, but user offline")
                        self.send(ID, colorama.Fore.YELLOW+f"user {cmd[1]} offline"+colorama.Fore.RESET)
                        return False
                    else:
                        self.logger.warning(f"user {name}, {ID} trying send private message to user {cmd[1]}, but user with this name not registered in base")
                        self.send(ID, colorama.Fore.RED+f"user {cmd[1]} not registered"+colorama.Fore.RESET)
                        return False

            # control of groups
            if cmd[0] == "/group":
                # if user have ADMIN or CREATOR access level
                if self.connected[ID]["access"] in (LVL_ACCESS_ADMIN, LVL_ACCESS_CREATOR): 
                    if cmd[1] == "set":
                        if cmd[4] in self.usrDataManager.get_users_list():
                            user, _ = self.usrDataManager.get_user_data(cmd[4])
                            if _: 
                                user.groupName = cmd[3]
                                key = self.search_user(user.name)
                                self.connected[key]["group"] == cmd[3]
                                self.logger.info(f"{name} set group of user({cmd[4]}) to {cmd[3]}")
                                self.send(ID, colorama.Fore.GREEN+"group setted sucsess"+colorama.Fore.RESET)
                                return True
                            else:
                                self.logger.warning(f"searched bad-saved account : {cmd[4]}.dat")
                                self.send(ID, "user data bad-saved, cmd not executed")
                                return False
                else:
                    self.logger.warning(f"user {name} tryed work with cmd '/group', but he not accesed to this cmd")
                    self.send(ID, colorama.Fore.RED+"you haven't access to this command")
                    return False
        else: 
            self.sendall(f"[{name}]: {retMsg}")
            self.logger.log(f"ID:{ID} send message '{msg}'")

    async def listen(self, sessionID):
        usrSock = self.connected[sessionID]["socket"]
        if isinstance(usrSock, socket.socket): # if user socket bad saved, server not stopping
            self.logger.info(f"try setup connection with ID : {sessionID}")
            sessionCryptor = Cryptor(int(self.config.get("KEY LEN")))
            pubKey = sessionCryptor.get_public_key()
            
            # try setup safe-channel with crypting messages  
            while True:
                data = await self.taskLoop.sock_recv(usrSock, 1024)
                try:
                    sessionCryptor.set_public_key(sessionCryptor.to_obj(data))
                    usrSock.send(sessionCryptor.to_bytes(pubKey))
                    break
                except TypeError:
                    self.logger.warning(f"ID:{sessionID} send not public key")

            self.connected[sessionID]["cryptor"] = sessionCryptor
            self.logger.info(f"safe-channel setuped, listening {sessionID}")
            
            while True:
                try:
                    data = await self.taskLoop.sock_recv(usrSock, 1024)
                    data = sessionCryptor.decrypt(data)
                    data = sessionCryptor.to_obj(data)

                    self.terminal(sessionID, data)

                except (ConnectionAbortedError, ConnectionResetError):
                    self.logger.info(f"{sessionID} disconnected, close session")
                    self.delete_user_from_list(sessionID)
                    self.sendall(f"{sessionID} disconnected")
                    return None
        else: 
            self.logger.warning(f"bad-saved socket, user ID : {sessionID}")
            self.delete_user_from_list(sessionID)

    async def accept(self):
        # preparing for work...
        self.taskLoop.create_task(self.save(FROM_CONFIG))

        # main server cycle
        while True:
            usrSock, usrAddr = await self.taskLoop.sock_accept(self.serverSocket)
            sessionID = u.generate_ID(int(self.config.get("ID LEN")))
            self.logger.info(f"user connected, session ID : {sessionID}")
            self.sendall(f"{sessionID} connected")

            self.add_user_to_list(sessionID, usrSock, usrAddr)
            self.taskLoop.create_task(self.listen(sessionID))

    def start(self, IP=FROM_CONFIG, PORT=FROM_CONFIG, queueLen=FROM_CONFIG, addrFamily=socket.AF_INET, proto=socket.SOCK_STREAM):
        self.serverSocket = socket.socket(addrFamily, proto)

        if IP==FROM_CONFIG: IP = self.config.get("IP")
        if PORT==FROM_CONFIG: PORT = int(self.config.get("PORT"))
        self.serverSocket.bind((IP, PORT))

        if queueLen==FROM_CONFIG: queueLen = int(self.config.get("QUEUE LEN"))
        self.serverSocket.listen(queueLen)

        self.taskLoop = asyncio.new_event_loop()
        self.logger.info(f"server started on addr <{IP}|{PORT}> with queue len: {queueLen}")
        self.taskLoop.run_until_complete(self.accept())
    
    def __del__(self):
        self.logger.info("server object deleted")
        self.logger.dump("logs.txt")


if __name__ == "__main__":
    serv = Server()
    serv.start()