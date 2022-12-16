# MemesTransferProtocol
# author: Patrik Valach
# 21.11.2021

import socket
import base64
import pynetstring
import tkinter
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename

# needs a connection to a server which will be able to communicate with this transfer protocol
HOST
PORT
# Variables
bg_col = '#2C2825'
inpt_col = '#705E52'
txt_col = '#FDCB52'
entr_meme = ''


def data_decode(data: bytes) -> str:
    return pynetstring.decode(data.decode().rstrip())[0].decode()


def data_encode(data: str, add: bool = False) -> bytes:
    global data_sum
    data = pynetstring.encode('C {}'.format(data))
    if add:
        data_sum += int(data.decode().split(':')[0]) - 2
    return data


def MTP(HOST: str, PORT: str, nick: str, password: str, meme: str, description: str, nsfw: str):
    global data_sum, status
    data_sum = 0
    meme = base64.b64encode(open(meme, "rb").read()).decode("ascii")
    # Part One----------------------------------------------------------------------------
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        status['text'] = 'Attempting to communicate with server.'
        window.update()

        # Connect---------
        try:
            s.connect((HOST, int(PORT)))
        except:
            status['text'] = 'Failed to connect to server. Check IP and Port.'
            return
        # -----------------

        # Init------------------------------------------------
        status['text'] = 'Starting MTP request.'
        window.update()

        s.sendall(data_encode('MTP V:1.0'))

        data = data_decode(s.recv(1024))
        if data[0] == 'E':
            status['text'] = data
            return
        else:
            data = data[2:]
        # Verify response
        if data != 'MTP V:1.0':
            status['text'] = 'Server failed accept MTP request.'
            return

        status['text'] = 'Server accepts MTP protocol'
        window.update()
        # -----------------------------------------------------

        # Send Nick---------------
        s.sendall(data_encode(nick))
        # Get Token---------------
        TOKEN1 = data_decode(s.recv(1024))
        if TOKEN1[0] == 'E':
            status['text'] = TOKEN1
            return
        else:
            TOKEN1 = TOKEN1[2:]
        # Get DataChannel Port----
        PORT_DATA = data_decode(s.recv(1024))
        if PORT_DATA[0] == 'E':
            status['text'] = PORT_DATA
            return
        else:
            PORT_DATA = int(PORT_DATA[2:])

    # Part Two----------------------------------------------------------------------------
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as d:
            status['text'] = 'Attempting to communicate with data server.'
            window.update()
            # Connect---------
            try:
                d.connect((HOST, PORT_DATA))
            except:
                status['text'] = 'Failed to connect to data server.'
                return

            status['text'] = 'Connected to data server.'
            window.update()
            # -----------------

            # Send nick---------------
            d.sendall(data_encode(nick))
            # Get token and check-----
            TOKEN2 = data_decode(d.recv(1024))
            if TOKEN2[0] == 'E':
                status['text'] = TOKEN2
                return
            else:
                TOKEN2 = TOKEN2[2:]
            if TOKEN1 != TOKEN2:
                status['text'] = 'Recieved unmatching token from data server.'
                return

            # Send meme---------------------------------------
            status['text'] = 'Uploading meme.'
            window.update()

            data = data_decode(d.recv(1024))
            if data[0] == 'E':
                status['text'] = data
                return
            else:
                data = data[2:]

            while 'END:' not in data:
                if data[4:] == 'meme':
                    d.sendall(data_encode(meme, True))
                elif data[4:] == 'description':
                    d.sendall(data_encode(description, True))
                elif data[4:] == 'isNSFW':
                    d.sendall(data_encode(nsfw, True))
                elif data[4:] == 'password':
                    d.sendall(data_encode(password, True))

                data = data_decode(d.recv(1024))
                if data[0] == 'E':
                    status['text'] = data
                    return
                else:
                    data = data[2:]

                data = data_decode(d.recv(1024))
                if data[0] == 'E':
                    status['text'] = data
                    return
                else:
                    data = data[2:]

            status['text'] = 'Meme uploaded.'
            window.update()
            # -------------------------------------------------
            TOKEN3 = data
    # Part Three----------------------------------------------------------------------------
        # Len Check----------------
        data = data_decode(s.recv(1024))
        if data[0] == 'E':
            status['text'] = data
            return
        else:
            data = data[2:]

        if int(data) != data_sum:
            status['text'] = 'Could not validate sent meme.'
            return

        status['text'] = 'File Validated.'
        window.update()
        # ---------------------------

        # Send Token--------------
        s.sendall(data_encode(TOKEN3[4:]))
        # End Communnication------
        data = data_decode(s.recv(1024))
        if data[0] == 'E':
            status['text'] = data
            return
        else:
            data = data[2:]

        if data == 'ACK':
            status['text'] = 'Successfully completed transfer.'
        else:
            status['text'] = 'Unsuccessfully completed tranfer!!!!'


