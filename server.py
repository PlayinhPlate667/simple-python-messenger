# v 1.1.0
import asyncio
import socket
import utils as u

class Server:
    def __init__(self) -> None:
        self.connected = {}
    
    async def listen(self, sessionID):
        usrSock = self.connected[sessionID]["socket"]
        u.info(f"listening {sessionID}")
        while True:
            try:
                data = await self.taskLoop.sock_recv(usrSock, 1024)
                data = data.decode("UTF-8")
                u.log(f"{sessionID} send: {data}")
                usrSock.send("data received".encode("UTF-8"))
            except (ConnectionAbortedError, ConnectionResetError):
                u.info(f"{sessionID} disconnected, close session")
                del self.connected[sessionID]
                return None

    async def accept(self):
        while True:
            usrSock, usrAddr = await self.taskLoop.sock_accept(self.serverSocket)
            sessionID = u.generate_ID(16)
            u.info(f"user connected, session ID : {sessionID}")
            self.connected[sessionID] = {
                "socket" : usrSock,
                "address" : usrAddr
            }
            self.taskLoop.create_task(self.listen(sessionID))

    def start(self, IP, PORT, queueLen, addrFamily=socket.AF_INET, proto=socket.SOCK_STREAM):
        self.serverSocket = socket.socket(addrFamily, proto)
        self.serverSocket.bind((IP, PORT))
        self.serverSocket.listen(queueLen)
        self.taskLoop = asyncio.new_event_loop()
        u.info(f"server started on addr <{IP}|{PORT}>")
        self.taskLoop.run_until_complete(self.accept())

if __name__ == "__main__":
    serv = Server()
    serv.start("127.0.0.1", 8080, 3)