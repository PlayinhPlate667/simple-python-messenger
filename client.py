# v 1.3.0
from utils.cryptor import Cryptor
import asyncio
import socket
import os, sys

class Client:
    def __init__(self, messagesBUfferSize=256, addrFamily=socket.AF_INET, proto=socket.SOCK_STREAM) -> None:
        self.clientSocket = socket.socket(
            addrFamily, proto
        )
        self.messages = ""
        self.msgBuffSize = messagesBUfferSize
        self.cryptor = Cryptor(1024)
    
    def connect(self, IP, PORT) -> bool:
        try:
            self.clientSocket.connect((IP, PORT))
            print("SETUP SAFE CONNECTION")
            self.clientSocket.send(self.cryptor.to_bytes(self.cryptor.get_public_key()))
            self.cryptor.set_public_key(self.cryptor.to_obj(self.clientSocket.recv(1024)))
            print("CONNECTION SETUPED")
            return True
        except ConnectionRefusedError:
            return False

    def main(self):
        self.taskLoop = asyncio.new_event_loop()
        self.taskLoop.create_task(self.send_data())
        self.taskLoop.run_until_complete(self.listen_server())

    async def listen_server(self):
        while True:
            # receive data
            data = await self.taskLoop.sock_recv(self.clientSocket, 1024)
            data = self.cryptor.to_obj(self.cryptor.decrypt(data))
            self.messages += data + "\n"
            
            # clear console
            if sys.platform == 'win32': os.system("cls")
            else: os.system("clear")

            print(self.messages)
            # clear messages history if this needed
            if len(self.messages) > self.msgBuffSize: self.messages = ""

    async def send_data(self):
        while True:
            data = await self.taskLoop.run_in_executor(None, input, "input~$: ")
            self.clientSocket.send(self.cryptor.encrypt(self.cryptor.to_bytes(data)))

if __name__ == "__main__":
    client = Client()
    client.connect("127.0.0.1", 8080)
    client.main()