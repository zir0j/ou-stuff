###############
## LIBRARIES ##
###############
import os
import json
from cryptography.fernet import Fernet
from getpass import getpass
# from art import *

###############


################
## FUNCTIONS GO HERE ##

# Generate or load the encryption key
def load_key():
    if not os.path.exists("key.key"):
        key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(key)
    else:
        with open("key.key", "rb") as key_file:
            key = key_file.read()
    return key

cipher = Fernet(load_key())

# Save the metadata for entries (JSON for simplicity)
def load_metadata():
    if not os.path.exists("metadata.json"):
        with open("metadata.json", "w") as meta_file:
            json.dump({}, meta_file)
    with open("metadata.json", "r") as meta_file:
        return json.load(meta_file)

def save_metadata(metadata):
    with open("metadata.json", "w") as meta_file:
        json.dump(metadata, meta_file)

metadata = load_metadata()

def diary_entry():
    writing_proper = input("Share me your thoughts! Press enter when you're done. >>>") 
    menu_for_saving = input("Are you happy with what you wrote? Only input Yes or No: ")
    while True:
        try:
            if menu_for_saving.lower() == "Yes":
                file_password = getpass("Insert the password for this entry:") 
                file_name = f"entry_{len(metadata) + 1}.dat"  # Unique file name for each entry
                encrypted_data = cipher.encrypt((file_password + '\n' + writing_proper).encode())
                with open(file_name, "wb") as entry_file:
                    entry_file.write(encrypted_data)
                metadata[file_name] = {"password": cipher.encrypt(file_password.encode()).decode()}
                save_metadata(metadata)
                print("Entry saved securely!")
                break
            elif menu_for_saving.lower() == "No":
                print("Rewriting your entry...")
                diary_entry()  # Restart the entry process
                break
            else:
                print("Hmmm i didn't recognize that.")
                break  
        except Exception as e:
            print(f"Hmmm that seems to not be there lol. Error: {e}")

def diary_archives():
    print("1. View your entries")
    print("2. Edit your entries")
    user_choice_2 = input("What would you like to do? Only type the number of your selection.")
    try:
        if user_choice_2 == "1":
            list_entries()
            file_name = input("Enter the file name of the entry you'd like to view: ")
            if file_name not in metadata:
                print("File not found!")
                return
            pw_input_for_viewing = getpass("Please type the password of the entry you wish to view: ")
            with open(file_name, "rb") as entry_file:
                encrypted_data = entry_file.read()
                decrypted_data = cipher.decrypt(encrypted_data).decode()
            if not decrypted_data.startswith(pw_input_for_viewing):
                print("Incorrect password!")
                return
            print("Your entry:")
            print(decrypted_data.split("\n", 1)[1])
        elif user_choice_2 == "2":
            list_entries()
            file_name = input("Enter the file name of the entry you'd like to edit: ")
            if file_name not in metadata:
                print("File not found!")
                return
            pw_input_for_edit = getpass("Please type the password of the entry you wish to edit: ")
            with open(file_name, "rb") as entry_file:
                encrypted_data = entry_file.read()
                decrypted_data = cipher.decrypt(encrypted_data).decode()
            if not decrypted_data.startswith(pw_input_for_edit):
                print("Incorrect password!")
                return
            new_entry = input("Enter your updated entry: ")
            new_data = pw_input_for_edit + "\n" + new_entry
            with open(file_name, "wb") as entry_file:
                entry_file.write(cipher.encrypt(new_data.encode()))
            print("Entry updated successfully!")
        else:
            print("Hmm, I don't know that one.")
            return
    except Exception as e:
        print(f"Hmmm this doesn't belong here. Error: {e}")

def about_creators():
    print("This diary was amde by Group 5. For inquiries, message us at blahg blah blah")

def list_entries():
    print("Your saved entries:")
    for entry in metadata.keys():
        print(entry)

def change_password():
    list_entries()
    file_name = input("Enter the file name of the entry you'd like to change the password for: ")
    if file_name in metadata:
        old_password = getpass("Enter the current password: ")
        with open(file_name, "rb") as entry_file:
            encrypted_data = entry_file.read()
            decrypted_data = cipher.decrypt(encrypted_data).decode()
            if decrypted_data.startswith(old_password):
                new_password = getpass("Enter the new password: ")
                new_data = new_password + "\n" + decrypted_data.split("\n", 1)[1]
                with open(file_name, "wb") as entry_file:
                    entry_file.write(cipher.encrypt(new_data.encode()))
                metadata[file_name]["password"] = cipher.encrypt(new_password.encode()).decode()
                save_metadata(metadata)
                print("Password updated successfully!")
            else:
                print("Incorrect current password!")
    else:
        print("File not found!")

######################
###     MENU     ###
######################

def menu():
    ascii_menu_heading = print("Diary. <3")
    while True:
        try:
            print(ascii_menu_heading)
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
