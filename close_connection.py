import socket
import pyaudio
import threading
import tkinter as tk
from PIL import Image, ImageTk  # Import Image and ImageTk from the PIL library
import sys
from tkinter import Frame
# Sender configuration
SENDER_HOST = '0.0.0.0'  # Host IP
SENDER_PORT = 12345     # Port for sender
RECEIVER_IP = '192.168.29.157'  # Receiver's IP address
RECEIVER_PORT = 12346   # Port for receiver
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
MAX_PACKET_SIZE = 4096  # Maximum size of each packet
server_ip = '192.168.29.157'  # Raspberry Pi's IP address
server_port = 12356

# Initialize PyAudio
audio = pyaudio.PyAudio()
sender_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
receiver_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

# Set up sender and receiver sockets
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind((SENDER_HOST, RECEIVER_PORT))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ptt_active = False
exit_flag = False  # Flag to signal threads to exit

def send_audio():
    while not exit_flag:
        if ptt_active:
            data = sender_stream.read(CHUNK)
            for i in range(0, len(data), MAX_PACKET_SIZE):
                chunk = data[i:i+MAX_PACKET_SIZE]
                sender_socket.sendto(chunk, (RECEIVER_IP, RECEIVER_PORT))

def receive_audio():
    while not exit_flag:
        data, _ = receiver_socket.recvfrom(MAX_PACKET_SIZE)
        receiver_stream.write(data)

# Start sender and receiver threads
sender_thread = threading.Thread(target=send_audio)
receiver_thread = threading.Thread(target=receive_audio)
sender_thread.start()
receiver_thread.start()

# Create a function to draw a red circle for "Busy" status
def draw_busy_circle():
    canvas.create_oval(170, 100, 270, 200, fill="red")
    canvas.create_text(220, 150, text="Busy", fill="white", font=("Helvetica", 18, "bold"))

# Create a function to draw a blue circle for "Ready to Use" status
def draw_ready_circle():
    canvas.create_oval(170, 100, 270, 200, fill="blue")
    canvas.create_text(220, 150, text="Available", fill="white", font=("Helvetica", 16, "bold"))

# Create a function to simulate key press
def simulate_key_press():
    client_socket.sendto(b'high', (server_ip, server_port))
    global ptt_active
    ptt_active = True
    status_label.config(text="Status: Talking", fg="blue")
    print("Talking")
    canvas.delete("all")  # Clear the canvas
    draw_busy_circle()

# Create a function to simulate key release
def simulate_key_release():
    client_socket.sendto(b'low', (server_ip, server_port))
    global ptt_active
    ptt_active = False
    status_label.config(text="Status: Not Talking", fg="red")
    print("Not Talking")
    canvas.delete("all")  # Clear the canvas
    draw_ready_circle()

def key_pressed(event):
    if event.keysym == 'p':
        client_socket.sendto(b'high', (server_ip, server_port))
        global ptt_active
        ptt_active = True
        print("Talking...")

def key_released(event):
    if event.keysym == 't':
        client_socket.sendto(b'low', (server_ip, server_port))
        global ptt_active
        ptt_active = False
        print("Not talking...")

# Create the main window
root = tk.Tk()
root.configure(bg='black')
root.title("PTT Control")

# Load and display the background image

# bg_label.place(x=0, y=0, relwidth=1, relheight=1)
# Load and display the background image


# Calculate the center coordinates of the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 440
window_height = 440
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# Set the window size and position
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Create buttons for key press and key release
key_press_button = tk.Button(root, text="Key Press (P)", command=simulate_key_press, bg="blue", padx=10, pady=10)
key_release_button = tk.Button(root, text="Key Release (T)", command=simulate_key_release, bg="red", padx=10, pady=10)

# Create a label for the status
status_label = tk.Label(root, text="Status: Not Talking", fg='red', font=("Helvetica", 21, "bold") ,bg='black' )

# Create a canvas for drawing circles
canvas = tk.Canvas(root, width=window_width, height=window_height,bg='black',highlightbackground="black")

def close_connection():
    global ptt_active, exit_flag
    exit_flag = True  # Set the exit flag to signal threads to exit
    if ptt_active:
        ptt_active = False
        client_socket.sendto(b'low', (server_ip, server_port))
    sender_stream.stop_stream()
    sender_stream.close()
    receiver_stream.stop_stream()
    receiver_stream.close()
    sender_socket.close()
    receiver_socket.close()
    client_socket.close()
    audio.terminate()
    root.destroy()
    sys.exit()  # Exit the script

close_button = tk.Button(root, text="Close Connection", command=close_connection, bg="green", padx=10, pady=10)

frame_img = Frame(root, width=100, height=100 )
frame_img.configure(bg='black')
frame_img.pack()

bg_image = Image.open("armlogo.jpg")  # Replace "background.jpg" with the path to your JPEG image
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(frame_img, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

frame_img.place(x=-50,y=0, relx=0.5, rely=0.5)

# Pack the elements to display them in the window
key_press_button.pack(pady=10)
key_release_button.pack(pady=10)
status_label.pack()
close_button.pack(pady=10)
canvas.pack()

# Initialize the canvas with a blue circle for "Ready to Use"
draw_ready_circle()
root.bind('<KeyPress>', key_pressed)
root.bind('<KeyRelease>', key_released)

# Start the Tkinter main loop
root.mainloop()