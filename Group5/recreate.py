###############
## LIBRARIES ##
###############
import os
import json
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from getpass import getpass
from pwinput import pwinput
from art import *
from tabulate import tabulate

###############


################
## FUNCTIONS GO HERE ##

# Generate or load the encryption key
def create_fernet_object_using_password(salt, password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return Fernet(key)

def get_password_input():
    file_password = "first"
    reenter_password = "second"
    while file_password != reenter_password:
        file_password = pwinput("Insert the password for this entry: ")
        reenter_password = pwinput("Reenter the password: ")

        if file_password != reenter_password:
            print("Let's try that again.")
    
    return file_password.encode('UTF-8')


# Save the metadata for entries (JSON for simplicity)
def load_database():
    if not os.path.exists("database.json"):
        with open("database.json", "w") as db_file:
            json.dump({}, db_file)
    with open("database.json", "r") as db_file:
        return json.load(db_file)

def save_database(database):
    with open("database.json", "w") as db_file:
        json.dump(database, db_file)

database = load_database()

def diary_entry():
    writing_proper = input("Share to me your thoughts! Press enter when you're done.\n") 
    menu_for_saving = input("Are you happy with what you wrote? (Y)es or (N)o: ")
    while True:
        try:
            if menu_for_saving[0].lower() == "y":
                entry_name = input("Enter the name of diary entry: ")
                file_password = get_password_input()
                salt = os.urandom(16)
                cipher = create_fernet_object_using_password(salt=salt, password=file_password)
                encrypted_data = cipher.encrypt((writing_proper).encode()).decode("utf-8")
                database[entry_name] = {"data": encrypted_data, "salt": base64.b64encode(salt).decode("utf-8")}
                save_database(database)
                print("Entry saved securely!")
                break
            elif menu_for_saving[0].lower() == "n":
                print("Rewriting your entry...")
                diary_entry()  # Restart the entry process
                break
            else:
                print("Hmmm, I didn't recognize that.")
                menu_for_saving = input("Are you happy with what you wrote? (Y)es or (N)o: ")
        except Exception as e:
            print(f"Hmmm, that seems to not be there lol. Error: {e}")

def diary_archives():
    print("1. View your entries")
    print("2. Edit your entries")
    user_choice_2 = input("What would you like to do? ")

    while True:
        try:
            if user_choice_2 == "1":
                list_entries()
                entry_name = input("Enter the name of the diary entry you'd like to view: ")
                if entry_name in database:
                    entry = database[entry_name]
                    pw_input_for_viewing = pwinput("Please type the password of the entry you wish to view: ").encode()
                    salt = base64.b64decode(entry["salt"].encode())
                    cipher = create_fernet_object_using_password(salt = salt, password= pw_input_for_viewing)
                    try:
                        decrypted_data = cipher.decrypt(entry["data"]).decode()
                        print("Your entry: ")
                        print(decrypted_data)
                    except Exception as e:
                        print("You have entered the wrong password!")
                else:
                    print("Entry not found!")
                break
            elif user_choice_2 == "2":
                list_entries()
                entry_name = input("Enter the name of the diary entry you'd like to edit: ")
                if entry_name in database:
                    entry = database[entry_name]
                    pw_input_for_edit = pwinput("Please type the password of the entry you wish to edit: ").encode()
                    salt = base64.b64decode(entry["salt"].encode())
                    cipher = create_fernet_object_using_password(salt = salt, password= pw_input_for_edit)
                    try:
                        decrypted_data = cipher.decrypt(entry["data"]).decode()
                        print("Your entry: ")
                        print(decrypted_data)
                    except Exception as e:
                        print("You have entered the wrong password!")
                    
                    new_entry = input("Enter your updated entry: ")
                    encrypted_data = cipher.encrypt((new_entry).encode()).decode("utf-8")
                    database[entry_name] = {"data": encrypted_data, "salt": base64.b64encode(salt).decode("utf-8")}
                    save_database(database)
                    print("Entry updated successfully!")
                else:
                    print("Entry not found!")
                break
            else:
                print("Hmm idk that one.")
                continue
        except Exception as e:
            print(f"Hmmm this doesn't belong here. Error: {e}")

def about_creators():
    print("This diary was made by Group 5. For inquiries, message:")
    # List of program developers with email.
    developers = [
        {"Developers": "Edwin Aljibe","Email Address": "epaljibe@up.edu.ph"},
        {"Developers": "Kyne De Guzman","Email Address": "kvdeguzman3@up.edu.ph"},
        {"Developers": "Angelo Dela Fuente","Email Address": "austriadelafuente@gmail.com"},
        {"Developers": "Levi Ebora","Email Address": "lcebora@up.edu.ph"},
        {"Developers": "Christian Joriz Martinez (Ceej)","Email Address": "csmartinez@up.edu.ph"},
        {"Developers": "Alein Narca","Email Address": "adnarca@up.edu.ph"},
        {"Developers": "Alfred Olivan","Email Address": "aholivan@up.edu.ph"},
        {"Developers": "Jeanelle Lorelei Paat","Email Address": "japaat@up.edu.ph"},
        {"Developers": "Billy Jan Ponce (Bill)","Email Address": "bcponce@up.edu.ph"},
        {"Developers": "John Paul Punzalan","Email Address": "japunzalan@up.edu.ph"},
        {"Developers": "Jose Manuel Velarde","Email Address": "jyvelarde@up.edu.ph"},
    ]

    # Table format
    table = tabulate(developers, headers="keys", tablefmt="grid")

    # Table display
    print("PROGRAM DEVELOPERS:")
    print(table)

def list_entries():
    print("Your saved entries:")
    for entry in database.keys():
        print(entry)

def change_password():
    list_entries()
    entry_name = input("Enter the name of the diary entry you'd like to change the password for: ")
    if entry_name in database:
        old_password = pwinput("Enter the current password: ").encode()
        entry = database[entry_name]
        salt = base64.b64decode(entry["salt"].encode())
        cipher = create_fernet_object_using_password(salt = salt, password= old_password)
        try:
            decrypted_data = cipher.decrypt(entry["data"])
            new_password = get_password_input()
            new_cipher = create_fernet_object_using_password(salt = salt, password= new_password)
            encrypted_data = new_cipher.encrypt((decrypted_data)).decode("utf-8")
            database[entry_name]["data"] = encrypted_data
            save_database(database)
            print("Password updated successfully!")
        except Exception as e:
            print("You have entered the wrong password!")
    else:
        print("Entry not found!")

######################
###     MENU     ###
######################

def menu():
    ascii_menu_heading = tprint("Diary. <3")
    while True:
        try:
            print("\nWhat would you want to do?")
            print("1. Write")
            print("2. View/Edit")
            print("3. Change Password")
            print("4. About the program")
            user_choice_1 = input("Enter your choice: ")

            if user_choice_1 == "1":
                diary_entry()
            elif user_choice_1 == "2":
                diary_archives()
            elif user_choice_1 == "3":
                change_password()
            elif user_choice_1 == "4":
                about_creators()
            else:
                print("Hmmm, I didn't get that.")
        except Exception as e:
            print(f"Woops! Restart the terminal. Error: {e}")

menu()  # Open the program when run on terminal
