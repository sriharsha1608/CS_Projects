import sys
import socket
import ssl
import os

server_port = int(sys.argv[1])

ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssocket.bind(("", server_port))

ssocket.listen(1)
print("Server on port", server_port)

current_dir = os.path.dirname(os.path.abspath(__file__))
password_dir = os.path.dirname(current_dir)
pass_file_path = os.path.join(password_dir, "password")
passwords_dict = {}
with open(pass_file_path, "r") as f:
    for line in f:
        user_id, password = line.strip().split()
        passwords_dict[user_id] = password


while True:
    connection, address = ssocket.accept()

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    ssl_connection = ssl_context.wrap_socket(connection, server_side=True)

    authenticated = False
    while not authenticated:
        client_id, client_password = ssl_connection.recv(1024).decode().strip().split()

        if client_id in passwords_dict and passwords_dict[client_id] == client_password:
            authenticated = True
            ssl_connection.send("success".encode())
            print(f"User {client_id} verified")
        else:
            ssl_connection.send("wrong details".encode())

    
    while True:
        command = ssl_connection.recv(1024).decode().strip()

        if command.startswith("put "):
            file_path = command[4:]
            file_size = int(ssl_connection.recv(1024).decode().strip())
            with open(file_path, "wb") as f:
                letters_read = 0
                while letters_read < file_size:
                    block = ssl_connection.recv(1024)
                    f.write(block)
                    letters_read += len(block)
            print(f"File {file_path} received from {client_id}")
        elif command == "lls":
            files = os.listdir(".")
            file_list = "\n".join(files)
            ssl_connection.send(file_list.encode())
        elif command == "exit":
            ssl_connection.close()
            print(f"Session closed with {client_id}")
            break
        else:
            ssl_connection.send("Invalid Command\n".encode())