def meme_loc():
    global entr_meme, lbl_file
    entr_meme = askopenfilename(title="Select a Meme")
    lbl_file['text'] = 'File {}'.format(entr_meme)
    has_input()


def has_input():
    global btn_run, status
    if len(entr_ip.get()) > 0 and len(entr_port.get()) > 0 and len(entr_nick.get()) > 0 and len(entr_pass.get()) > 0 and len(entr_dscrb.get("1.0", tkinter.END)) > 1 and len(entr_meme) > 5:
        if entr_meme[-4:] == '.png' or entr_meme[-5:] == '.jpeg':
            status['text'] = 'Ready to transfer meme.'
            btn_run['state'] = tkinter.NORMAL
            return
        else:
            status['text'] = 'Invalid file selected. (png/jpeg)'
    else:
        status['text'] = 'No input in entry fields or no file selected.'
    btn_run['state'] = tkinter.DISABLED


# Gui-----------------------------------------------------------------------------------
# Tk--------------------------------
window = tkinter.Tk()
window.geometry('770x400')
window.title('Memes Transfer Protocol Client')
window['bg'] = bg_col
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=8)
window.columnconfigure(2, weight=1)
window.columnconfigure(3, weight=8)

# Labels--------------------------------
tkinter.Label(text='IP Adress:', bg=bg_col, fg=txt_col).grid(
    row=0, column=0, sticky='w', padx=10, pady=5)
tkinter.Label(text='Port:', bg=bg_col, fg=txt_col).grid(
    row=0, column=2, sticky='w', padx=10)
tkinter.Label(text='Nick:', bg=bg_col, fg=txt_col).grid(
    row=1, column=0, sticky='w', padx=10)
tkinter.Label(text='Password:', bg=bg_col, fg=txt_col).grid(
    row=1, column=2, sticky='w', padx=10)
tkinter.Label(text='Description', bg=bg_col, fg=txt_col).grid(
    row=3, column=0, sticky='w', padx=10)
tkinter.Label(text='Meme', bg=bg_col, fg=txt_col).grid(
    row=5, column=0, sticky='w', padx=10, pady=10)

lbl_file = tkinter.Label(text='File:', bg=bg_col, fg=txt_col)
lbl_file.grid(row=7, column=0, sticky='w', padx=10, pady=10, columnspan=4)

status = tkinter.Label(
    text='No input in entry fields or no file selected.', bg=bg_col, fg=txt_col)
status.grid(row=5, column=1, columnspan=3)

# Entries--------------------------------
entr_ip = tkinter.Entry(bg=inpt_col, width=40)
entr_ip.grid(row=0, column=1, sticky='w')
entr_port = tkinter.Entry(bg=inpt_col, width=40)
entr_port.grid(row=0, column=3, sticky='w')
entr_nick = tkinter.Entry(bg=inpt_col, width=40)
entr_nick.grid(row=1, column=1, sticky='w')
entr_pass = tkinter.Entry(bg=inpt_col, width=40)
entr_pass.grid(row=1, column=3, sticky='w')

# Other widgets--------------------------------
entr_nsfw = tkinter.StringVar(value='false')
tkinter.Checkbutton(bg=bg_col, fg=txt_col, activebackground=bg_col, activeforeground=inpt_col, selectcolor=inpt_col,
                    text='NSFW', variable=entr_nsfw, offvalue='false', onvalue='true').grid(row=2, column=0)

entr_dscrb = tkinter.scrolledtext.ScrolledText(
    height=10, width=90, bg=inpt_col)
entr_dscrb.grid(row=4, column=0, columnspan=4, sticky='w', padx=10)

btn_loc = tkinter.Button(text='Browse', bg=txt_col,
                         activebackground=txt_col, command=lambda: meme_loc())
btn_loc.grid(row=6, column=0, sticky='w', padx=10)

btn_run = tkinter.Button(text='Send Meme', bg=txt_col, activebackground=txt_col, state=tkinter.DISABLED, command=lambda: MTP(
    entr_ip.get(), entr_port.get(), entr_nick.get(), entr_pass.get(), entr_meme, entr_dscrb.get("1.0", tkinter.END), entr_nsfw.get()))
btn_run.grid(row=7, column=3, sticky='e', padx=20)

window.bind('<KeyRelease>', lambda event: has_input())

window.mainloop()
