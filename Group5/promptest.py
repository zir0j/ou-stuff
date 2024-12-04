from prompt_toolkit import prompt

# Initial input
user_input = prompt("Please enter some text: ")
print(f"You entered: {user_input}")

# Loop to continue editing the text
while True:
    # Prompt with the current text as the default value
    user_input = prompt(f"Edit your text (current: {user_input}): ", default=user_input)
    
    print(f"Updated text: {user_input}")

    # Ask if the user wants to continue editing
    continue_editing = input("Do you want to continue editing? (y/n): ").strip().lower()
    if continue_editing != 'y':
        break

print("Final text:", user_input)
