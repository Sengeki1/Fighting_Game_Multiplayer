from _thread import start_new_thread
import socket
import pickle
import pygame as pg
from player import Player
import threading
import time
import psutil  # Import psutil for setting CPU affinity

# Initialize Pygame
pg.init()
pg.display.set_mode((800, 600))  # Adjust the size as needed

server = "192.168.1.64"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection, Server Started")

clients = []
players = [Player((700, 854), "Character 1"), Player((1100, 854), "Character 2")]

# Condition variable to synchronize clients and timer
condition = threading.Condition()
connected_clients = 0
currentPlayer = 0

# Timer flag and thread
timer_thread = None
timer_running = False

def countdown_timer(duration):
    global timer_running
    try:
        while duration > 0:
            with condition:
                if not timer_running:
                    break
                for conn in clients:
                    try:
                        conn.sendall(pickle.dumps({"start_timer": duration}))
                    except Exception as e:
                        print(f"Error sending timer: {e}")
            duration -= 1
            time.sleep(0.02)
        # Notify clients that the timer has ended
        with condition:
            if timer_running:
                for conn in clients:
                    try:
                        conn.sendall(pickle.dumps({"start_timer": 0, "lose": False}))
                    except Exception as e:
                        print(f"Error sending timer end notification: {e}")
    finally:
        timer_running = False

def start_timer(duration):
    global timer_thread, timer_running
    with condition:
        if not timer_running:
            timer_running = True
            timer_thread = threading.Thread(target=countdown_timer, args=(duration,))
            timer_thread.start()

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
            data = pickle.loads(conn.recv(1024))  # Increased buffer size
            if "timer" in data:
                start_timer(100)

            if "timer" not in data:
                players[player].update_data(data)  # Update the player's data

                if not data:
                    print("Disconnected")
                    break
                else:
                    if player == 1:
                        reply = players[0].get_data()  # Send player 0's data to player 1
                    else:
                        reply = players[1].get_data()  # Send player 1's data to player 0

                    print(reply)

                    conn.sendall(pickle.dumps(reply))             
        except Exception as e:
            print(f"Error during communication with player {player}: {e}")
            break

    print(f"Player {player} lost connection")
    conn.close()
    with condition:
        connected_clients -= 1
        clients.remove(conn)
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
