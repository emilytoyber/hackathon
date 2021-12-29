import StoppableThread
import configuration
from socket import *
import colorama
from scapy.arch import get_if_addr
import struct


def reader(conn):
    try:
        message = input()
        conn.send(message.encode())# send client answer
    except:
        print('time out!')


class Client:

    def _init_(self):
        self.UDP_port = configuration.DESTINATION_PORT
        self.port_number = 2346 #configuration.CLIENT_PORT
        self.server_port = configuration.SERVER_PORT
        self.TCP_socket = None
        self.name = configuration.CLIENT_NAME

    def server_connection(self, address, port):
        print(f"Received offer from {address}, attempting to connect...")
        self.TCP_socket = socket(AF_INET, SOCK_STREAM)
        # self.TCP_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            self.TCP_socket.connect((address, port))
        except:
            return None
        return self.TCP_socket


client = Client()
while True:
    # client looking for offers
    colorama.init()
    message = f"{colorama.Fore.BLUE} Client started, listening for offer requests..."
    print(message)
    client.client_UDP = socket(AF_INET, SOCK_DGRAM)
    client.client_UDP.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    client.client_UDP.bind(('', client.UDP_port))
    # connection to server
    
    try:
        data, address = client.client_UDP.recvfrom(1024)
        data = struct.unpack("IBH", data)
        
        if data[0] == configuration.MAGIC_COOKIE and data[1] == configuration.MESSAGE_TYPE:
            #print(type(address[0]), type(data[2]))
            conn = client.server_connection(address[0], data[2])
            print(conn)
        print("before amit kaka")
        if not conn:
           continue
        print("Connected!!!")
        # game process
        conn.send(client.name.encode())
        question = conn.recv(1024).decode()  # receive response
        print(question)
        thread = StoppableThread.StoppableThread(target=reader, args=(conn,))
        try:
            thread.start()
        except:
            print("no answer from client!")
        server_response = conn.recv(1024).decode()  # receive response
        thread.StopThread()
        print(server_response)

        print(f"{colorama.Fore.CYAN}{colorama.Style.BRIGHT}Server disconnected, listening for offer requests...")

    except Exception as e:
        print(f"Error occurred: {e}")