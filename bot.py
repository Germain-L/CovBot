import discord
import json
import inspect
import api


API = api.API()


def start():
    bot = MyBot()
    bot.run(read_token())


def read_token() -> str:
    # keeps token secret from git
    with open('./files/secret.json') as f:
        data = json.load(f)
        return data["token"]


def format_number(number) -> str:
    # this somehow splits number by groups of 3 and re-reverses back to normal
    # https://www.geeksforgeeks.org/python-split-string-in-groups-of-n-consecutive-characters/
    # if you can explain this, make a PR :D
    formatted_number = number
    formatted_number = [(formatted_number[i:i + 3]) for i in range(0, len(formatted_number), 3)][::-1]
    formatted_number = ' '.join(formatted_number)
    return formatted_number


class MyBot(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    @staticmethod
    async def on_message(message):
        # prefix used by bot to detect commands
        prefix = "?"

        # find first character in message
        prefix_message = message.content[0]

        # end function if prefixes don't match
        if prefix_message != prefix:
            return 0

        # remove prefix from commands
        message.content = message.content[1:]

        # splits arguments into an array where ' ' are found in the message
        args = [i.lower() for i in message.content.split()]

        if args[0] == "stats":
            # if no country specified, display worldwide stats
            if len(args) == 1:

                # get worldwide stats
                world = API.summary_worldwide()

                if "error" not in world:
                    # reverse each number and store in array
                    cases = [
                        str(world["TotalConfirmed"])[::-1],
                        str(world["TotalDeaths"])[::-1],
                        str(world["TotalRecovered"])[::-1]
                    ]

                    str_to_send = ""

                    count = 0
                    for case_type in cases:
                        formatted_string = format_number(case_type)

                        # add message to string
                        if count == 0:
                            str_to_send += "Total confirmed" + ': ' + formatted_string + '\n'
                        elif count == 1:
                            str_to_send += "Total deaths" + ': ' + formatted_string + '\n'
                        elif count == 2:
                            str_to_send += "Total recovered" + ': ' + formatted_string + '\n'

                        count += 1

                    # send message to channel
                    await message.channel.send(str_to_send)

                else:
                    # sends error back to user
                    await message.channel.send("Error occurred: {0}".format(world["error"]))
            else:
                country_code = args[1].upper()

                data = API.summary_by_country(country_code)

                if "error" not in data:
                    data_to_send = {
                        "new_confirmed": data["NewConfirmed"],
                        "total_confirmed": data["TotalConfirmed"],
                        "new_deaths": data["NewDeaths"],
                        "total_deaths": data["TotalDeaths"],
                        "new_recovered": data["NewRecovered"],
                        "total_recovered": data["TotalRecovered"],
                    }

                    # formats number
                    for number in data_to_send:
                        data_to_send[number] = format_number(str(data_to_send[number]))

                    # add country name
                    data_to_send["Country"] = data["Country"]

                    # create string to send back
                    string_to_send = """Statistics for {6}:
                    
                        new cases: {0},
                        total cases: {1}
                        
                        new deaths: {2}
                        total deaths: {3}
                        
                        newly recovered: {4}
                        total recovered: {5}
                    """.format(
                        data_to_send["new_confirmed"],
                        data_to_send["total_confirmed"],
                        data_to_send["new_deaths"],
                        data_to_send["total_deaths"],
                        data_to_send["new_recovered"],
                        data_to_send["total_recovered"],
                        data_to_send["Country"]
                    )

                    # remove wacky indents from string
                    string_to_send = inspect.cleandoc(string_to_send)

                    await message.channel.send(string_to_send)

                else:
                    await message.channel.send("Error occurred: {0}".format(data["error"]))


start()