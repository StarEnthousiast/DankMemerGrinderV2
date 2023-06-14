import asyncio
import ctypes
import json
import os
import random
import sys

import discord.errors
import requests
from discord.ext import commands, tasks

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("dankmemergrindercli")
except AttributeError:
    pass

account_tasks = {}

commands_dict = {
    "trivia": "trivia",
    "dig": "dig",
    "fish": "fish",
    "hunt": "hunt",
    "pm": "postmemes",
    "beg": "beg",
    "pet": "pets",
    "hl": "highlow",
    "search": "search",
    "dep_all": "deposit",
    "stream": "stream",
    "work": "work",
    "daily": "daily",
    "crime": "crime",
    "adventure": "adventure",
}

config_example = {
    "state": False,
    "channel_id": "",
    "discord_token": "",
    "offline": False,
    "auto_vote": False,
    "alerts": False,
    "autobuy": {
        "lifesavers": {"state": True, "amount": 5},
        "fishing": False,
        "shovel": False,
        "rifle": False,
    },
    "commands": {
        "trivia": {"state": False, "delay": 5, "trivia_correct_chance": 0.75},
        "dig": {"state": False, "delay": 30},
        "fish": {"state": False, "delay": 30},
        "hunt": {"state": False, "delay": 30},
        "pm": {"state": False, "delay": 20},
        "beg": {"state": False, "delay": 40},
        "pet": {"state": False, "delay": 1800},
        "hl": {"state": False, "delay": 20},
        "search": {
            "state": False,
            "delay": 20,
            "priority": [
                "phoenix pits",
                "aeradella's home",
                "shadow's realm",
                "dog",
                "grass",
                "air",
                "kitchen",
                "dresser",
                "mail box",
                "bed",
                "couch",
                "pocket",
                "toilet",
                "washer",
                "who asked",
            ],
            "second_priority": ["fridge", "twitter", "vacuum"],
            "avoid": [
                "bank",
                "discord",
                "immortals dimension",
                "laundromat",
                "soul's chamber",
                "police officer",
                "tesla",
                "supreme court",
            ],
        },
        "dep_all": {"state": False, "delay": 30},
        "stream": {
            "state": False,
            "delay": 660,
            "order": [1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 2],
        },
        "work": {"state": False, "delay": 3600},
        "daily": {"state": False, "delay": 86400},
        "crime": {
            "state": False,
            "delay": 40,
            "priority": [
                "hacking",
                "tax evasion",
                "fraud",
                "eating a hot dog sideways",
                "trespassing",
            ],
            "second_priority": ["bank robbing", "murder"],
            "avoid": ["arson", "dui", "treason"],
        },
        "adventure": {"state": True, "delay": 1800, "adventure": "west"},
    },
    "autouse": {
        "state": False,
        "hide_disabled": False,
        "pizza_slice": {"state": False},
        "cowboy_boots": {"state": False},
        "lucky_horseshoe": {"state": False},
        "daily_box": {"state": False},
        "apple": {"state": False},
        "ammo": {"state": False},
        "energy_drink": {"state": False},
        "fishing_bait": {"state": False},
        "bank_note": {"state": False},
    },
}

