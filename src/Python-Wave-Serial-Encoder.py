# !/usr/bin/python3
import tkinter as tk
import sys
import os
import serial
import time
import threading
import webbrowser
import wave
import tkinter.font

from os import path

# from serial import Serial
from tkinter import Label
from tkinter import StringVar
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
from tkinter import ttk
from serial.tools import list_ports  # pyserial
from queue import Queue


# Setting Available Ports
def serial_ports():
    ports = serial.tools.list_ports.comports()

    ser_port = []
    for port, desc, hwid in sorted(ports):
        ser_port.append("{}".format(port))

    return ser_port


def enumerate_serial_devices():
    length = len(list_ports.comports())
    return length


def check_new_devices(old_devices, port, connection, combo):
    new_length = enumerate_serial_devices()
    ser_port = serial_ports()
    if new_length != old_devices:
        combo.set("")
        combo["values"] = ser_port
        if new_length > old_devices:
            connection.config(fg="white", bg="black")
            port.set("No connection")
        else:
            connection.config(bg="red")
            port.set("Disconnected")

    return new_length


def usb_monitor(e, e1, e2, port, connection, old_devices, combo):
    while e.is_set():
        if e1.is_set():
            old_devices = check_new_devices(old_devices, port, connection, combo)
        time.sleep(1)
    e2.set()


# Update Serial Ports List
def update_ports(ser_port):
    ser_port = serial_ports()
    combo.set("")
    combo["values"] = ser_port


# Connection
def connPort(arduino, port, connection):
    port_name = str(combo.get())

    if port_name != "":
        arduino.port = port_name
        port.set("Selected device " + combo.get() + ".\nPress Start to open port.")
        connection.config(bg="black")
    else:
        port.set("Connection Failed")
        connection.config(bg="red")


# Reading
def read_from_port(q, e, e1, e3, arduino, entry, result):
    while e.is_set():
        if not e1.is_set():
            if path.isfile(entry.get()):
                os.remove(entry.get())

            try:
                f = wave.open(entry.get(), "wb")
                f.setnchannels(1)
                f.setframerate(16000)
                f.setsampwidth(2)

                arduino.write(b"\x01")
                arduino.flushInput()
                result.set("Writing on " + entry.get())

                while arduino.isOpen():
                    ser_bytes = arduino.read(256)

                    if ser_bytes != b"":
                        f.writeframes(ser_bytes)
                        # print(ser_bytes)

                    if not q.empty():
                        f.close()
                        arduino.close()
                        e1.set()
            except IOError:
                result.set("Error: file path not valid")
        time.sleep(0.1)
    e3.set()


# Start recording
def start(e1, q, arduino, port, connection, entry, result):
    # print("Start")

    if entry.get() != "":
        q.queue.clear()
        try:
            if not arduino.isOpen():
                arduino.open()
            connection.config(bg="green")
            port.set("Port open")
            e1.clear()
        except serial.SerialException:
            port.set("Port not selected or connection button not pushed")
            connection.config(bg="red")
    else:
        result.set("File name entry empty")


# Stop recording
def stop(q, arduino, port, connection, e1):
    # print("Stop")
    if not e1.is_set():
        arduino.write(b"\x00")
        arduino.flushInput()
        a = 0
        q.put(a)
        port.set("Port closed")
        connection.config(bg="black")


# Setting save path
def save(entry):
    dir_name = filedialog.asksaveasfilename(
        defaultextension=".wav", filetypes=[("Wave", "*.wav")]
    )
    entry.delete(0, "end")
    entry.insert(0, dir_name)
    entry.xview_moveto(1)


def man_callback():
    readme = tk.Tk()
    readme.title("Python Wave Serial Encoder")
    readme.geometry("580x260")
    text = tk.Label(readme, text="Manual", font="Helvetica 16 bold")
    man = tk.Label(
        readme,
        justify=tk.LEFT,
        text="""1. Use the dropdown menu to select the port and then click on "Connect"

2. Choose the path where the file will be saved by using the "Save" button

3. Use start and stop button to respectively start and stop the recording.

Please note: to record more than one file, change the path else the old file will be overridden.

In case the dropdown menu does not detect the port, use the button "Refresh"
to update the Serial Port""",
        anchor="e",
    )
    text.pack()
    man.pack()


def exit_callback(e, e1, e2, e3, q, arduino):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if not e1.is_set():
            arduino.write(b"\x00")
            arduino.flushInput()
            a = 0
            q.put(a)
            while not e1.is_set():
                time.sleep(1)
        e.clear()
        e2.wait()
        e3.wait()
        sys.exit()


def info_callback():
    info = tk.Tk()
    info.title("Python Wave Serial Encoder")
    info.geometry("400x150")
    # readme.iconphoto(False, tk.PhotoImage(file='st_icon.png'))
    title = tk.Label(info, text="Python Wave Serial Encoder", font="Helvetica 16 bold")
    inft = tk.Label(
        info,
        text="Copyright \u00a9 STMicroelectronics 2020\n\n\
        Version 1.0.0",
    )
    title.pack()
    inft.pack()

    link = Label(info, text="http://www.st.com", fg="blue", cursor="hand2")
    link.pack()
    link.bind("<Button-1>", lambda event: webbrowser.open(link.cget("text")))


