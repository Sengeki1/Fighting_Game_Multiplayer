from _thread import start_new_thread
import socket
import pickle
import pygame as pg
from player import Player
import threading
import time

# Initialize Pygame
pg.init()
pg.display.set_mode((800, 600))

server = "192.168.1.66"
tcp_port = 5555
udp_port = 5556

# TCP socket for connection
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((server, tcp_port))
tcp_socket.listen(2)

# UDP socket for data
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((server, udp_port))

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
                for addr in clients:
                    try:
                        udp_socket.sendto(pickle.dumps({"start_timer": duration, "stopMoving": True}), addr)
                    except Exception as e:
                        print(f"Error sending timer: {e}")
            duration -= 1
            time.sleep(1)  # Changed to 1 second for a real countdown
        # Notify clients that the timer has ended
        with condition:
            if timer_running:
                for addr in clients:
                    try:
                        udp_socket.sendto(pickle.dumps({"start_timer": 0, "stopMoving": False}), addr)
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

def threaded_client(conn, address, player):
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
            data, addr = udp_socket.recvfrom(1024)
            data = pickle.loads(data)
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
                    udp_socket.sendto(pickle.dumps(reply), addr)
        except Exception as e:
            print(f"Error during communication with player {player}: {e}")
            break

    print(f"Player {player} lost connection")
    with condition:
        connected_clients -= 1
        clients.remove(addr)
        if currentPlayer > 0:
            currentPlayer -= 1
        else:
            currentPlayer = 0

print("[STARTING] server is starting...")
while True:
    conn, addr = tcp_socket.accept()
    print("Connected to:", addr)

    if addr not in clients:
        clients.append(addr)
        start_new_thread(threaded_client, (conn, addr, currentPlayer))
        currentPlayer += 1
