import datetime
import functools
from itertools import islice

import aiohttp
import discord
from discord.ext import commands


class Utils:

    def __init__(self, bot):
        self.bot = bot

        self.channel = Channel(bot)
        self.role = Role(bot)
        self.color = Color()
        self.icon = Icon(bot)

    @staticmethod
    async def loading(ctx: commands.Context, text: str, edit: discord.Message = None):
        loading_message = discord.Embed()
        loading_message.colour = ctx.bot.utils.color.warn()
        loading_message.description = f'**{text}**  {str(ctx.bot.utils.icon.loading())}'
        if edit:
            return await edit.edit(embed=loading_message)
        return await ctx.send(embed=loading_message)

    @staticmethod
    async def get_user(ctx: commands.Context, name):
        if name.lower().__contains__('#'):
            if len(name.lower().split('#')[1]) != 4:
                return None
        elif name.lower().startswith('<@') and name.lower().endswith('>'):
            pass
        elif len(name) >= 18:
            try:
                int(name)
            except ValueError:
                return None
        else:
            return None
        user = None
        try:
            user = await commands.MemberConverter().convert(ctx, name)
        except commands.BadArgument:
            pass
        return user

    @staticmethod
    def format_number(number):
        return "{:,}".format(number)

    @staticmethod
    def mention_role(role: discord.Role):
        if role.is_default():
            return '@everyone'
        return role.mention

    @staticmethod
    def chunk_list(list, size):
        for i in range(0, len(list), size):
            yield list[i:i + size]

    @staticmethod
    def chunk_dict(data, size):
        it = iter(data)
        for i in range(0, len(data), size):
            yield {k: data[k] for k in islice(it, size)}


class Channel:

    def __init__(self, bot):
        self.bot = bot

    def news(self):
        channel_id = int(self.bot.cfg.get('Channel.News'))
        return self.bot.get_channel(channel_id)


class Role:
    def __init__(self, bot):
        self.bot = bot

    def notification(self):
        role_id = int(self.bot.cfg.get('Role.Notification'))
        return self.bot.guilds[0].get_role(role_id)


class Icon:

    def __init__(self, bot):
        self.bot = bot

    def fortnite_api(self):
        role_id = int(self.bot.cfg.get('Icons.FortniteAPI'))
        return self.bot.get_emoji(role_id)


class Color:

    @staticmethod
    def fail():
        return discord.Colour.from_rgb(194, 54, 22)

    @staticmethod
    def success():
        return discord.Colour.from_rgb(39, 174, 96)

    @staticmethod
    def warn():
        return discord.Colour.from_rgb(241, 196, 15)

    @staticmethod
    def select():
        return discord.Colour.from_rgb(0, 98, 102)

    @staticmethod
    def invisible():
        return discord.Colour.from_rgb(54, 57, 63)
