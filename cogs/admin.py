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

        notification_selection = image_selection.add_result('*', SelectionType.REACTION, 'Select Notification',
                                                            'Message successfully set!\n\n'
                                                            '**Should we notify someone?**\n'
                                                            '\U0001f514 **- Enable Notification**\n'
                                                            '\U0001f515 **- Disable Notification**',
                                                            reactions=['🔔', '🔕'])

        def f1(result):
            return result[0]

        def f2(result):
            return result[1]

        def f3(result):
            return result[2]

        submit_selection = notification_selection.add_result('*', SelectionType.CONFIRM_SELECTION,
                                                             ReplacedText('{}', f1),
                                                             ReplacedText('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n{}', f2),
                                                             color=discord.Color.blurple(),
                                                             image=ReplacedText('{}', f3),
                                                             thumbnail='https://fortnite-api.com/logo.png',
                                                             footer='Subscribe to Updates in #info by clicking on the '
                                                                    'reaction.')

        async def a(context, result):
            update_message = discord.Embed()
            update_message.set_author(name=result[0])
            update_message.colour = discord.Color.blurple()
            update_message.set_thumbnail(url='https://fortnite-api.com/logo.png')
            update_message.description = f'▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n{result[1]}'
            update_message.set_footer(text='Subscribe to Updates in #info by clicking on the reaction.')

            update_role = context.utils.role.notification()
            await update_role.edit(mentionable=True, reason='Update mention')

            await context.utils.channel.news().send(
                content=update_role.mention if selection.result()[3] == '🔔' else None,
                embed=update_message)

            await update_role.edit(mentionable=False, reason='Update mention')

        submit_selection.set_action(a)

        submit_selection.add_result('*', SelectionType.SUCCESS, 'Update successfully',
                                    ':white_check_mark: Update successfully sent!')

        await selection.start()

    @commands.command(case_insensitive=True)
    @commands.guild_only()
    @checks.is_admin()
    async def post(self, ctx: Context, post_type, channel: discord.TextChannel, message_id: int = None):
        message = await channel.fetch_message(message_id) if message_id else None
        post_messages = []
        if post_type == 'upcoming':
            post_message = discord.Embed()
            post_message.colour = discord.Color.dark_purple()
            post_message.description = '🔻 **-** Features marked with this tag require a high effort and may get ' \
                                       'published later'
            post_message.set_author(name='General')
            post_message.add_field(name='• Fortnite server status',
                                   value='Get information about the server status (Lightswitch + '
                                         'https://status.epicgames.com)')
            post_message.add_field(name='• Creator Code validation & information',
                                   value='Get information about the inserted Creator Code and check if it exists.')
            post_message.add_field(name='• Epic Games blog posts',
                                   value='Get the blog posts from the news tab on the website.\n'
                                         '- Available in all game languages')
            post_message.add_field(name='• Player lookup',
                                   value='Get information about a player.\n'
                                         '- Lookup by name, console name and ID available')
            post_message.add_field(name='• Game assets',
                                   value='Get Assets from the game files.')
            post_message.add_field(name='• Version information',
                                   value='Get version information like the current game version.', inline=False)
            post_messages.append(post_message)

            post_message = discord.Embed()
            post_message.colour = discord.Color.dark_purple()
            post_message.set_author(name='Battle Royale')
            post_message.add_field(name='• Upcoming Cosmetics',
                                   value='Get upcoming/unreleased cosmetics.\n'
                                         '- Available in all game languages')
            post_message.add_field(name='• Playlist information',
                                   value='Get all playlists/game modes.\n'
                                         '- Available in all game languages\n'
                                         '- Includes an option to show only active playlists in the specific regions.')
            post_message.add_field(name='• Weapon information 🔻',
                                   value='Get all weapons.\n'
                                         '- Available in all game languages')
            post_message.add_field(name='• Player stats',
                                   value='Get the stats from a player.\n'
                                         '- Stats V1 & Stats V2 available\n'
                                         '- Option for seasonal stats (only latest season)')
            post_message.add_field(name='• Challenges 🔻',
                                   value='Get all missions & challenges.\n'
                                         '- Available in all game languages')
            post_message.add_field(name='• Map',
                                   value='Get the current map with POI Names.\n'
                                         '- Available in all game languages')
            post_message.add_field(name='• Creative island information',
                                   value='Get information of a published Creative island if it exists.')
            post_messages.append(post_message)

            post_message = discord.Embed()
            post_message.colour = discord.Color.dark_purple()
            post_message.set_author(name='Save the World features')
            post_message.add_field(name='• Player stats 🔻',
                                   value='Get stats from a player.')
            post_message.add_field(name='• World info 🔻',
                                   value='Get information about all missions. (eg. for missions alerts)')
            post_message.add_field(name='• Shop 🔻',
                                   value='Get the current shop.\n'
                                         '- Available in all game languages')
            post_messages.append(post_message)

            post_message = discord.Embed()
            post_message.colour = discord.Color.dark_purple()
            post_message.set_author(name='Website & API')
            post_message.add_field(name='• API keys',
                                   value='API requests will require an API key soon.\n'
                                         'The authentication will work through Discord.\n'
                                         'This change will be announced about a week before it goes live.')
            post_message.add_field(name='• Featured projects',
                                   value='We soon add a page on our website where you can add your project if it uses '
                                         'our API and corresponds to our quality standards.')
            post_messages.append(post_message)
        elif post_type == 'home':
            post_message = discord.Embed()
            post_message.colour = discord.Color.blue()
            post_message.set_author(name='Fortnite-API.com', url='https://fortnite-api.com')
            post_message.set_thumbnail(url='https://fortnite-api.com/logo.png')
            post_message.description = 'Welcome to our Discord server!\n' \
                                       'Here you get support & updates of our API.'
            post_message.add_field(name='**Rules**', inline=False,
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
                                         '[GitHub](https://github.com/Fortnite-API)\n'
                                         '[PayPal (donation)](https://fortnite-api.com/paypal)\n'
                                         '[Server Invite](https://discord.gg/AqzEcMm)')
            post_message.add_field(name='**Libraries**',
                                   value='<:javascript:645765463095377921> [JavaScript](https://github.com/Fortnite-API/js-wrapper) (by <@473592440817713172>)\n'
                                         '<:python:642027841017479179> [Python](https://github.com/Fortnite-API/py-wrapper) (by <@262511457948663809>)\n'
                                         '<:java:642027839008276493> [Java](https://github.com/Fortnite-API/java-wrapper) (by <@312157715449249795>)\n'
                                         '<:csharp:642027845434212383> [C#](https://github.com/Fortnite-API/csharp-wrapper) (by <@373913699943186432>)\n'
                                         '<:php:642041601291583488> [PHP](https://github.com/Fortnite-API/php-wrapper) (by <@473592440817713172>)\n')
            post_message.add_field(name='**Roles**', inline=False,
                                   value='React to the emojis to self-assign roles.\n\n'
                                         '<:fortniteapi:641395927025844254> **-** Get notified about API Updates.\n\n'
                                         '<:nodejs:642027841512538148> **-** JavaScript / Node.js\n'
                                         '<:python:642027841017479179> **-** Python\n'
                                         '<:java:642027839008276493> **-** Java\n'
                                         '<:csharp:642027845434212383> **-** C#\n'
                                         '<:php:642041601291583488> **-** PHP\n'
                                         '<:ruby:646760486049677352> **-** Ruby\n'
                                         '<:swift:642027842334490652> **-** Swift\n'
                                         'Missing your programming language? Let us know.')
            post_message.set_footer(text=f'Last update')
            post_message.timestamp = datetime.datetime.now(pytz.timezone('UTC'))
            post_messages.append(post_message)

        for post_message in post_messages:
            print(message)
            if not message:
                await channel.send(embed=post_message)
            else:
                await message.edit(embed=post_message)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
