from discord.ext.bridge.bot import Bot
from discord.ext.commands.bot import when_mentioned_or, Context
from discord.ext.tasks import loop # type: ignore
from discord import Message, Intents, ActivityType, Activity
from asyncio import sleep
from discord import utils
from typing import List
from helpcmd import PogBotHelp
from time import time
from os import environ
from statcord import StatcordClient
from random import choice

class PogBot(Bot):
    def __init__(self, extensions: List[str] = None):
        i = Intents.all()
        i.message_content = False
        i.typing = False

        super().__init__(
            command_prefix=when_mentioned_or("pog ", "pog"),
            case_insensitive=True,
            intents=i,
            owner_ids=(
                536644802595520534,  # thrizzle.#4258
                819786180597907497,  # griffin#1405
                656021685203501066,  # RyZe#7968
                839514280251359292,  # Random_1s#999
            ),
            help_command=PogBotHelp(),
        )
        self.ext = extensions or ("chatbot", "error", "meme", "text", "economy", "fun", "utils")
        self.poglist = (
            "pog",
            "pogger",
            "poggers",
            "pogg",
            "poger",
            "poggus",
        )
        self.statuses = (
            Activity(type=ActivityType.watching, name="you pog"),
            Activity(type=ActivityType.listening, name="Yuno Miles"),
            Activity(type=ActivityType.watching, name="us grow"),
            Activity(type=ActivityType.watching, name="Yuno Miles music videos"),
            Activity(type=ActivityType.watching, name="thrzl break stuff"),
            Activity(type=ActivityType.listening, name="Twenty One Pilots"),
            Activity(type=ActivityType.watching, name="me being verified"),
            Activity(type=ActivityType.watching, name="TOP music vids")
        )
        self.statcord_client = StatcordClient(self, environ["STATCORD_TOKEN"])

    async def check(self, ctx: Context):
        if ctx.author.bot or not ctx.guild:
            return False
        return True

    @loop(seconds=60)
    async def change_status(self):
        await self.change_presence(activity=choice(self.statuses)) # nosec: B311

    def get_cog(self, name: str):
        return {n.lower(): cog for n, cog in self.cogs.items()}.get(name.lower())

    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return
        await self.process_commands(message)
        for i in [c.name.lower() for c in self.commands]:
            if message.content.lower() in [f"pog{i}", f"pog {i}"]:
                return
        for word in message.content.lower().split(" "):
            if word in self.poglist:
                await sleep(1)
                custom_emoji = utils.get(self.emojis, id = 846888695717036033)
                if not custom_emoji:
                    return
                await message.add_reaction(custom_emoji)
        if message.content == "family":
            await message.channel.send(
                "https://tenor.com/view/i-dont-have-friends-i-have-family-theyre-not-my-friends-theyre-my-family-more-than-friends-gif-16061717"
            )

    def run(self):
        token = environ.get("TOKEN")
        super().load_extension("jishaku")
        for ext in self.ext:
            self.load_extension(f"cogs.{ext}")
        self.start_time = time()
        super().run(token)

    async def on_ready(self):
        print("[i] Bot ready")
        self.change_status.start()
#
