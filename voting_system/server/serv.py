import socket
import ssl
import hashlib
import random
import os
from datetime import datetime
from Crypto.Cipher import AES
import hashlib
import sys


def encrypt(data,enc_key):
    data_bytes = data.encode('utf-8')
    hash_object = hashlib.md5(data_bytes)
    hash_bytes = hash_object.digest()

    cipher = AES.new(enc_key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(hash_bytes)
    return ciphertext

def check_voted(client_id):
    with open("history", "r") as f:
        for line in f:
            parts = line.split()
            file_name = parts[0]
            if file_name == client_id:
                return False
                break

    return True

# with open('voterinfo', "w") as f:
#     vot_in=['Alice 1123456 1234','Bob 1138765 5678','Tom 1154571 9012']
#     for i in vot_in:
#         f.write(i+'\n')

server_port = int(sys.argv[1])


ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssocket.bind(("", server_port))

ssocket.listen(5)
print("Server on port", server_port)

# enc_key = os.urandom(16)
file = open("symmetric_key", "rb")
# file.write(enc_key)
enc_key=file.read()
file.close()

# new_lines = [] 
# with open('voterinfo', "r") as f:   
#     for line in f:
#         parts = line.split(" ", 2)
#         passw=encrypt(parts[2].strip(),enc_key)        
#         new_line = f"{parts[0]} {parts[1]} {passw}"       
#         new_lines.append(new_line)

# with open('voterinfo', "w") as f:
#     f.write("\n".join(new_lines))

candidates = {1: "Chris", 2: "Linda"}

try:
    with open("result", "r") as f:
        lines = f.readlines()
except:
    with open("result", "w") as f:
        f.write(f"Chris 0\n")
        f.write(f"Linda 0\n")

with open("result", "r") as f:
    lines = f.readlines()
    chris_votes = int(lines[0].split()[1])
    linda_votes = int(lines[1].split()[1])


try:
    with open("history", "r") as f:
        pass
except:
    with open("history", "w") as f:
        pass


reg_dict={}
passwords_dict = {}
with open("voterinfo", "r") as f:
    for line in f:
        user_id,reg_number,password = line.strip().split(" ", 2)
        reg_dict[user_id] = reg_number
        passwords_dict[user_id] = password


total_voters=len(reg_dict)

while True:
    connection, address = ssocket.accept()

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    ssl_connection = ssl_context.wrap_socket(connection, server_side=True)
    print("hi")
    authenticated = False
    while not authenticated:
        client_id, client_reg_number, client_password = ssl_connection.recv(1024).decode().strip().split()

        if client_id in reg_dict and reg_dict[client_id] == client_reg_number:
            eeclient_password=f"{encrypt(client_password.strip(),enc_key)}  "
            if passwords_dict[client_id] == eeclient_password.strip():
                authenticated = True
                ssl_connection.send("success".encode())
                print(f"User {client_id} verified")
            else:
                ssl_connection.send("wrong details".encode())
        else:
            ssl_connection.send("wrong details".encode())

    
    while True:
        command = ssl_connection.recv(1024).decode().strip()
        check=check_voted(client_id)
        if command=='1':
            
            if check:
                ssl_connection.sendall(b"1")
                vote = ssl_connection.recv(1024).decode().strip()
                candidate_number = int(vote)
                if candidate_number == 1:
                    chris_votes+=1
                elif candidate_number == 2:
                    linda_votes+=1
                
                with open("result", "w") as f:
                    f.write(f"Chris {chris_votes}\n")
                    f.write(f"Linda {linda_votes}\n")

                now = datetime.now()
                date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

                with open("history", "a") as f:
                    f.write(f"{client_id} {date_time_str}\n")
                
                # check=False
                # ssl_connection.sendall(f"You voted for {candidates[candidate_number]}\n".encode())
                ssl_connection.sendall(f"You have successfully voted\n".encode())
            else:
                ssl_connection.sendall(b"0")
        elif command=='2':
            vote_count=0
            with open("history", "r") as f:
                for line in f:
                    vote_count+=1
                   
            if  vote_count< total_voters:
                ssl_connection.sendall(b"0")
            else:
                ssl_connection.sendall(b"1")
                if chris_votes > linda_votes:
                    winner = "Chris"
                elif linda_votes > chris_votes:
                    winner = "Linda"
                else:
                    winner = "Tie"
                
                send_msg1= winner+' Win'
                send_msg2='Chris '+str(chris_votes)
                send_msg3='Linda '+str(linda_votes)
            
                ssl_connection.sendall(send_msg1.encode())
                ssl_connection.sendall(send_msg2.encode())
                ssl_connection.sendall(send_msg3.encode())
        elif command=='3':
            if check:
                ssl_connection.sendall("you are yet to vote".encode())
            else:
                with open("history", "r") as f:
                    for line in f:
                        parts = line.split()
                        file_name = parts[0]
                        if file_name == client_id:
                            his=line
                            break

                ssl_connection.sendall(his.encode())
        elif command=='4':
            ssl_connection.close()
            break
        else:
            ssl_connection.sendall("Invalid Command\n".encode())
