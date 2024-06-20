from _thread import start_new_thread
import socket
import pickle

class DatabaseConn():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.5.179"
        self.port = 4000
        self.addr = (self.server, self.port)
        self.client.connect(self.addr)

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(1024))
        except:
            pass  
