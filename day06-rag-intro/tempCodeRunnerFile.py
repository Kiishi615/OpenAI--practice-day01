reply= get_ai_response(client, messages)

        messages.append({"role":"assistant", "content":reply})
        

        display_response(reply)
