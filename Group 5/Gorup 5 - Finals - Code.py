###############
## LIBRARIES ##
###############






################



################
## FUNCTIONS GO HERE ##

def diary_entry():
    writing_proper = input("Share me your thoughts! Press enter when you're done.") # Bakla function na lang na while loop ulit HAHAHAHA
    menu_for_saving = input("Are you happy with what you write?")
    while True:
        try:
            if menu_for_saving == "Yes":
                file_password = input("Insert the password for this entry:")    # Concat maybe?
                ## Function for file manipulation for writing_proper ##
                break
            elif menu_for_saving == "No":
                writing_proper
                pass
                break
            else:
                print("Hmmm i didn't recognize that.")  #Should loop back to where they were writing?
                writing_proper
        except:
            print("Hmmm that seems to not be there lol.")

def diary_archives():
    ## TO RESEARCH ##
    ## User can view or edit files ##
    user_choice_2 = input("What would you like to do?")

    print("1. View your entries")
    print("2. Edit your entries")

    while True:
        try:
            if user_choice_2 == 1:
                pw_input_for_viewing = input("Please type the password of the entry you wish to edit: ")
                break
            elif user_choice_2 == 2:
                pw_input_for_edit = input("Please type the password of the entry you wish to edit: ")
                break
            else:
                print("Hmm idk that one.")
                continue
        except:
            print("Hmmm this doesn't belong here. You might have to restart.")

def about_creators():
    print("This diary was amde by Group 5. For inquireis, message us at blahg blah blah")

################
################


####################
###     MENU     ###
####################

def menu():
    while True:
        try:
            user_choice_1 = input("What would you want to do?") #  Function
            
            ## ADD ASCII ART FOR INTERFACE ##
            print("1. Write")
            print("2. View/Edit")
            print("3. About the program")
            print(user_choice_1)

            if user_choice_1 == 1:
                diary_entry()
                break
            elif user_choice_1 == 2:
                diary_archives()
                break
            elif user_choice_1 == 3:
                about_creators()
                break
            else:
                print("Hmmm i didnt get that.")
                user_choice_1
        except:
            print("Woops! Restart the terminal")


menu()      # Open the program when run on terminal