global_config_example = {
    "min_click_delay": 400,
    "max_click_delay": 600,
    "min_commands_delay": 2500,
    "adventure": {
        "space": {
            "A friendly alien approached you slowly. What do you do?": "Attack",
            "A small but wise green alien approaches you.": "Do",
            "Oh my god even in space you cannot escape it": "69",
            "This planet seems to be giving off radioactive chemicals. What do you do?": (
                "Distant Scan"
            ),
            "Whaaaat!? You found a space kitchen! It looks like it is full of shady stuff. What do you do?": (
                "Inspect"
            ),
            "You accidentally bumped into the Webb Telescope. Oh god.": "Flee",
            "You come upon a dark pyramid shaped ship fighting a spherical white ball looking thing. What do you do?": (
                "Embrace Dark"
            ),
            "You encountered someone named Dank Sidious, what do you do?": "Do it",
            'You find a vending machine selling "Moon Pies". What do you do?': "Buy",
            "You flew past a dying star": "Flee",
            "You found a strange looking object. What do you do?": "Ignore",
            "You got abducted by a group of aliens, who are trying to probe you. What do you do?": (
                "Sit Back and Enjoy"
            ),
            "You ran out of fuel! What next?": "Urinate",
            "You see a shooting star!": "Wish",
            "You uh, just came across a pair of Odd Eyes floating around": "Flee",
            "You're picking up a transmission from deep space!": "*<)#%':]|##",
        },
        "west": {
            "A lady next to a broken down wagon is yelling for help.": "Ignore Her",
            "A snake is blocking your path. What do you want to do?": "Wait",
            "A stranger challenges you to a quick draw. What do you want to do?": (
                "Decline"
            ),
            "Someone is getting ambushed by bandits!": "Ignore them",
            "Someone on the trail is lost and asks you for directions.": "Ignore them",
            "You bump into someone near the horse stables. They challenge you to a duel": (
                "Run away"
            ),
            "You come across a saloon with a poker game going on inside. What do you want to do?": (
                "Join"
            ),
            "You entered the saloon to rest from the journey. What do you want to do?": (
                "Play the piano"
            ),
            "You find a dank cellar with an old wooden box": "Ignore it",
            "You find an abandoned mine. What do you want to do?": "Explore",
            "You found a stray horse. What do you want to do?": "Feed",
            "You get on a train and some bandits decide to rob the train. What do you do?": (
                "Don't hurt me!"
            ),
            "You see some bandits about to rob the local towns bank. What do you do?": (
                "Stop them"
            ),
            "You wander towards an old abandoned mine.": "Go in",
            "You're dying of thirst. Where do you want to get water?": "Cactus",
            "You're riding on your horse and you get ambushed. What do you do?": (
                "Run away"
            ),
            "Your horse sees a snake and throws you off. What do you do?": (
                "Find a new horse"
            ),
            "__**WANTED:**__": "Billy Bob Jr.",
        },
        "brazil": {
            "After a long day shopping for souvenirs in a crowded mall, you stop at the food court to grab some food. What do you order?": (
                "McDonald's"
            ),
            "On your way to the beach, you stop at a comer store to buy some drinks and notice a litle caramel-colored dog is sleeping outside. What do you do?": (
                "Pet the Dog"
            ),
            "While enjoying Carnival, you decide to go to the stadium to watch the samba schools perform. Where do you buy your tickets?": (
                "Online"
            ),
            "While traveling in the city, you hear about Snake Island and decide you have to see if it is really as bad as they say. The boat captain will take you there but demands more money if you want to dock. What do you do?": (
                "Stay on the Boat"
            ),
            "While visiting Rio Grande do Sul, you stop at one of the famous Brazilian steakhouses with all the meat you can eat. What do you want?": (
                "Broccoli"
            ),
            "While visiting São Paulo, you find a place to see capybaras. What do you do?": (
                "Pull up"
            ),
            "You can't get enough of the Brazilian beaches, and decide to spend the day exploring a remote one you found. What do you do first?": (
                "Go Swimming"
            ),
            "You can't visit Rio de Janeiro without touring the Christ the Redeemer statue. How do you get there?": (
                "Bus"
            ),
            "You decide to take an MMA class while visiting to learn from the best. Which style do you choose?": (
                "Capoiera"
            ),
            "You stop at a local bakery for some of the Brazilian cheese bread you've heard so much about. What else do you try?": (
                "Nothing"
            ),
            "You take a boat tour in Manaus to go down the Amazon River. At a fork in the path, the guide tells you to the right are piranhas and left anacondas. Which do you choose?": (
                "Piranhas"
            ),
            "You went to schedule a trip into the Amazon to see the animals. What sort of trip do you book?": (
                "Private Tour"
            ),
        },
        "vacation": {
            "A family road trip is a perfect getaway until you end up lost and without cell service. What do you do?": (
                "Keep Driving"
            ),
            "A family vacation can't be complete without a trip to an amusement park. What ride are you dying to try?": (
                "Waterslide"
            ),
            "A friend tells you about a quaint mountain resort, so you decide to spend a few days enjoying the snow. What do you do after you arrive?": (
                "Go Skiing"
            ),
            "Camping has always relaxed you, so you decide to vacation in the wilderness. What sort of camping do you prefer?": (
                "Rent an RV"
            ),
            "During your vacation in Lisbon, the hotel offers you a small pastry for breakfast. What do you do?": (
                "Pass"
            ),
            "Nothing can beat a romantic vacation in Paris. What do you want to do first?": (
                "Louvre"
            ),
            "You can't go on vacation without doing a little sightseeing. What do you want to see?": (
                "Museum"
            ),
            "You decide it's time to visit some famous landmarks in the United States. Which do you visit first?": (
                "Mt. Rushmore"
            ),
            "You decide the beach sounds like a perfect choice for a weekend away. Which beach do you want to visit?": (
                "Daytona Beach, Florida"
            ),
            "You decide to go stargazing in the Chilean desert, but there are only two flights left. Which do you take?": (
                "Night"
            ),
            "You decide to pick up Badosz and spend the weekend at Legoland. What do you look at first?": (
                "Gift Shop"
            ),
            "You find a discounted whale watching tour and decide to give it a go, but the deal is for two. Who do you take with you?": (
                "Kable"
            ),
            "You get a flyer for some discount cruises that sound wonderful. Which destination do you choose?": (
                "Mediterranean"
            ),
            "Your cruise ship docks at a small island for a day of sun and swimming. What do you do?": (
                "Sunbathe"
            ),
            "While vacationing in Rome, you visit the Colosseum and run into a group of people handing out friendship bracelets. What do you do?": (
                "Take a Bracelet"
            ),
        },
    },
}


