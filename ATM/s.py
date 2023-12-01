import socket
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes


def decrypt_with_rsa(private_key, ciphertext):
    cipher_rsa = PKCS1_OAEP.new(private_key)
    plaintext = cipher_rsa.decrypt(ciphertext)
    return plaintext


def decrypt_with_des(key, ciphertext):
    decipher_des = DES.new(key, DES.MODE_ECB)
    plaintext = decipher_des.decrypt(ciphertext)
    # Remove padding
    plaintext = plaintext.rstrip(b' ')
    return plaintext


# Load the bank's private key
with open("bank_private_key.pem", "rb") as key_file:
    bank_private_key = RSA.import_key(key_file.read())

# Load the password file
passwords = {}
with open("password.txt", "r") as password_file:
    for line in password_file.readlines():
        username, password = line.strip().split()
        passwords[username] = password

# Load the initial balance file
balances = {}
with open("balance.txt", "r") as balance_file:
    for line in balance_file.readlines():
        username, savings_balance, checking_balance = line.strip().split()
        balances[username] = {
            "savings": int(savings_balance),
            "checking": int(checking_balance),
        }

# Create a socket for server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 12345))
server_socket.listen(5)

while True:
    print("Waiting for a connection...")
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    try:
        # Step 4: Receive and decrypt the client's message
        encrypted_symmetric_key = client_socket.recv(256)
        encrypted_credentials = client_socket.recv(256)

        
        symmetric_key = decrypt_with_rsa(bank_private_key,encrypted_symmetric_key)

        
        decrypted_credentials = decrypt_with_des(symmetric_key,encrypted_credentials)

        received_username, received_password = decrypted_credentials.decode().strip().split(" ")

        # Step 4: Authenticate the user
        if received_username in passwords and passwords[received_username] == received_password:
            client_socket.send("ID and password are correct".encode())
        else:
            client_socket.send("ID or password is incorrect".encode())
            client_socket.close()
            continue

        while True:
            # Step 5: Display main menu and handle user choice
            choice = client_socket.recv(256).decode()

            if choice == "1":
                # Step 6: Handle money transfer
                while True:
                    account_choice = client_socket.recv(256).decode()
                    if account_choice not in ["1", "2"]:
                        client_socket.send("Incorrect input".encode())
                        continue
                    else:
                        client_socket.send("correct input".encode())
                        break

                recipient_username = client_socket.recv(256).decode()
                transfer_amount = int(client_socket.recv(256).decode())

                if recipient_username not in balances:
                    client_socket.send("The recipient's ID does not exist\n".encode())
                    continue

                if account_choice == "1":
                    if balances[received_username]["savings"] >= transfer_amount:
                        balances[received_username]["savings"] -= transfer_amount
                        balances[recipient_username]["savings"] += transfer_amount
                        client_socket.send("Your transaction is successful\n".encode())
                    else:
                        client_socket.send("Your account does not have enough funds\n".encode())

                elif account_choice == "2":
                    if balances[received_username]["checking"] >= transfer_amount:
                        balances[received_username]["checking"] -= transfer_amount
                        balances[recipient_username]["checking"] += transfer_amount
                        client_socket.send("Your transaction is successful\n".encode())
                    else:
                        client_socket.send("Your account does not have enough funds\n".encode())

                with open("balance.txt", "r") as balance_file:
                    lines = balance_file.readlines()
                with open("balance.txt", "w") as balance_file:
                    for line in lines:
                        username, savings_balance, checking_balance = line.strip().split()
                        if username == received_username:
                            savings_balance = str(balances[received_username]["savings"])
                            checking_balance = str(balances[received_username]["checking"])
                        balance_file.write(f"{username} {savings_balance} {checking_balance}\n")

            elif choice == "2":
                # Step 7: Check account balance
                client_socket.send(
                    f"Your savings account balance: {balances[received_username]['savings']}\nYour checking account balance: {balances[received_username]['checking']}\n".encode()
                )

            elif choice == "3":
                # Step 8: Exit
                client_socket.send("Exiting...\n".encode())
                client_socket.close()
                break

            else:
                # Step 9: Incorrect input
                client_socket.send("Incorrect input\n".encode())

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        client_socket.close()
