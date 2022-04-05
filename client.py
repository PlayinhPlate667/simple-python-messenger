# v 1.0.0
import socket



# client socket
client = socket.socket(
    socket.AF_INET, # IPv4
    socket.SOCK_STREAM # TCP
)

# set IP and PORT of server
IP = "127.0.0.1"
PORT = 8080

# connection to server
client.connect((IP, PORT))

# main infinity cycle
while True:
    data = input("$:") # input message
    if data=="":data="~<|EMPTY MESSAGE|>~"
    client.send(data.encode("UTF-8")) # set encoding of server
    print(client.recv(1024).decode("UTF-8"))

    if data == "close": # if user input 'close'
        print("close of connection")
        client.close() # close connection
        break