def get_config():
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except:
        configs = {"global": global_config_example}
        for i in range(1, 6):
            configs[str(i)] = config_example
        with open("config.json", "w") as config_file:
            json.dump(configs, config_file, indent=4)
            return configs


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


async def start_bot(token, account_id):
    class Colors:
        red = "\033[31m"
        green = "\033[32m"
        yellow = "\033[33m"
        reset = "\033[0m"

    def log(text, color="default"):
        color_code = {
            "red": Colors.red,
            "green": Colors.green,
            "yellow": Colors.yellow,
            "default": Colors.reset,
        }.get(color, Colors.reset)

        print(f"{color_code}Bot {account_id}: {text}{Colors.reset}")

    class MyClient(commands.Bot):
        def __init__(self):
            super().__init__(command_prefix="-", self_bot=True)
            config_dict = get_config()
            self.account_id = account_id
            self.config_dict = config_dict[self.account_id]
            self.config_example = config_example
            self.state = self.config_dict["state"]
            self.channel_id = int(config_dict[account_id]["channel_id"])
            self.channel = None
            self.commands_dict = commands_dict
            self.last_ran = {}
            self.global_config_dict = config_dict["global"]
            for command in self.commands_dict:
                self.last_ran[command] = 0

        @tasks.loop(seconds=5)
        async def update(self):
            with open("config.json", "r") as config_file:
                if str(self.account_id) not in json.load(config_file):
                    sys.exit()
                config_file.seek(0)
                self.config_dict = json.load(config_file)[self.account_id]
                self.state = self.config_dict["state"]
                if self.config_dict["channel_id"] != str(self.channel_id):
                    sys.exit()

        @staticmethod
        async def click(message, component, children, delay=None):
            min_delay, max_delay = delay or (
                config_dict["global"]["min_click_delay"],
                config_dict["global"]["max_click_delay"],
            )
            await asyncio.sleep(random.randint(min_delay, max_delay) / 1000)

            try:
                await message.components[component].children[children].click()
            except (discord.errors.HTTPException, discord.errors.InvalidData):
                pass

        @staticmethod
        async def select(message, component, children, option, delay=None):
            min_delay, max_delay = delay or (
                config_dict["global"]["min_click_delay"],
                config_dict["global"]["max_click_delay"],
            )
            await asyncio.sleep(random.randint(min_delay, max_delay) / 1000)

            try:
                select_menu = message.components[component].children[children]
                await select_menu.choose(select_menu.options[option])
            except (discord.errors.HTTPException, discord.errors.InvalidData):
                pass

        async def send(self, command_name, channel=None, **kwargs):
            if channel is None:
                channel = self.channel

            async for cmd in channel.slash_commands(query=command_name, limit=None):
                try:
                    if cmd.application.id == 270904126974590976:
                        await cmd(**kwargs)
                        return
                except discord.errors.Forbidden:
                    await self.send(command_name, **kwargs)
                except (
                    discord.errors.DiscordServerError,
                    KeyError,
                    discord.errors.InvalidData,
                ):
                    pass

        async def sub_send(
            self, command_name, sub_command_name, channel=None, **kwargs
        ):
            if channel is None:
                channel = self.channel
            try:
                async for cmd in channel.slash_commands(query=command_name, limit=None):
                    if cmd.application.id == 270904126974590976:
                        for count, sub_cmd in enumerate(cmd.children):
                            if sub_cmd.name.lower() == sub_command_name.lower():
                                await cmd.children[count](**kwargs)
                                break
                        return
            except (
                discord.errors.DiscordServerError,
                KeyError,
                discord.errors.InvalidData,
            ):
                pass

        async def is_valid_command(self, message, command, sub_command=""):
            if not message.interaction:
                return False

            try:
                if (
                    "[premium](https://www.patreon.com/dankmemerbot) cooldown is"
                    in message.embeds[0].to_dict()["description"]
                ):
                    return False
            except (IndexError, KeyError):
                pass

            return (
                message.channel.id == self.channel_id
                and self.state
                and message.interaction.name
                == f"{commands_dict[command]} {sub_command}".rstrip()
                and self.config_dict["commands"][command]["state"]
                and message.interaction.user == self.user
                and not message.flags.ephemeral
            )

        async def setup_hook(self):
            self.update.start()
            self.channel = await self.fetch_channel(self.channel_id)

            for filename in os.listdir(resource_path("./cogs")):
                if filename.endswith(".py"):
                    await self.load_extension(f"cogs.{filename[:-3]}")

            log(f"Logged in as {self.user}", "green")

    client = MyClient()
    try:
        await client.start(token)
    except discord.errors.LoginFailure:
        log("Invalid token", "red")
        await client.close()
        account_tasks[account_id].cancel()
    except (discord.errors.NotFound, ValueError):
        log("Invalid channel", "red")
        await client.close()
        account_tasks[account_id].cancel()


