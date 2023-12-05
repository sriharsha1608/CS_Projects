import socket
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes

def encrypt_with_rsa(public_key, plaintext):
    cipher_rsa = PKCS1_OAEP.new(public_key)
    ciphertext = cipher_rsa.encrypt(plaintext)
    return ciphertext


def encrypt_with_des(key, plaintext):
    cipher_des = DES.new(key, DES.MODE_ECB)  # ECB mode for simplicity (not recommended for production)
    # Pad the plaintext to be a multiple of 8 bytes (DES block size)
    while len(plaintext) % 8 != 0:
        plaintext += b' '
    ciphertext = cipher_des.encrypt(plaintext)
    return ciphertext


# Load the bank's public key
with open("bank_public_key.pem", "rb") as key_file:
    bank_public_key = RSA.import_key(key_file.read())

# Create a socket for the ATM
atm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
atm_socket.connect(("localhost", 12345))

while True:
    # Step 2: Prompt the user for ID and password
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Step 3: Generate symmetric key K and send encrypted credentials to the server
    symmetric_key = get_random_bytes(8)

    encrypted_symmetric_key = encrypt_with_rsa(bank_public_key, symmetric_key)
    up=username+' '+password
    encrypted_credentials = encrypt_with_des(symmetric_key, up.encode())
    atm_socket.send(encrypted_symmetric_key)
    atm_socket.send(encrypted_credentials)

    # Step 4: Receive and display the server's response
    response = atm_socket.recv(256).decode()
    print("hello:",response," ",len(response))

    if response == "ID and password are correct":
        while True:
            # Handle the main menu options (Steps 5 to 9)
            choice = input(
                "Please select one of the following actions (enter 1, 2, or 3):\n1. Transfer money\n2. Check account balance\n3. Exit\n"
            )
            atm_socket.send(choice.encode())

            if choice == "1":
                # Handle money transfer (Step 6)
                while True:

                    account_choice = input("Please select an account (enter 1 or 2):\n1. Savings\n2. Checking\n")
                    atm_socket.send(account_choice.encode())

                    resp = atm_socket.recv(256).decode()
                    if resp=='Incorrect input':
                        print("Incorrect input\n")
                        continue
                    else:
                        break

                recipient_username = input("Enter recipient's username: ")
                atm_socket.send(recipient_username.encode())

                transfer_amount = input("Enter the amount to transfer: ")
                if transfer_amount.isdigit():
                    atm_socket.send(transfer_amount.encode())

                    response = atm_socket.recv(256).decode()
                    print(response)
                else:
                    print("Amount should be digits")
                    continue

            elif choice == "2":
                # Check account balance (Step 7)
                balance_response = atm_socket.recv(256).decode()
                print(balance_response)

            elif choice == "3":
                # Exit (Step 8)
                atm_socket.close()
                exit()
            else:
                # Incorrect input (Step 9)
                print("Incorrect input")
