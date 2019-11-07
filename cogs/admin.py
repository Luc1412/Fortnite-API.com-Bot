import datetime

import discord
import pytz
from discord.ext import commands

from util import checks
from util.context import Context
from util.selection import SelectionInterface, SelectionType, ReplacedText


class AdminCommands(commands.Cog):

    @commands.command(case_insensitive=True)
    @commands.guild_only()
    @checks.is_admin()
    async def update(self, ctx: Context):
        selection = SelectionInterface(ctx, timeout=300)

        title_selection = selection.set_base_selection(SelectionType.TEXT, 'Select Title',
                                                       '**Please enter the update title.**')

        message_selection = title_selection.add_result('*', SelectionType.TEXT, 'Select Message',
                                                       'Title successfully set!\n\n'
                                                       '**Please enter the update message.**')

        image_selection = message_selection.add_result('*', SelectionType.TEXT, 'Select Image',
                                                       'Message successfully set!\n\n'
                                                       '**Please enter the image url.**\n'
                                                       'For no image enter `none` for no image.')

        def f1(result):
            return result[0]

        def f2(result):
            return result[1]

        def f3(result):
            return result[2]

        submit_selection = image_selection.add_result('*', SelectionType.CONFIRM_SELECTION, ReplacedText('{}', f1),
                                                      ReplacedText('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n{}', f2),
                                                      color=discord.Color.blurple(),
                                                      image=ReplacedText('{}', f3),
                                                      thumbnail='https://fortnite-api.com/logo.png',
                                                      footer='Subscribe to Updates in #home by clicking on the reaction.')

        async def a(context, result):
            update_message = discord.Embed()
            update_message.set_author(name=result[0])
            update_message.colour = discord.Color.blurple()
            update_message.set_thumbnail(url='https://fortnite-api.com/logo.png')
            update_message.description = f'▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n{result[1]}'
            update_message.set_footer(text='Subscribe to Updates in #home by clicking on the reaction.')

            update_role = context.utils.role.notification()
            await update_role.edit(mentionable=True, reason='Update mention')

            # await context.utils.channel.news().send(content=update_role.mention, embed=update_message)
            await context.utils.channel.news().send(content='@everyone', embed=update_message)

            await update_role.edit(mentionable=False, reason='Update mention')

        submit_selection.set_action(a)

        submit_selection.add_result('*', SelectionType.SUCCESS, 'Update successfully',
                                    ':white_check_mark: Update successfully sent!')

        await selection.start()

    @commands.command(case_insensitive=True)
    @commands.guild_only()
    @checks.is_admin()
    async def post(self, ctx: Context, post_type, channel: discord.TextChannel):
        post_messages = []
        if post_type == 'upcoming':
            post_message = discord.Embed()
            post_message.colour = discord.Color.dark_purple()
            post_message.set_author(name='General features')
            post_message.add_field(name='• Fortnite server status',
                                   value='This endpoint will return information of the server status.\n'
                                         'The result will include a server status object with information about the '
                                         'main server status (if you able to play Fortnite), all categories shown on '
                                         'https://status.epicgames.com, information about maintenance, information '
                                         'about the latest issues.')
            post_message.add_field(name='• Creator Code validation & information',
                                   value='This endpoint will return information about the inserted Creator Code.\n'
                                         'The result will include a Creator Code object if the Creator Code exists.')
            post_message.add_field(name='• EpicGames blog posts',
                                   value='This endpoint will return the blog posts fom the news tab on the website.\n'
                                         'The result will include a list of blog entry objects\n'
                                         '- Available in all game languages')
            post_message.add_field(name='• Player lookup',
                                   value='This endpoint will return information about a player.\n'
                                         'The result will include a player object with id, name, console name/ID\n'
                                         '- Lookup by name, console name(case sensitive) and ID available')
            post_messages.append(post_message)

            post_message = discord.Embed()
            post_message.colour = discord.Color.dark_purple()
            post_message.set_author(name='Battle Royale Features')
            post_message.add_field(name='• Upcoming Cosmetics',
                                   value='This endpoint will return upcoming/unreleased cosmetics.\n'
                                         'The result will include a list of cosmetic objects.\n'
                                         '- Available in all game languages')
            post_message.add_field(name='• Playlist information',
                                   value='This endpoint will return all playlists/gamemodes.\n'
                                         'The result will include a list of playlist objects with name, '
                                         'description, image, playlist information eg. team-size\n'
                                         '- Available in all game languages\n'
                                         '- Includes a option to only show active playlists in the specific regions.')
            post_message.add_field(name='• Weapon information',
                                   value='This endpoint will return all weapons.\n'
                                         'The result will include a list of weapon objects with name, '
                                         'icon, damage and rarities\n'
                                         '- Available in all game languages\n'
                                         '- Includes a option to only show enabled weapons.')
            post_message.add_field(name='• Player stats',
                                   value='This endpoint will return the Battle Royale stats from a player.\n'
                                         'The result will include a BR stats object\n'
                                         '- Stats V1 & Stats V2 available\n'
                                         '- Option for seasonal stats (only latest season)')
            post_message.add_field(name='• Challenges',
                                   value='This endpoint will return all challenges.\n'
                                         'The result will include a list of challenge object\n'
                                         '- Available in all game languages\n'
                                         '- Option for active ones?')
            post_message.add_field(name='• Creative island information',
                                   value='This endpoint will return information of a published Creative island.\n'
                                         'The result will include a Creative island objects if found')
            post_messages.append(post_message)

            post_message = discord.Embed()
            post_message.colour = discord.Color.dark_purple()
            post_message.set_author(name='Save the World features')
            post_message.add_field(name='• Player stats',
                                   value='This endpoint will return the Save the World stats from a player.\n'
                                         'The result will include a STW stats object with base power, level and '
                                         'owned items information')
            post_message.add_field(name='• World info',
                                   value='This endpoint will return information about the the missions.\n'
                                         'The result will include a world info object with a list of missions '
                                         '(eg. for missions alerts)')
            post_message.add_field(name='• Shop',
                                   value='This endpoint will return the shop.\n'
                                         'The result will include a STW shop object\n'
                                         '- Available in all game languages')
            post_messages.append(post_message)

            post_message = discord.Embed()
            post_message.colour = discord.Color.dark_purple()
            post_message.set_author(name='Website features')
            post_message.add_field(name='• Discord login for API key',
                                   value='We\'ll soon add a authentication to prevent spam/abuse.\n'
                                         'The login will work trough Discord.\n'
                                         '- After successfully authentication you\'ll receive a `Verified User` rank '
                                         'in this Discord')
            post_message.add_field(name='• Featured projects',
                                   value='We soon add an page on our website where you can add your project if it uses'
                                         'our API and corresponds our quality standards.')
            post_messages.append(post_message)

            post_message = discord.Embed()
            post_message.colour = discord.Color.dark_purple()
            post_message.set_author(name='Premium features')
            post_message.add_field(name='• Auto updates',
                                   value='Get automatically updates if information are changing\n'
                                         'This feature will work for:\n'
                                         '- BR/STW Shop\n'
                                         '- STW Mission Alerts\n'
                                         '- Upcoming cosmetics\n'
                                         '- BR Matches')
            post_message.add_field(name='• Battle Royale Player Matches',
                                   value='This endpoint will return the latest matches of a player.\n'
                                         'The result will include a list of match objects')
            post_messages.append(post_message)
        elif post_type == 'home':
            post_message = discord.Embed()
            post_message.colour = discord.Color.blue()
            post_message.set_author(name='Fortnite-API.com', url='https://fortnite-api.com')
            post_message.set_thumbnail(url='https://fortnite-api.com/logo.png')
            post_message.description = 'Welcome to our Discord server!\n' \
                                       'Here you get support & updates of our API.'
            post_message.add_field(name='**Rules**',
                                   value='**1.** Be friendly and respectful!\n'
                                         '**2.** Don\'t spam or write in caps!\n'
                                         '**3.** Advertisement of any kind are forbidden.\n'
                                         '**4.** Follow Discord\'s [Terms of Service](https://discordapp.com/terms), '
                                         '[Community Guidelines](https://discordapp.com/guidelines)!\n'
                                         '**5.** Follow the instructions of the <@&640551807978045461>!\n\n'
                                         'We reserve the right to change or modify any of the rules at any time.')
            post_message.add_field(name='**Links**',
                                   value='[Website](https://fortnite-api.com/)\n'
                                         '[Documentation](https://fortnite-api.com/documentation)\n'
                                         '[Twitter](https://twitter.com/Fortnite_API)\n'
                                         '[Server Invite](https://discord.gg/AqzEcMm)')
            post_message.add_field(name='**Roles**',
                                   value='React with a Emoji to get the specific Role.\n\n'
                                         '<:fortniteapi:641395927025844254> **-** Get notified about API Updates.\n\n'
                                         '<:javascript:642027841512538148> **-** Java Script / Node.js\n'
                                         '<:python:642027841017479179> **-** Python\n'
                                         '<:java:642027839008276493> **-** Java\n'
                                         '<:csharp:642027845434212383> **-** C#\n'
                                         '<:php:642041601291583488> **-** PHP\n'
                                         '<:swift:642027842334490652> **-** Swift\n'
                                         'Missing your programming language? Let us know.')
            post_message.set_footer(text=f'Last Update')
            post_message.timestamp = datetime.datetime.now(pytz.timezone('UTC'))
            post_messages.append(post_message)

        for post_message in post_messages:
            await channel.send(embed=post_message)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
