import socket
import threading

# Server configuration
HOST = '127.0.0.1' 
PORT = 5555        

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

def broadcast(message, sender_client):
    """Sends a message to all connected clients EXCEPT the sender."""
    for client in clients:
        if client != sender_client: # Prevent echoing back to the sender
            try:
                client.send(message)
            except:
                clients.remove(client)

def handle_client(client):
    """Listens for messages from a specific client."""
    while True:
        try:
            message = client.recv(1024)
            broadcast(message, client) # Pass the client so we know who sent it
        except:
            if client in clients:
                clients.remove(client)
            client.close()
            break

def receive():
    """Accepts new connections continuously."""
    print(f"Server is running and listening on {HOST}:{PORT}...")
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        
        clients.append(client)
        
        # Start a new thread to handle this specific client
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

# Start the server
receive()