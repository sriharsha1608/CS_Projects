import sys
import socket
import ssl
import os


def receive_data(connection):
    data = connection.recv(1024).decode()
    return data.strip()

def send_data(connection, data):
    connection.send(data.encode())

def command_operations(connection, command):
    if command.startswith('put'):
        filename = command.split()[1]
        if not os.path.isfile(filename):
            print(f"No {filename}")
            return

        send_data(connection, command)
        with open(filename, 'rb') as file:
            file_data = file.read()

        send_data(connection, str(os.path.getsize(filename)))
        connection.sendall(file_data)
        print(f"File {filename} transfered")
    elif command == 'lls':
        # send_data(connection, command)
        # print(receive_data(connection))
        files = os.listdir('.')
        for file in files:
            print(file)
    elif command == 'exit':
        send_data(connection, command)
        print("terminating session")
        connection.close()
        exit()
    else:
        print("Invalid command")


server_domain = sys.argv[1]
server_port = int(sys.argv[2])

csock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
conn_sock=context.wrap_socket(csock,server_hostname=server_domain)
conn_sock.connect((server_domain,server_port))


while True:
    user_id = input("ID:")
    password = input("password:")
    send_data(conn_sock, f"{user_id} {password}")
    response = receive_data(conn_sock)
    if response == "success":
        print(f"Hi {user_id}")
        break
    else:
        print("wrong details, please try again")

while True:
    command = input("sftp >")
    command_operations(conn_sock, command)

