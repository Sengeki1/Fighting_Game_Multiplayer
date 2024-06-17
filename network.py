import socket
import pickle

class Network:
    def __init__(self) -> None:
        self.client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = "192.168.1.66"
        self.port_tcp = 5555
        self.port_udp = 5556
        self.tcp_addr = (self.server, self.port_tcp)
        self.udp_addr = (self.server, self.port_udp)
        self.p = self.connect()

    def getP(self):
        return self.p
    
    def connect(self):
        try:
            self.client_tcp.connect(self.tcp_addr)  # Connect to Server
            return pickle.loads(self.client_tcp.recv(1024))  # get Player Position and Color
        except socket.error as e:
            print(f"Error connecting to the server: {e}")
            return None

    def send(self, data):
        try:
            self.client_tcp.send(pickle.dumps(data))
            return pickle.loads(self.client_tcp.recv(1024))
        except socket.error as e:
            print(f"TCP send error: {e}")
            return None
    
    def sendUDP(self, data):
        try:
            self.client_udp.sendto(pickle.dumps(data), self.udp_addr)
            data, _ = self.client_udp.recvfrom(1024)
            return pickle.loads(data)
        except socket.error as e:
            print(f"UDP send error: {e}")
            return None