if __name__ == "__main__":
    version = requests.get(
        "https://raw.githubusercontent.com/BridgeSenseDev/Dank-Memer-Grinder/main/"
        "resources/version.txt"
    ).text
    print(
        """ ____              _       __  __                              ____      _           _           
|  _ \  __ _ _ __ | | __  |  \/  | ___ _ __ ___   ___ _ __    / ___|_ __(_)_ __   __| | ___ _ __ 
| | | |/ _` | '_ \| |/ /  | |\/| |/ _ \ '_ ` _ \ / _ \ '__|  | |  _| '__| | '_ \ / _` |/ _ \ '__|
| |_| | (_| | | | |   <   | |  | |  __/ | | | | |  __/ |     | |_| | |  | | | | | (_| |  __/ |   
|____/ \__,_|_| |_|_|\_\  |_|  |_|\___|_| |_| |_|\___|_|      \____|_|  |_|_| |_|\__,_|\___|_|"""
    )
    print("\033[33mv1.5.2")
    if int(version.replace(".", "")) > 152:
        print(
            f"A new version v{version} is available, download it"
            f" here:\nhttps://github.com/BridgeSenseDev/Dank-Memer-Grinder/releases/tag/vf{version}"
        )
    config_dict = get_config()
    loop = asyncio.get_event_loop()
    for account in map(str, range(1, len(config_dict))):
        if config_dict[account]["discord_token"] != "":
            task = loop.create_task(
                start_bot(config_dict[account]["discord_token"], account)
            )
            account_tasks[account] = task

    loop.run_forever()
