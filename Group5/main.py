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
from prompt_toolkit import prompt

###############


#######################
## FUNCTIONS GO HERE ##
#######################

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
    special_characters = {'@', '#', '!', '~', '$', '%', '^', '&', '*', '(', ')', '-', '+', '/', ':', '.', ',', '<', '>', '?', '|'}
    while True:
        # Prompt the user to input a password
        file_password = pwinput("Insert the password for this entry >> ")
        # Validate the password length
        if not (8 <= len(file_password) <= 16):
            print("Password must be between 8 and 16 characters. Let's try that again.")
            continue
        # Check for at least one special character
        if not any(c in special_characters for c in file_password):
            print("Password must contain at least one of any special characters (@#!~$%^&*()-+/:.,'<>?|). Let's try that again.")
            continue
        # Ask the user to re-enter the password
        reenter_password = pwinput("Reenter the password: ")
        # Validate if the passwords match
        if file_password != reenter_password:
            print("Passwords do not match. Let's try that again.")
            continue
        # If all validations pass, return the password
        print("Password accepted.")
        return file_password.encode('UTF-8')

# Save the metadata for entries (JSON for simplicity and security)
def load_database():
    if not os.path.exists("database.json"):
        with open("database.json", "w") as db_file:
            json.dump({}, db_file)
    with open("database.json", "r") as db_file:
        return json.load(db_file)

# Save any user input into encrypted data in the JSON file
def save_database(database):
    with open("database.json", "w") as db_file:
        json.dump(database, db_file)

def count_words(text):
    return len(text.split())

database = load_database()

# Function for the user to write their innermost thoughts, desires, etc.
def diary_entry():
    writing_proper = prompt("Share to me your thoughts! Press enter when you're done or type Cancel to go back to main menu.\n")
    word_count = count_words(writing_proper)
    if writing_proper.lower() == "cancel":
        return
    print(f"---Your new entry has {word_count} words.---")
    while True:
        menu_for_saving = input("Are you happy with what you wrote? (Y)es or (N)o >> ")
        if menu_for_saving[0].lower() == "y":
            entry_name = input("Enter the name of your diary entry >> ")
            file_password = get_password_input()
            # Generates random salt characters as added layer of security for password input.
            salt = os.urandom(16)
            cipher = create_fernet_object_using_password(salt=salt, password=file_password)
            encrypted_data = cipher.encrypt((writing_proper).encode()).decode("utf-8")
            # Creates dictionary for JSON file
            database[entry_name] = {
                "data": encrypted_data, 
                "salt": base64.b64encode(salt).decode("utf-8"),
                "word_count": word_count
            }
            save_database(database)
            print("Entry saved securely!")
            break
        # Returns where user left off. 
        writing_proper = prompt("Pick up where you left off! >> ", default=writing_proper)

