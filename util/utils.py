import datetime
import functools
from itertools import islice
from enum import Enum

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

    async def remove_reactions(self, channel, message_id: int):
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            return
        except discord.Forbidden:
            return
        else:
            try:
                await message.clear_reactions()
            except discord.Forbidden:
                for reaction in message.reactions:
                    if not reaction.me:
                        continue
                    await message.remove_reaction(reaction.emoji, self.bot.user)

    async def user_has_voted(self, user: discord.User):
        db_token = self.bot.cfg.get('DiscordBotLists.Top_GG_Token')
        url = f'https://top.gg/api/bots/{self.bot.user.id}/check?userId={user.id}'
        headers = {"Authorization": db_token}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await response.json()
                if not result.__contains__('voted'):
                    return None
                result = result['voted']
                return False if result == 0 else True

    async def report_to_metrics(self, path, points=1):
        try:
            func = functools.partial(self.bot.metrics.send, metric=path, points=points)
            await self.bot.loop.run_in_executor(None, func)
        except Exception:
            pass

    @staticmethod
    def get_time_until_date(date):
        today = datetime.datetime.today()
        delta = date - today
        if str(delta).startswith('-'):
            return '0'
        return str(delta).split('.')[0]

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
    async def check_url_for_image(url, max_size):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status not in range(200, 204):
                        return 404
                    valid_content_types = ['image/png', 'image/jpeg']
                    if response.content_type not in valid_content_types:
                        return 406
                    if response.content_length > max_size:
                        return 413
        except Exception:
            return 404

    @staticmethod
    async def send_to_offline_bot(mode, data):
        import websockets
        try:
            async with websockets.connect('ws://localhost:7683') as websocket:
                await websocket.send(f'{mode.value}:{data}')
        except Exception:
            pass

    @staticmethod
    def get_motd_playlist():
        return [
            ['l', '!help | {s} Server'],
           # ['p', 'Support me with !fn vote'], TODO:
            ['l', '!help | {uu} Unique User'],
        ]

    @staticmethod
    def mention_role(role: discord.Role):
        if role.is_default():
            return '@everyone'
        return role.mention

    @staticmethod
    def get_footer(storage_guild):

        from random import choice

        def get_footer_list():
            return [
                'Checkout new Languages with !fn settings',
            ]

        def get_ad_footer_list():
            return [
                'Support me with !vote',
            ]

        if storage_guild.disabled_ads and storage_guild.premium:
            footer_list = get_footer_list()
        else:
            footer_list = get_footer_list() + get_ad_footer_list()

        return choice(footer_list)

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

    def fail(self):
        emoji_id = int(self.bot.cfg.get('Icons.Fail'))
        return self.bot.get_emoji(emoji_id)

    def success(self):
        emoji_id = int(self.bot.cfg.get('Icons.Success'))
        return self.bot.get_emoji(emoji_id)

    def loading(self):
        emoji_id = int(self.bot.cfg.get('Icons.Loading'))
        return self.bot.get_emoji(emoji_id)

    def trash(self):
        emoji_id = int(self.bot.cfg.get('Icons.Trash'))
        return self.bot.get_emoji(emoji_id)

    def discord_user(self):
        emoji_id = int(self.bot.cfg.get('Icons.DiscordUser'))
        return self.bot.get_emoji(emoji_id)

    def bots(self):
        emoji_id = int(self.bot.cfg.get('Icons.Bot'))
        return self.bot.get_emoji(emoji_id)

    def category_channel(self):
        emoji_id = int(self.bot.cfg.get('Icons.CategoryChannel'))
        return self.bot.get_emoji(emoji_id)

    def text_channel(self):
        emoji_id = int(self.bot.cfg.get('Icons.TextChannel'))
        return self.bot.get_emoji(emoji_id)

    def voice_channel(self):
        emoji_id = int(self.bot.cfg.get('Icons.VoiceChannel'))
        return self.bot.get_emoji(emoji_id)

    def online(self):
        emoji_id = int(self.bot.cfg.get('Icons.Online'))
        return self.bot.get_emoji(emoji_id)

    def idle(self):
        emoji_id = int(self.bot.cfg.get('Icons.Idle'))
        return self.bot.get_emoji(emoji_id)

    def dnd(self):
        emoji_id = int(self.bot.cfg.get('Icons.Dnd'))
        return self.bot.get_emoji(emoji_id)

    def offline(self):
        emoji_id = int(self.bot.cfg.get('Icons.Offline'))
        return self.bot.get_emoji(emoji_id)

    def spotify(self):
        emoji_id = int(self.bot.cfg.get('Icons.Spotify'))
        return self.bot.get_emoji(emoji_id)

    def twitch(self):
        emoji_id = int(self.bot.cfg.get('Icons.Twitch'))
        return self.bot.get_emoji(emoji_id)


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
