import socket
import threading

HOST = '127.0.0.1' 
PORT = 5555        

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

def broadcast(message, sender_client):
    """Sends a message to all connected clients EXCEPT the sender."""
    for client in clients:
        if client != sender_client:
            try:
                client.send(message)
            except:
                clients.remove(client)

def handle_client(client):
    while True:
        try:
            # 5MB buffer to accommodate base64 file strings
            message = client.recv(1024 * 1024 * 5) 
            if message:
                broadcast(message, client)
        except:
            if client in clients:
                clients.remove(client)
            client.close()
            break

def receive():
    print(f"Server is running and listening on {HOST}:{PORT}...")
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        clients.append(client)
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

# Start the server
receive()