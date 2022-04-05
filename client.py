# v 1.1.0
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
    
    def connect(self, IP, PORT) -> bool:
        try:
            self.clientSocket.connect((IP, PORT))
            return True
        except ConnectionRefusedError:
            return False

    def main(self):
        self.taskLoop = asyncio.new_event_loop()
        self.taskLoop.create_task(self.send_data())
        self.taskLoop.run_until_complete(self.listen_server())

    async def listen_server(self):
        while True:
            data = await self.taskLoop.sock_recv(self.clientSocket, 1024)
            data = data.decode("UTF-8")
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
            self.clientSocket.send(data.encode("UTF-8"))

if __name__ == "__main__":
    client = Client()
    client.connect("127.0.0.1", 8080)
    client.main()