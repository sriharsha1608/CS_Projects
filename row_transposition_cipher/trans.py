import sys

def validate_key(keylength, key):
    if len(key) != keylength:
        print("Key length does not match specified keylength.")
        sys.exit(1)

    expected_digits = set(str(i) for i in range(1, keylength + 1))
    if set(key) != expected_digits:
        print("Key must include all digits from 1 to keylength exactly once.")
        sys.exit(1)

def read_file(filename):    
    with open(filename, 'r') as file:
        content = file.read().strip()
        if not all(char.islower() or char.isdigit() for char in content) or ' ' in content:
            print(f'The file {filename} must contain only lowercase letters (a-z) or digits (0-9).')
            sys.exit(1)
        return content
    

def write_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def encrypt(message, key):
    num_rows = len(message) // len(key) + (len(message) % len(key) != 0)
    matrix = [['z'] * len(key) for _ in range(num_rows)]

    row, col = 0, 0
    for char in message:
        matrix[row][col] = char
        col += 1
        if col == len(key):
            col = 0
            row += 1

    columns = [''] * len(key)
    for i, digit in enumerate(key):
        digit = int(digit)
        columns[i] = ''.join(matrix[row][digit - 1] for row in range(num_rows))

    ciphertext = ''.join(columns)
    return ciphertext

def decrypt(ciphertext, key):
    num_columns = len(key)
    num_rows = len(ciphertext) // num_columns
    grid = [['' for _ in range(num_columns)] for _ in range(num_rows)]
    index = 0
    for col in range(num_columns):
        col_index = int(key[col]) - 1
        for row in range(num_rows):
            grid[row][col_index] = ciphertext[index]
            index += 1

    plaintext = ''
    for row in range(num_rows):
        for col in range(num_columns):
            plaintext += grid[row][col]

    return plaintext

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python trans.py <keylength> <key> <inputfile> <outputfile> <enc/dec>")
        sys.exit(1)

    keylength = int(sys.argv[1])
    key = sys.argv[2]
    inputfile = sys.argv[3]
    outputfile = sys.argv[4]
    mode = sys.argv[5]

    validate_key(keylength, key)

    if mode == 'enc':
        plaintext = read_file(inputfile)
        ciphertext = encrypt(plaintext, key)
        write_file(outputfile, ciphertext)
        print("Encryption successful.")
    elif mode == 'dec':
        ciphertext = read_file(inputfile)
        plaintext = decrypt(ciphertext, key)
        write_file(outputfile, plaintext)
        print("Decryption successful.")
    else:
        print("Invalid mode. Use 'enc' for encryption or 'dec' for decryption.")
        sys.exit(1)
