# v 1.3.0
from utils.configmanager import ConfigManager, FROM_CONFIG
from utils.cryptor import Cryptor
from utils.logger import Logger
import asyncio
import socket
import utils.utils as u

class Server:
    def __init__(self) -> None:
        self.connected = {}
        self.logger = Logger()
        self.config = ConfigManager("conf.txt")
    
    def add_user_to_list(self, ID, sock, addr):
        self.connected[ID] = {
            "socket" : sock, "address" : addr, "cryptor" : None
        }

    def delete_user_from_list(self, ID):
        if ID in self.connected.keys(): del self.connected[ID]

    def sendall(self, msg):
        for key in self.connected.keys():
            usrCryptor = self.connected[key]["cryptor"]
            usrSocket = self.connected[key]["socket"]
            if isinstance(usrCryptor, Cryptor) and isinstance(usrSocket, socket.socket):
                sendMsg = usrCryptor.encrypt(usrCryptor.to_bytes(msg))
                usrSocket.send(sendMsg)
            

    async def save(self, timeout=FROM_CONFIG):
        if timeout==FROM_CONFIG: timeout=float(self.config.get("SAVE TIMEOUT"))
        while True:
            await asyncio.sleep(timeout)
            self.logger.info("save logs")
            self.logger.dump("latest.txt")

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

                    self.logger.log(f"{sessionID} send: {data}")
                    message = f"[{sessionID}]: {data}"
                    self.sendall(message)

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