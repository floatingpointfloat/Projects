import string
import random

characters = list(string.ascii_letters + string.digits)

def generate_password(length):
    password = ''
    for i in range(length):
        if i % 6 == 0 and i != 0:
            password += '-'
        else:
            password += characters[random.randint(0, len(characters) - 1)]
    return password

if __name__ == '__main__':
    while True:
        try:
            length = int(input("Enter the length of your password: "))
            if length < 6:
                print("Length must be at least 6 characters long.")
                continue
            password = generate_password(length)
            print(f"Your password is: {password}")
            if input("Do you want to generate another password? (y/n): ").lower() != 'y':
                break
        except ValueError:
            print("Please enter a valid number.")