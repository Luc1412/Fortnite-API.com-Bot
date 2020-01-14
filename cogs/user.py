import discord
from discord.ext import commands


class UserCommands(commands.Cog):

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        content = message.content.lower()
        if content.startswith('?id') or \
           content.startswith('?skin') or \
           content.startswith('.skin') or \
           content.startswith('+https://glitch.com/edit') or \
           content.startswith('https://glitch.com/edit'):
            await message.delete()
            e = discord.Embed()
            e.colour = discord.Color.red()
            e.title = 'Wrong Server!'
            e.description = 'This isn\'t the server for Fortnite Lobby bots / LupusLeaks bot. Please try this command' \
                            ' on his server.'
            await message.channel.send(embed=e, delete_after=30)


def setup(bot):
    bot.add_cog(UserCommands(bot))
