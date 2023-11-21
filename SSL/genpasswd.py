import hashlib
import datetime
import os

def get_user_id():
    while True:
        user_id = input("Enter ID: ")
        if user_id.islower() and user_id.isalpha():
            return user_id
        print("The ID should only contain lower-case letters")

def get_password():
    while True:
        password = input("Enter Password: ")
        if len(password) >= 8:
            return password
        print("The password should contain at least 8 characters")

def user_exists(user_id):
    if not os.path.exists('hashpasswd'):
        return False
    with open('hashpasswd', 'r') as file:
        for line in file:
            existing_id, _, _ = line.split(maxsplit=2)
            if existing_id == user_id:
                return True
    return False

def add_user(user_id, hashed_password):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('hashpasswd', 'a') as file:
        file.write(f"{user_id} {hashed_password} {timestamp}\n")

def main():
    while True:
        user_id = get_user_id()
        if user_exists(user_id):
            print("The ID already exists")
        else:
            password = get_password()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            add_user(user_id, hashed_password)
        if input("Would you like to enter another ID and Password (Y/N)? ").lower() != 'y':
            break

if __name__ == "__main__":
    main()
