from discord.ext.tasks import loop  # type: ignore
from discord.ext.commands import Cog, cooldown, BucketType  # type: ignore
import aiohttp
import discord
from cachetools import TTLCache
from random import choice
from collections import deque
from typing import Deque
from ormsgpack import packb, unpackb

from bot import PogBot
from discord.ext.bridge.core import bridge_command


class Meme(Cog):
    def __init__(self, bot: PogBot):
        self.bot = bot
        self.memehistory: TTLCache[str, Deque[bytes]] = TTLCache(100, 3600)
        self.memecache: TTLCache[str, Deque[bytes]] = TTLCache(100, 3600)
        self.allmemes: Deque[bytes] = deque()
        self.subreddits = (
            "memes",
            "dankmemes",
            "me_irl",
            "funny",
            "wholesomememes",
            "antimeme",
        )
        self.get_more_memes.start()

    async def get_memes_from_sub(self, sub: str):
        async with aiohttp.ClientSession() as session:
            d = await session.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=100")
            data = await d.json()
            memes = [
                i["data"] for i in data["data"]["children"] if not i.get("over_18")
            ]
            if sub not in self.memecache:
                self.memecache[sub] = deque(maxlen=1024)
            for meme in memes:
                m = packb(
                    {
                        "title": meme["title"],
                        "author": meme["author"],
                        "subreddit": sub,
                        "postLink": f"https://reddit.com{meme['permalink']}",
                        "ups": meme["ups"],
                        "url": meme["url"],
                    }
                )
                self.memecache[sub].appendleft(m)
                if sub.lower() != "showerthoughts":
                    self.allmemes.appendleft(m)

    @bridge_command(
        name="meme",
        description="Returns a random meme from reddit!",
        aliases=["memz"],
        usage="meme [subreddit]",
    )
    @cooldown(1, 2, BucketType.guild)
    async def meme(self, ctx, sub: str = None):
        if sub:
            if self.memecache.get(sub):
                meme: dict = unpackb(choice(self.memecache[sub]))  # nosec: B311
            else:
                await self.get_memes_from_sub(sub)
        if len(self.allmemes) < 1:
            await ctx.trigger_typing()
        meme: dict = unpackb(choice(self.allmemes))  # type: ignore
        embed = discord.Embed(title=meme["title"], color=ctx.author.color)
        embed.set_author(name=f"r/{meme['subreddit']}", url=meme["postLink"])
        embed.set_footer(text=f"👍 {meme['ups']} • u/{meme['author']}")
        embed.set_image(url=meme["url"])
        await ctx.respond(embed=embed)

    @bridge_command(
        description="Returns a random showerthought from reddit!", usage="showerthought"
    )
    @cooldown(1, 2, BucketType.user)
    async def showerthought(self, ctx):
        if not self.memecache.get("showerthoughts"):
            await ctx.trigger_typing()
            await self.get_memes_from_sub("showerthoughts")
        meme: dict = unpackb(choice(self.memecache["showerthoughts"]))  # type: ignore
        embed = discord.Embed(description=meme["title"], color=ctx.author.color)
        embed.set_author(name="r/showerthoughts", url=meme["postLink"])
        embed.set_footer(text=f"👍 {meme['ups']} • u/{meme['author']}")
        await ctx.respond(embed=embed)

    @bridge_command()
    @cooldown(1, 2, BucketType.user)
    async def dankmeme(self, ctx):
        await self.meme(ctx, "dankmemes")

    @bridge_command()
    @cooldown(1, 2, BucketType.user)
    async def antimeme(self, ctx):
        await self.meme(ctx, "antimeme")

    @bridge_command()
    @cooldown(1, 2, BucketType.user)
    async def me_irl(self, ctx):
        await self.meme(ctx, "me_irl")

    @bridge_command(aliases=["codememe"])
    @cooldown(1, 2, BucketType.user)
    async def programmerhumor(self, ctx):
        await self.meme(ctx, "ProgrammerHumor")

    @loop(seconds=30)
    async def get_more_memes(self):
        for sub in self.subreddits:
            await self.get_memes_from_sub(sub)

    @loop(hours=24)
    async def reload_memes(self):
        self.memecache.clear()
        self.memecache = deque(maxlen=1024)
        await self.get_more_memes()
        print("Reloaded Meme Cache")


def setup(bot):
    bot.add_cog(Meme(bot))
