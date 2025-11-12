# PASSWORD MANAGER - MESSY VERSION
import random
import string


print("Password Manager v1.0")
print("=" * 30)


def main():
    passwords={}
    

    
    while True:
        display_menu()
        action =get_menu_choice()
    
        if action == "1":
            add_password(passwords)
            
        elif action == "2":
            get_password(passwords)
                
        elif action == "3":
            generate_password(passwords)
                
        elif action == "4":
            list_sites(passwords)
                    
        elif action == "5":
            exit_program(passwords)
            break

def display_menu():
    print("\n1. Add password")
    print("2. Get password")
    print("3. Generate password")
    print("4. List all sites")
    print("5. Exit")    
def get_menu_choice():
    return input("\nWhat do you want to do? ")

    
    
def add_password(passwords):
        site = input("Site name: ")
        if site in passwords:
            overwrite = input(f"{site} already exists. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                return
        username = input("Username: ")
        password = input("Password: ")
        passwords[site] = {'username': username, 'password': password}
        print(f"Password for {site} saved!")
def get_password(passwords):
    site = input("Site name: ")
    if site in passwords:
            print(f"\nSite: {site}")
            print(f"Username: {passwords[site]['username']}")
            print(f"Password: {passwords[site]['password']}")
    else:
            print(f"No password found for {site}")
def generate_password(passwords):
        length = input("Password length (default 16): ")
        if length == "":
            length = 16
        else:
            length = int(length)
        include_symbols = input("Include symbols? (y/n): ")
        
        chars = string.ascii_letters + string.digits
        if include_symbols.lower() == 'y':
            chars += string.punctuation
            
        password = ''
        for _ in range(length):
            password += random.choice(chars)
            
        print(f"\nGenerated password: {password}")
        save = input("Save this password? (y/n): ")
        if save.lower() == 'y':
            site = input("Site name: ")
            username = input("Username: ")
            passwords[site] = {'username': username, 'password': password}
            print("Saved!")
def list_sites(passwords):
        if not passwords:
            print("No passwords saved yet!")
        else:
            print("\nSaved sites:")
            for site in passwords:
                print(f"- {site}")
def exit_program(passwords):
        save = input("Save before exit? (y/n): ")
        if save.lower() == 'y':
            with open("passwords.txt", "w") as f:
                for site, info in passwords.items():
                    f.write(f"{site}:{info['username']}:{info['password']}\n")
            print("Saved to passwords.txt")
        print("Goodbye!")
        

if __name__=="__main__":
     main()
