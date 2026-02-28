import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, filedialog
import os
import sys
import base64
from cryptography.fernet import Fernet
from plyer import notification

# --- ADVANCED FEATURES SETUP ---
ENCRYPTION_KEY = b'MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI='
cipher_suite = Fernet(ENCRYPTION_KEY)

EMOJIS = {
    ":)": "😊",
    ":(": "😢",
    ":D": "😁",
    "<3": "❤️",
    ":thumbsup:": "👍",
    ":fire:": "🔥"
}

def replace_emojis(text):
    for code, emoji in EMOJIS.items():
        text = text.replace(code, emoji)
    return text

HISTORY_FILE = "chat_history.txt"

def save_history(message):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

# --- SERVER CONNECTION ---
HOST = '127.0.0.1'
PORT = 5555
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
except:
    messagebox.showerror("Connection Error", "Could not connect to the server.")
    sys.exit()

# --- GUI SETUP ---
root = tk.Tk()
root.title("Advanced Chat App")
root.geometry("450x600")

# Authentication
root.withdraw()
username = simpledialog.askstring("Login", "Enter your username:", parent=root)
if not username:
    client.close()
    root.destroy()
    sys.exit()

root.deiconify()
root.title(f"Chat App - Secured Session ({username})")

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', bg="#f5f5f5")
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_area.tag_configure('right', justify='right', foreground='#0078D7', font=("Arial", 11, "bold"))
chat_area.tag_configure('left', justify='left', foreground='#333333', font=("Arial", 11))
chat_area.tag_configure('system', justify='center', foreground='#888888', font=("Arial", 9, "italic"))

input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

message_entry = tk.Entry(input_frame, font=("Arial", 12))
message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

# --- LOAD HISTORY ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        chat_area.config(state='normal')
        chat_area.insert('end', "--- Previous Chat History ---\n\n", 'system')
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                chat_area.insert('end', line, 'system')
        chat_area.insert('end', "--- End of History ---\n\n", 'system')
        chat_area.yview('end')
        chat_area.config(state='disabled')

load_history()

# --- CHAT & FILE FUNCTIONS ---
def receive_messages():
    while True:
        try:
            encrypted_message = client.recv(1024 * 1024 * 5) 
            if not encrypted_message:
                break
                
            decrypted_message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
            
            if decrypted_message.startswith("[FILE]:"):
                parts = decrypted_message.split(":", 3)
                sender = parts[1]
                filename = parts[2]
                encoded_data = parts[3]
                
                file_bytes = base64.b64decode(encoded_data)
                save_path = f"downloaded_{filename}"
                with open(save_path, "wb") as f:
                    f.write(file_bytes)
                
                display_msg = f"{sender} sent a file: {filename} (Saved to folder)"
            else:
                display_msg = decrypted_message
                
            chat_area.config(state='normal')
            chat_area.insert('end', display_msg + '\n\n', 'left')
            chat_area.yview('end')
            chat_area.config(state='disabled')
            
            save_history(display_msg)
            
            notification.notify(
                title=f"New Message",
                message=display_msg[:40] + "..." if len(display_msg) > 40 else display_msg,
                app_name="Advanced Chat",
                timeout=3
            )
        except Exception as e:
            print("Disconnected or error:", e)
            client.close()
            break

def send_message(event=None):
    message = message_entry.get()
    if message:
        message = replace_emojis(message)
        display_msg = f"You: {message}"
        
        chat_area.config(state='normal')
        chat_area.insert('end', display_msg + '\n\n', 'right')
        chat_area.yview('end')
        chat_area.config(state='disabled')
        
        save_history(display_msg)
        
        formatted_message = f"{username}: {message}" 
        encrypted_message = cipher_suite.encrypt(formatted_message.encode('utf-8'))
        client.send(encrypted_message)
        message_entry.delete(0, 'end')

def send_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        filename = os.path.basename(filepath)
        
        with open(filepath, "rb") as file:
            file_data = file.read()
        encoded_data = base64.b64encode(file_data).decode('utf-8')
        
        file_message = f"[FILE]:{username}:{filename}:{encoded_data}"
        
        display_msg = f"You sent a file: {filename}"
        chat_area.config(state='normal')
        chat_area.insert('end', display_msg + '\n\n', 'right')
        chat_area.yview('end')
        chat_area.config(state='disabled')
        save_history(display_msg)
        
        encrypted_message = cipher_suite.encrypt(file_message.encode('utf-8'))
        client.send(encrypted_message)

message_entry.bind("<Return>", send_message)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

send_button = tk.Button(button_frame, text="Send Text", command=send_message, bg="#0078D7", fg="white", font=("Arial", 10, "bold"), width=20)
send_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

file_button = tk.Button(button_frame, text="Send File", command=send_file, bg="#28A745", fg="white", font=("Arial", 10, "bold"), width=15)
file_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

# Start thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

root.mainloop()