def percent(n, t):
    return int((t * n) / 100)


e = threading.Event()
e1 = threading.Event()
e2 = threading.Event()
e3 = threading.Event()
e.set()
e1.set()
e2.clear()
e3.clear()

# WINDOW configuration


window = tk.Tk()
screen_width = int((window.winfo_screenwidth() * 60) / 100)
screen_height = int((window.winfo_screenheight() * 50) / 100)
s = str(screen_width) + "x" + str(screen_height)


window.title("Python Wave Serial Encoder")
window.geometry(s)
window.update()
window.iconphoto(False, tk.PhotoImage(file="st_icon.png"))


# MENU
menu_widget = tk.Menu(master=window)
menu_widget.add_command(label="Manual", command=man_callback)
menu_widget.add_command(label="Info", command=info_callback)
menu_widget.add_command(
    label="Exit", command=lambda: exit_callback(e, e1, e2, e3, queue, arduino)
)
window.config(menu=menu_widget)

# FRAME CONFIG

frame_dx = tk.LabelFrame(
    master=window,
    text="Recording",
    width=percent(60, screen_width),
    height=screen_height,
)

frame_sx = tk.LabelFrame(
    master=window,
    text="Selection port",
    width=percent(40, screen_width),
    height=screen_height,
)

w_fdx = frame_dx.winfo_reqwidth()
h_fdx = frame_dx.winfo_reqheight()
w_fsx = frame_sx.winfo_reqwidth()
h_fsx = frame_sx.winfo_reqheight()
font = tkinter.font.Font(size=percent(3, h_fdx))

# FRAME RIGHT
# Save Path Entry
man = Label(
    frame_dx,
    text="Click Save button to select path,\
    then enter the file name.",
)
saveB = tk.Button(master=frame_dx, text="Save", command=lambda: save(entry))
entry = tk.Entry(master=frame_dx, width=30, font=font)


# Result
result = StringVar()
msg = Label(frame_dx, textvariable=result, borderwidth=2, relief="sunken")
result.set("")

# Button Start Stop Reset
queue = Queue()
arduino = serial.Serial(None, 921600, timeout=0)

# Result
port = StringVar()
connection = Label(
    frame_sx, textvariable=port, borderwidth=2, relief="sunken", anchor="w"
)
connection.configure(fg="white", bg="black")
port.set("No connection")

startB = tk.Button(
    master=frame_dx,
    text="Start",
    command=lambda: start(e1, queue, arduino, port, connection, entry, result),
)
stopB = tk.Button(
    master=frame_dx,
    text="Stop",
    command=lambda: stop(queue, arduino, port, connection, e1),
)

# LOGO
load = Image.open("st_logo.png")
render = ImageTk.PhotoImage(load)
img = Label(frame_dx, image=render)
img.image = render
w = img.winfo_reqwidth()
h = img.winfo_reqheight()
img.place(x=w_fdx - (w + percent(8, w_fdx)), y=h_fdx - (h + percent(8, h_fdx)))

# FRAME LEFT

var = StringVar()
labelsx = Label(frame_sx, textvariable=var)
var.set("Select port: ")

# Combo Box
ser_port = serial_ports()
combo = ttk.Combobox(frame_sx, values=ser_port, font=font)
# combo.current(0)
# combo.bind("<<ComboboxSelected>>", callbackFunc)

# Button to Connect
connB = tk.Button(
    master=frame_sx, text="Connect", command=lambda: connPort(arduino, port, connection)
)

# Button to Refresh port
ref = tk.PhotoImage(file="ref.png", width=20, height=20)
refreshB = tk.Button(master=frame_sx, image=ref, command=lambda: update_ports(ser_port))

frame_dx.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True, padx=1, pady=1)
frame_sx.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=1, pady=1)

labelsx.place(x=percent(2, w_fsx), y=percent(2, h_fsx))
combo.place(x=percent(2, w_fsx), y=percent(8, h_fsx))
connection.place(x=percent(2, w_fsx), y=percent(16, h_fsx))
connB.place(x=percent(64, w_fsx), y=percent(8, h_fsx))
refreshB.place(x=percent(90, w_fsx), y=percent(8, h_fsx))
man.place(x=percent(2, w_fdx), y=percent(2, h_fdx))
entry.place(x=percent(2, w_fsx), y=percent(8, h_fsx))
saveB.place(x=percent(70, w_fdx), y=percent(8, h_fdx))
msg.place(x=percent(2, w_fdx), y=percent(16, h_fdx))
startB.place(x=percent(10, w_fsx), y=percent(24, h_fsx))
stopB.place(x=percent(30, w_fsx), y=percent(24, h_fsx))


old_devices = enumerate_serial_devices()
u = threading.Thread(
    target=usb_monitor, args=(e, e1, e2, port, connection, old_devices, combo)
)
u.start()
t = threading.Thread(
    target=read_from_port, args=(queue, e, e1, e3, arduino, entry, result)
)
t.start()


def on_closing():
    exit_callback(e, e1, e2, e3, queue, arduino)


window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()  # do script
