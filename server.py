# v 1.2.0
from configmanager import ConfigManager, FROM_CONFIG
from logger import Logger
import asyncio
import socket
import utils as u

class Server:
    def __init__(self) -> None:
        self.connected = {}
        self.logger = Logger()
        self.config = ConfigManager("conf.txt")
    
    def add_user_to_list(self, ID, sock, addr):
        self.connected[ID] = {
            "socket" : sock, "address" : addr
        }

    def delete_user_from_list(self, ID):
        if ID in self.connected.keys(): del self.connected[ID]

    async def save(self, timeout=FROM_CONFIG):
        if timeout==FROM_CONFIG: timeout=float(self.config.get("SAVE TIMEOUT"))
        while True:
            await asyncio.sleep(timeout)
            self.logger.info("save logs")
            self.logger.dump("latest.txt")

    async def listen(self, sessionID):
        usrSock = self.connected[sessionID]["socket"]
        if isinstance(usrSock, socket.socket): # if user socket bad saved, server not stopping
            self.logger.info(f"listening {sessionID}")
            while True:
                try:
                    data = await self.taskLoop.sock_recv(usrSock, 1024)
                    data = data.decode("UTF-8")

                    self.logger.log(f"{sessionID} send: {data}")
                    usrSock.send("data received".encode("UTF-8"))

                except (ConnectionAbortedError, ConnectionResetError):
                    self.logger.info(f"{sessionID} disconnected, close session")
                    self.delete_user_from_list(sessionID)
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
            sessionID = u.generate_ID(16)
            self.logger.info(f"user connected, session ID : {sessionID}")

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
        self.logger.info("server stopped")
        self.logger.dump("logs.txt")


if __name__ == "__main__":
    serv = Server()
    serv.start()