import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

# --- SERVER CONNECTION ---
HOST = '127.0.0.1'
PORT = 5555
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
except:
    messagebox.showerror("Connection Error", "Could not connect to the server.")
    exit()

# --- GUI SETUP (Tkinter) ---
root = tk.Tk()
root.title("Advanced Chat App - Base")
root.geometry("400x500")

# Hide the main window temporarily to ask for the username
root.withdraw()
username = simpledialog.askstring("Login", "Enter your username:", parent=root)

# If the user clicks cancel, close the app
if not username:
    client.close()
    root.destroy()
    exit()

# Show the main window again
root.deiconify()
root.title(f"Chat App - Logged in as: {username}")

# Chat History Area
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', bg="#f5f5f5")
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Configure Text Tags for Right/Left alignment
chat_area.tag_configure('right', justify='right', foreground='#0078D7', font=("Arial", 10, "bold"))
chat_area.tag_configure('left', justify='left', foreground='#333333', font=("Arial", 10))

# Message Entry Box
message_entry = tk.Entry(root, font=("Arial", 12))
message_entry.pack(padx=10, pady=(0, 10), fill=tk.X)

# --- CHAT FUNCTIONS ---
def receive_messages():
    """Listens for incoming messages from the server."""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            chat_area.config(state='normal')
            # Insert incoming messages aligned to the left
            chat_area.insert('end', message + '\n\n', 'left')
            chat_area.yview('end')
            chat_area.config(state='disabled')
        except:
            client.close()
            break

def send_message(event=None):
    """Sends the typed message to the server and displays it on the right."""
    message = message_entry.get()
    if message:
        # 1. Display our own message locally (aligned right)
        chat_area.config(state='normal')
        chat_area.insert('end', f"You: {message}\n\n", 'right')
        chat_area.yview('end')
        chat_area.config(state='disabled')
        
        # 2. Send the message to the server with our username attached
        formatted_message = f"{username}: {message}" 
        client.send(formatted_message.encode('utf-8'))
        
        # 3. Clear the input box
        message_entry.delete(0, 'end')

message_entry.bind("<Return>", send_message) # Press Enter to send

# Send Button
send_button = tk.Button(root, text="Send", command=send_message, bg="#0078D7", fg="white", font=("Arial", 10, "bold"))
send_button.pack(padx=10, pady=(0, 10), fill=tk.X)

# Start listening thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Run the GUI loop
root.mainloop()