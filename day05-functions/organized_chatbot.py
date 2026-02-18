from file_functions import read_text_file, save_text_file

from shared import (display_response, get_ai_response, get_user_file,
                    get_user_input, load_config, save_chat_log, setup_api)


def main():
    # 1. Setup
    config = load_config()
    client = setup_api()

    # 2. File to read
    filename = get_user_file()
    messages= []
    file_content = read_text_file(filename)
    if file_content:
        print(f"---- Loaded content from {filename}----")
        messages.append({"role":"system", "content": file_content})

    

    #3. The Chat bot
    while True:
        user_input = get_user_input()
        if not user_input:
            continue
        
        #4. Exitting the bot
        if user_input.lower()=="quit":
            print("Saving chat log...")
            save_name = input("Enter filename to save log: ")
            save_chat_log(messages, save_name)
            break
        
        
        ## Code continues
        messages.append({"role":"user", "content": user_input})

        
        reply = get_ai_response(client, messages, config)

        messages.append({"role":"assistant", "content":reply})
        display_response(reply)
if __name__=="__main__":
    main()