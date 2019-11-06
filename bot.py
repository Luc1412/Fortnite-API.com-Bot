import asyncio
import logging
import time

import sys
import traceback

import discord
from discord.ext import commands

from util.config import Config
from util.context import Context
from util.database import Database
from util.utils import Utils

start_time = time.time()


class FortniteApiSupport(commands.Bot):

    def __init__(self, *args, **kwargs):
        self.logger = set_logger()
        self.cfg = Config(False)

        super().__init__(*args, command_prefix=get_prefix, **kwargs, owner_id=int(self.cfg.get('Core.OwnerID')))

        self.db = Database(self)
        self.utils = Utils(self)

    @property
    def scheduler(self):
        return self.get_cog('ScheduleManager')

    @property
    def storage(self):
        return self.get_cog('StorageManager')


async def get_prefix(bot, message: discord.Message):
    return ['!']


def init(bot_class=FortniteApiSupport):
    client = bot_class(description='Fortnite API Support Bot', case_insensitive=True)
    client.remove_command("help")

    extensions = client.cfg.get('Core.InitialCogs').split(', ')

    for extension in extensions:
        try:
            client.load_extension(f'cogs.{extension}')
        except Exception:
            client.logger.exception(f'Failed to load extension {extension}.')
            traceback.print_exc()

    @client.event
    async def on_ready():
        global start_time
        if start_time == 0.0:
            return
        bot.logger.info(f'[CORE] The bot was started successfully after {int(time.time() - start_time)} seconds with '
                        f'{bot.shard_count} Shards')
        start_time = 0.0

    @client.event
    async def on_command_error(ctx: Context, error):

        ignored = (commands.MissingRequiredArgument, commands.CommandNotFound, commands.BadArgument, discord.NotFound,
                   commands.NotOwner)

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.NoPrivateMessage):
            pass
            # return await bot.send_error(ctx, error='This command cannot be used in private messages.', dm=True)
        else:
            raise error

    @client.event
    async def on_error(event, *args, **kwargs):
        await bot.utils.report_exception(traceback.format_exc())

    @client.event
    async def on_command(ctx: Context):
        client.logger.info(f'[CORE] {ctx.author} on {ctx.guild.name}: {ctx.message.content}')

    @client.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.TextChannel):
            return
        await client.process_commands(message)

    @client.event
    async def process_commands(message: discord.Message):
        await client.wait_until_ready()
        ctx = await client.get_context(message, cls=Context)
        if not ctx.valid:
            return
        await client.invoke(ctx)

    return client


def set_logger():
    import datetime
    import gzip
    import os
    import shutil
    logger = logging.getLogger('bot')
    logger.setLevel(logging.DEBUG)
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.INFO)
    log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    discord_logger.addHandler(console_handler)

    if sys.argv.__contains__('-NoFileLog'):
        return logger

    if not os.path.exists('logs'):
        os.makedirs('logs')
    if os.path.isfile('logs//latest.log'):
        filename = None
        index = 1
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        while filename is None:
            check_filename = f'{date}-{index}.log.gz'
            if os.path.isfile(f'logs//{check_filename}'):
                index += 1
            else:
                filename = check_filename
        with open('logs//latest.log', 'rb') as f_in, gzip.open(f'logs//{filename}', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove('logs//latest.log')

    file_handler = logging.FileHandler(filename='logs//latest.log', encoding='utf-8', mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    discord_logger.addHandler(file_handler)

    return logger


async def main(efs_bot):
    await efs_bot.login(efs_bot.cfg.get('Core.Token'))
    await efs_bot.connect()


if __name__ == '__main__':
    bot = init()
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main(bot))
    except discord.LoginFailure:
        bot.logger.exception(traceback.format_exc())
    except Exception as e:
        bot.logger.exception('[CORE] Fatal exception! Bot is not able to login! Attempting graceful logout!',
                             exc_info=e)
        loop.run_until_complete(bot.logout())
    finally:
        loop.close()
        exit(0)
