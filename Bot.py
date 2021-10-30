from os import getenv
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
token = getenv("TOKEN")
intents = discord.Intents.default()
intents.members = True

if __name__ == "__main__":
    bot = commands.Bot(command_prefix="!")
    bot.load_extension("Commands.Testcomm")
    bot.load_extension("Commands.SetUp")
    bot.load_extension("Commands.ModTools")
    bot.load_extension("Commands.MusicTools")
    bot.load_extension("Commands.Soundboard")

    bot.run(token)
