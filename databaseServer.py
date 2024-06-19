from _thread import start_new_thread
import socket
import pickle
import requests

server = "192.168.1.69"
port = 3030

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen()
print("Waiting for a connection, Server Started")

def send_login_request(username, password):
    url = "http://localhost:8000/login"  # Replace with your server's address and port
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None

def threaded_client(conn):
    while True:
        try:
            data = pickle.loads(conn.recv(1024))

            if "stop" in data:
                break
            
            username = data["username"]
            password = data["password"]
            if username and password:
                response = send_login_request(username, password)
                print(f"Response from login route: {response}")
                conn.send(pickle.dumps(response))
                       
        except Exception as e:
            print(f"Error during communication with player: {e}")
            break

    print(f"Player lost connection")
    conn.close()

print("[STARTING] server is starting...")
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn,))