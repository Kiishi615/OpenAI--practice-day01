from jokeapi import Jokes
import asyncio, requests, json

async def print_joke():
    try:
        j = await Jokes()  # Initialise the class
        joke = await j.get_joke(category=['programming', 'dark'], amount= 5)
        for each_joke in joke["jokes"]:
            if each_joke["type"] == "single": # Print the joke
                print(f"\n{each_joke["joke"]}")
            else:
                print(each_joke["setup"])
                print(f"{each_joke["delivery"]}\n")
    except requests.Timeout :
        print("Request timeout")
    except requests.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
    except requests.RequestException as e:
        print(f"Network error: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON decode")

asyncio.run(print_joke())