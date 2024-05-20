from _thread import *
import socket
import pickle
import pygame as pg
from player import Player

# Initialize Pygame
pg.init()
pg.display.set_mode((800, 600))  # Adjust the size as needed

server = "192.168.1.68"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

clients = []
players = [Player((700, 834), "Character 1"), Player((1100, 854), "Character 2")]

def threaded_client(conn, player): # given the player
    conn.send(pickle.dumps(players[player].get_data())) # send the player the compress data object information
    reply = ""
    while True:
        try:
            # Receive and deserialize data from the client
            data = pickle.loads(conn.recv(1024))
            players[player].update_data(data) # Update the player's data
            if not data:
                print("Disconnected")
                break
            else:
                # Determine the reply data based on the current player
                if player == 1:
                    reply = players[0].get_data() # Send player 0's data to player 1
                else:
                    reply = players[1].get_data() # Send player 1's data to player 0

                print("Received: ", data)
                print("Sending: ", reply)

            # Send the reply data back to the client
            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0
print("[STARTING] server is starting...")
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    clients.append(conn)
    start_new_thread(threaded_client,(conn, currentPlayer))
    currentPlayer += 1

for client in clients:
    client.send(pickle.dumps({'message': 'START'}))


