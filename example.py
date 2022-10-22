# This example requires the 'message_content' intent.
from discord.ext import tasks, commands
from datetime import datetime
import discord
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=['/', '!'], intents=intents)

# Change these values
discord_token = ''
jira_link = ''
channel_id = '123'
names = [
    {'name': 'John Doe', 'score': 0},
    {'name': 'Jane Doe', 'score': 0},
]


class Standupper:
    def __init__(self, index: int, names: list) -> None:
        self.index = index
        self.names = names
        self.name = names[index]['name']

    def new_name(self) -> str:
        if self.index == (len(self.names) - 1):
            self.index = 0
        else:
            self.index += 1
        self.name = self.names[self.index]['name']

    def update_score(self, function: str) -> None:
        if function == 'add':
            self.names[self.index]['score'] += 1
        else:
            if self.names[self.index]['score'] > 0:
                self.names[self.index]['score'] -= 1


standupper = Standupper(random.randrange(len(names)), names)


async def send_msg() -> None:
    channel = bot.get_channel(channel_id)
    standupper.new_name()
    embed = discord.Embed(
        description='Graag het bord tevoorschijn toveren en de standup leiden')

    def get_colleagues() -> str:
        # Get a new list to embed and add fancy emoji
        colleagues = [person['name'] for person in standupper.names]
        # list comprehension this
        for index, name in enumerate(colleagues):
            if standupper.name == name:
                colleagues[index] = name + '  💬'
                return '\n'.join([name for name in colleagues])

    embed.add_field(name='Collega',
                    value=get_colleagues(), inline=True)
    embed.add_field(name='Puntjes', value='\n'.join(
        [str(person['score']) for person in standupper.names]))
    embed.add_field(
        name='Jira', value=f'[Link naar bord]({jira_link})', inline=False)

    done_button = discord.ui.Button(
        label='Done', style=discord.ButtonStyle.green)
    next_button = discord.ui.Button(
        label='Next', style=discord.ButtonStyle.red)

    async def done_button_re(interaction):
        standupper.update_score('add')
        embed.set_field_at(1, name='Puntjes', inline=True, value='\n'.join(
                           [str(person['score']) for person in standupper.names]))
        view.remove_item(done_button)
        view.remove_item(next_button)
        await interaction.message.edit(embeds=[embed], view=view)
        await interaction.response.defer()

    async def next_button_re(interaction):
        standupper.update_score('substract')
        embed.set_field_at(1, name='Puntjes', inline=True, value='\n'.join(
                           [str(person['score']) for person in standupper.names]))
        standupper.new_name()
        embed.set_field_at(0, name='Collega',
                           value=get_colleagues(), inline=True)
        await interaction.message.edit(embeds=[embed])
        await interaction.response.defer()

    done_button.callback = done_button_re
    next_button.callback = next_button_re

    view = discord.ui.View()
    view.add_item(done_button)
    view.add_item(next_button)
    await channel.send(embeds=[embed], view=view)


@ tasks.loop(seconds=60)
async def automatic_standup():
    now = datetime.now()
    # standups on weekdays and at 9 'o clock
    if now.weekday() < 5:
        if now.hour == 8 and now.minute == 59:
            await send_msg()


@ bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')
    print(f'Logged in on {bot.guilds[0].id}')
    automatic_standup.start()


@ bot.command()
async def standup(ctx):
    await send_msg()

bot.run(discord_token)
