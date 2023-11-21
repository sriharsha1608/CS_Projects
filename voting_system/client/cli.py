import sys
import socket
import ssl
import os
import sys

def receive_data(connection):
    data = connection.recv(1024).decode()
    return data.strip()

def send_data(connection, data):
    connection.send(data.encode())


def command_operations(connection, command):
    if command == '1':
        connection.sendall('1'.encode())
        
        vote_response = connection.recv(1024).decode()
        if vote_response == '0':
            print('You have already voted')
            print("")
        else:
            
            print('Candidates: (enter 1 or 2)')
            print('1. Chris')
            print('2. Linda')
            candidate_choice = input('Enter a number (1-2): ')
            
            connection.sendall(candidate_choice.encode())
            
            confirmation = connection.recv(1024).decode()
            print(confirmation)
            print("")
            
    
    elif command == '2':
       
        connection.sendall('2'.encode())  

        re_check=connection.recv(1024).decode()
        if re_check=='0':
            print('The result is not available\n')
        else:
            result = connection.recv(1024).decode()
            print(result)
            can1 = connection.recv(1024).decode()
            print(can1)
            can2 = connection.recv(1024).decode()
            print(can2)
            print("")
    
    elif command == '3':
        connection.sendall('3'.encode())

        history = connection.recv(1024).decode()
        print(history)
        print("")

    elif command == '4':
        connection.sendall('4'.encode())
        print("terminating session")
        connection.close()
        exit()
    else:
        print("Invalid option\n")


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
    reg_no = input("registration number:")
    password = input("password:")
    send_data(conn_sock, f"{user_id} {reg_no} {password}")
    response = receive_data(conn_sock)
    if response == "success":
        print(f"\nWelcome {user_id}")
        break
    else:
        print("Invalid name, registration number, or password\n")

while True:
    print("Please enter a number (1-4)")
    print("1. Vote")
    print("2. View election result")
    print("3. My vote history")
    print("4. Exit\n")
    command = input()
    command_operations(conn_sock, command)
