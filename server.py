from _thread import start_new_thread
import socket
import pickle
import pygame as pg
from player import Player
import threading

# Initialize Pygame
pg.init()
pg.display.set_mode((800, 600))  # Adjust the size as needed

server = "192.168.1.65"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection, Server Started")

clients = []
players = [Player((700, 834), "Character 1"), Player((1100, 854), "Character 2")]

# Condition variable to synchronize clients
condition = threading.Condition()
connected_clients = 0
currentPlayer = 0

def threaded_client(conn, player):
    global connected_clients
    global currentPlayer
    with condition:
        connected_clients += 1
        if connected_clients < 2:
            print(f"Client {player} waiting for another player...")
            condition.wait()  # Wait until the second client connects
        else:
            condition.notify_all()  # Notify the waiting client

    conn.send(pickle.dumps({"player_data": players[player].get_data(), "message": "START"}))

    while True:
        try:
            data = pickle.loads(conn.recv(4096))  # Increase buffer size to 4096
            players[player].update_data(data)  # Update the player's data

            if not data:
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = players[0].get_data()  # Send player 0's data to player 1
                else:
                    reply = players[1].get_data()  # Send player 1's data to player 0

                print(f"Player {player} received: {data}")
                print(f"Player {player} sending: {reply}")

            conn.sendall(pickle.dumps(reply))
        except Exception as e:
            print(f"Error during communication with player {player}: {e}")
            break

    print(f"Player {player} lost connection")
    conn.close()
    with condition:
        connected_clients -= 1
        if currentPlayer > 0:
            currentPlayer -= 1
        else:
            currentPlayer = 0

print("[STARTING] server is starting...")
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    clients.append(conn)
    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
