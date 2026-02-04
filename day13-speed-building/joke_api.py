from jokeapi import Jokes
import asyncio

async def print_joke():
    j = await Jokes()  # Initialise the class
    joke = await j.get_joke(category=['programming', 'dark'], amount= 5)
    for each_joke in joke["jokes"]:
        if each_joke["type"] == "single": # Print the joke
            print(f"\n{each_joke["joke"]}")
        else:
            print(each_joke["setup"])
            print(f"{each_joke["delivery"]}\n")

asyncio.run(print_joke())