def diary_archives():
    print("\nView/Edit/Delete")
    print("1. View your entries")
    print("2. Edit your entries")
    print("3. Delete your entries")
    print("4. Change Title")
    print("5. Go Back to Main Menu")

    while True:
        user_choice_2 = input("What would you like to do? Type the number of what you want to do >>")
        try:
            if user_choice_2 == "1":
                list_entries()
                entry_name = input("Enter the name of the diary entry you'd like to view >> ")
                # Added for case-insensitivity
                entry_name_lower = entry_name.lower()
                entry_match = next((name for name in database if name.lower() == entry_name_lower), None)
                if entry_match:
                    entry = database[entry_match]
                    pw_input_for_viewing = pwinput("Please type the password of the entry you wish to view: ").encode()
                    salt = base64.b64decode(entry["salt"].encode())
                    cipher = create_fernet_object_using_password(salt = salt, password= pw_input_for_viewing)
                    # Checks if passowrd of entry matches 
                    try:
                        decrypted_data = cipher.decrypt(entry["data"]).decode()
                        print("Your entry: ", entry_name)
                        print(decrypted_data)
                        print(f"---Your edited entry has: {entry['word_count']} words---")
                        diary_archives()
                    except Exception as e:
                        print("You have entered the wrong password! Try again.")
                        diary_archives()
                # Checks if entry is found or not
                else:
                    print("Entry not found!")
                    diary_archives()
                    return
            elif user_choice_2 == "2":
                list_entries()
                entry_name = input("Enter the name of the diary entry you'd like to edit >> ")
                entry_name_lower = entry_name.lower()
                entry_match = next((name for name in database if name.lower() == entry_name_lower), None)
                if entry_match:
                    entry = database[entry_match]
                    pw_input_for_edit = pwinput("Please type the password of the entry you wish to edit >> ").encode()
                    salt = base64.b64decode(entry["salt"].encode())
                    cipher = create_fernet_object_using_password(salt = salt, password= pw_input_for_edit)
                    # IF successful, it'll decrypt the data of the entry to be changed
                    try:
                        decrypted_data = cipher.decrypt(entry["data"]).decode()
                        print("Your entry: ")
                        print(decrypted_data)
                        print("\nOptions:")
                        print("1. Continue to write at the bottom part?")
                        print("2. Overwrite the entire entry?")
                        edit_choice = input("Choose an option by typing (1) or (2) >> ")
                        # Adds additional sentences, words, etc, for entry
                        if edit_choice == "1":
                            append_text = input("Enter the words you would like to add: ")
                            new_entry = decrypted_data + "\n" + append_text
                        
                        # Overwrites all of the entry
                        elif edit_choice == "2":
                            new_entry = input("Overwrite the new entry >> ")

                        # If choise was not made.
                        else:
                            print("Invalid choice. No changes made.")
                            return
                        
                        # New entry upon editing
                        print("Below is the new data for your file: ", entry_name)
                        print(new_entry)
                        word_count = count_words(new_entry)
                        encrypted_data = cipher.encrypt(new_entry.encode()).decode("utf-8")
                        database[entry_name] = {
                            "data": encrypted_data,
                            "salt": base64.b64encode(salt).decode("utf-8"),
                            "word_count": word_count
                        }
                        save_database(database)
                        print(f"---Entry updated successfully! Word count: {word_count}---")
                        diary_archives()
                        return
                    except Exception as e:
                        print("You have entered the wrong password!\n Try again!")
                        return
                else:
                    print("Entry not found!")
                    diary_archives()
                    return
            elif user_choice_2 == "3":
                list_entries()
                entry_name = input("Enter the name of the diary entry you'd like to delete >> ")
                entry_name_lower = entry_name.lower()
                entry_match = next((name for name in database if name.lower() == entry_name_lower), None)
                if entry_match:
                    entry = database[entry_match]
                    pw_input_for_edit = pwinput("Please type the password of the entry you wish to delete >> ").encode()
                    salt = base64.b64decode(entry["salt"].encode())
                    cipher = create_fernet_object_using_password(salt = salt, password= pw_input_for_edit)
                    # Decrypts data to be deleted and removes it. 
                    try:
                        decrypted_data = cipher.decrypt(entry["data"]).decode()
                        database.pop(entry_match)
                        save_database(database)
                        print(f"---Entry deleted successfully!---")
                        diary_archives()
                    # Stops deletion when wrong password is entered
                    except Exception as e:
                        print("You have entered the wrong password!")
                        diary_archives()
                        return
                # Stops when no entry is found in user input.
                else:
                    print("Entry not found!")
                    diary_archives()
                    return
            if user_choice_2 == "4":
                list_entries()
                entry_name = input("Enter the entry you want to change the title of >> ")
                if entry_name in database:
                    entry = database[entry_name]
                    pw_input_for_edit = pwinput("Please type the password of the entry you wish to change the title of >> ").encode()
                    salt = base64.b64decode(entry["salt"].encode())
                    cipher = create_fernet_object_using_password(salt=salt, password=pw_input_for_edit)
                    try:
                        # Decrypts entry to have title change
                        decrypted_data = cipher.decrypt(entry["data"]).decode()
                        print(f"Current entry content: {decrypted_data}") 
                        new_title = input("Enter the new title: ")
                        # Add the entry under the new title
                        database[new_title] = {
                            "data": entry["data"],  # Use existing encrypted data
                            "salt": entry["salt"],
                            "word_count": entry["word_count"]
                        }
                        # Remove the old title
                        del database[entry_name]
                        save_database(database)
                        print(f"---Title changed successfully! New title: {new_title}---")
                    except Exception as e:
                        print("You have entered the wrong password!")
                    return
                else:
                    print("Entry not found!")
                    return
            elif user_choice_2 == "5":
                return
        except Exception as e:
            print(f"Invalid Choice. Try Again.: {e}")
            diary_archives()
            return     
        break

def about_creators():
    # Learns more about the program creatores
    print("\nAbout the Program")
    print("Lock It is a secure digital diary that encrypts your entries as non-human-readable files, ensuring that only you can access your private thoughts. Through the use of encryption and password input, it creates a safe and protected repository for your personal reflections.")
    print("The program also features a simple game loop, adding a touch of fun to the journaling experience. With Lock It, you have full control over your content, keeping it secure from unauthorized access.")
    # Data privacy statement
    print("\nData Privacy Disclosure")
    print("• No Personal Information Collected: We do not collect names, email addresses, phone numbers, or any other identifying data.")
    print("• No Data Usage Tracking: There is no tracking of how users interact with the program.")
    print("• Local Storage: All data remains on the user’s device and is not transmitted elsewhere.")
    print("• Security: The program uses encryption to protect data locally on your device.")
    print("• No External Access: Data is not accessible from outside the user’s device.")
    print("\nThis diary was made by Group 5. For inquiries, message:")
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
    print("All rights reserved (c) 2024")

# Returns all list entries from database
def list_entries():
    print("Your saved entries:")
    for entry_name, entry_details in database.items():
        word_count = entry_details.get("word_count", "Empty")
        print(f"{entry_name}  |  Word Count: {word_count}")

# Function for password changes.
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
###      MENU      ###
######################

def menu():
    while True:
        try:
            tprint("LockIt!")                       # ASCII Art for logo of diary program
            print("==The diary with a lock==")
            print("\nWhat would you want to do?")
            print("1. Write")
            print("2. View/Edit/Delete")
            print("3. Change Password")
            print("4. About the program")
            print("5. Exit Program!")
            user_choice_1 = input("Enter your choice by typing the number of what you want to do: ")
            match user_choice_1:                    # Match-case for efficiency
                case "1":
                    diary_entry()
                case "2":
                    diary_archives()
                case "3":
                    change_password()
                case "4":
                    about_creators()
                case "5":
                    print("Okay! Have a nice day!")
                    return
                case _:
                    print("Hmmm, I didn't get that.")
                    continue
        except Exception as e:
            print(f"Woops! Restart the terminal. Error: {e}")
            
menu()