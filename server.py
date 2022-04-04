# v 1.0.0
import socket

# create server socket
server = socket.socket(
    socket.AF_INET, # IPv4 
    socket.SOCK_STREAM # TCP
)
IP = "127.0.0.1" # localhost
PORT = 8080 # port for connection (use 1025-65000 ports for best working)

server.bind((IP, PORT)) # bind server on address
server.listen(5) # server listening connections (5 - len of queue on connect, not use 1-25 for best working)

# main infinity cycle 
while True:
    usrSock, usrAddr = server.accept() # accept connections
    print(f"connection, IP:{usrAddr[0]} PORT:{usrAddr[1]}")
    
    # infinity cycle for listening connected user
    while True:
        data = usrSock.recv(1024).decode("UTF-8") # receive sended data, 1024 - size of package
        print(f"user send : {data}")

        if data == "close": # if user send 'close' message
            print("user break connection")
            usrSock.close() # close connection
            break # end of listening user