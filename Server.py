import struct
import colorama
from scapy.all import get_if_addr
import configuration
import random
from socket import *
import time
import threading
from StoppableThread import StoppableThread


def generate_math_exercise():
    number1 = random.randint(2, 5)
    number2 = random.randint(1, number1-1)
    operator = random.choice(["+", "-"])
    if operator == "+":
        result = number1 + number2
    else:
        result = number1 - number2

    math_ex = f"{number1} {operator} {number2}"
    return math_ex, result


class Server:

    def _init_(self):
        self.first_client = None
        self.second_client = None
        self.port_number = configuration.SERVER_PORT
        self.host_name = get_if_addr('eth1') # when we test it, we will convert it to 'eth2'
        self.UDP_port = configuration.DESTINATION_PORT
        self.free_flags = [True, True]
        self.mutex = threading.Lock()

        # server message
        colorama.init()
        message = f"{colorama.Fore.GREEN}Server started, listening on IP address {self.host_name}"
        print(message)
        self.server_socket = socket()
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(('', self.port_number))
        self.server_socket.listen(2)

    def UDP_broadcast(self):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        udp_message = struct.pack('IBH', configuration.MAGIC_COOKIE, configuration.MESSAGE_TYPE, self.port_number)
        while not (self.first_client and self.second_client):
            udp_socket.sendto(udp_message, ('<broadcast>', self.UDP_port))
            time.sleep(1)

        udp_socket.close()  # when udp founds two clients

    def TCP_connection(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('127.0.0.1', self.port_number))
        server_socket.listen(2)

        def worker(socket):
            while any(self.free_flags):
                client_socket, address = socket.accept()  # conn is socket for the specific client
                if self.first_client is None:
                    self.first_client = (client_socket, address)
                    self.free_flags[0] = False

                else:
                    self.second_client = (client_socket, address)
                    self.free_flags[1] = False

        thread = threading.Thread(target=worker, args=(self.server_socket,))
        thread.start()

    def clients_exe_answer(self, first_client_name, second_client_name):

        answer = [None, None]

        def worker(player_name, client_socket):
            client_answer = None
            try:
                # gets the answer from the client, if exists
                client_answer = client_socket.recv(1).decode()
                if client_answer is not None:
                    answer[0] = client_answer
                    answer[1] = player_name
            except Exception as e:
                print(e)

        t0 = StoppableThread(target=worker, args=(first_client_name, self.first_client[0]))
        t1 = StoppableThread(target=worker, args=(second_client_name, self.second_client[0]))
        # run threads
        t0.start()
        t1.start()
        finish_time = time.time() + 10

        while time.time() < finish_time:
            time.sleep(0.000001)
            if answer[0] is not None:
                t0.StopThread()
                t1.StopThread()
                return answer

        t0.StopThread()
        t1.StopThread()



server = Server()

while True:
    try:
        server.TCP_connection()
        server.UDP_broadcast()
        # game process
        first_client_name = server.first_client[0].recv(1024).decode()  # decode bytes to receive string
        second_client_name = server.second_client[0].recv(1024).decode()

        math_question, result = generate_math_exercise()
        welcome_message = \
            f"""
                Welcome to Quick Maths.
                Player 1: {first_client_name}
                Player 2: {second_client_name}
                ==
                Please answer the following question as fast as you can:
                How much is {math_question}?
                """
        server.first_client[0].send(welcome_message.encode())  # sent to client the message encoded from string to bits
        server.second_client[0].send(welcome_message.encode())

        answer = server.clients_exe_answer(first_client_name, second_client_name)
        end_draw_message = f"""Game over!
                The correct answer was {result}!
                Game finished with a DRAW!
                """
        if not answer:
            # send draw message
            server.first_client[0].send(end_draw_message.encode())
            server.second_client[0].send(end_draw_message.encode())
            # return

        try:
            math_answer, first_to_answer = answer

        except:
            first_to_answer = ""
            math_answer = -1

        if math_answer == result:
            winner_player = first_to_answer
        elif first_to_answer == first_client_name:
            winner_player = second_client_name
        else:
            winner_player = first_to_answer

        end_win_message = f"""Game over!
                    The correct answer was {result}!
                    Congratulations to the winner: {winner_player}
                    """

        server.first_client[0].send(end_win_message.encode())
        server.second_client[0].send(end_win_message.encode())

        server.first_client = None
        server.second_client = None
        print(f"Game over, sending out offer requests...")
    except Exception as e:
        print(e)