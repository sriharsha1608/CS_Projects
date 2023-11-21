import socket
import ssl
import hashlib

def handle_client(connection):
    while True:
        data = connection.recv(4096).decode()
        if not data:
            break
        user_id, password = data.split()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        with open('hashpasswd', 'r') as file:
            for line in file:
                existing_id, existing_hashed_password, *_ = line.split(maxsplit=2)
                if existing_id == user_id and existing_hashed_password == hashed_password:
                    connection.send(b"Correct ID and password")
                    break
            else:
                connection.send(b"The ID/password is incorrect")
    connection.close()

def main(server_port):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    with socket.socket(socket.AF_INET) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', server_port))
        sock.listen(1)
        with context.wrap_socket(sock, server_side=True) as server_sock:
            while True:
                client_sock, _ = server_sock.accept()
                handle_client(client_sock)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 serv.py <server_port>")
    else:
        server_port = int(sys.argv[1])
        main(server_port)
