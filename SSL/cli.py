import socket
import ssl
import sys

def main(server_domain, server_port):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    with socket.create_connection((server_domain, server_port)) as sock:
        with context.wrap_socket(sock, server_hostname=server_domain) as ssock:
            while True:
                user_id = input("Enter ID: ")
                password = input("Enter Password: ")
                ssock.send(f"{user_id} {password}".encode())
                response = ssock.recv(4096).decode()
                print(response)
                if response == "Correct ID and password":
                    break

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 cli.py <server_domain> <server_port>")
    else:
        server_domain = sys.argv[1]
        server_port = int(sys.argv[2])
        main(server_domain, server_port)
