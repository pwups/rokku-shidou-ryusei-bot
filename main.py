import discord
from discord.ext import commands
import asyncio, random, datetime

TOKEN = os.environ.get("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)

PINK

sniped_messages = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Dropdown Help View
class HelpMenu(discord.ui.View):
    @discord.ui.select(
        placeholder="Choose a category...",
        options=[
            discord.SelectOption(label="utility", description="cmds for convenience"),
            discord.SelectOption(label="moderation", description="server moderation cmds"),
            discord.SelectOption(label="entertainment", description="fun and games"),
            discord.SelectOption(label="giveaways", description="giveaway cmds"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        embeds = {
            "utility": get_utility_embed(),
            "moderation": get_moderation_embed(),
            "entertainment": get_entertainment_embed(),
            "giveaways": get_giveaway_embed()
        }
        await interaction.response.edit_message(embed=embeds[category], view=self)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="<:infoo:1366957200442130484> help menu", description="- select a category below to view commands\n-more commands coming soon", color=discord.Color.blue())
    await ctx.send(embed=embed, view=HelpMenu())

# --------- HELP EMBEDS ---------
def get_utility_embed():
    embed = discord.Embed(title="Utility Commands", color=discord.Color.green())
    embed.add_field(name=";afk [reason]", value="Set your AFK status.", inline=False)
    embed.add_field(name=";clearafk", value="Clear your AFK status.", inline=False)
    embed.add_field(name=";snipe", value="Show the last deleted message.", inline=False)
    embed.add_field(name=";avatar [user]", value="Get the avatar of a user.", inline=False)
    embed.add_field(name=";banner [user]", value="Get the banner of a user.", inline=False)
    embed.add_field(name=";userinfo [user]", value="Show user information.", inline=False)
    embed.add_field(name=";mc", value="Show the server's member count.", inline=False)
    embed.add_field(name=";serverinfo", value="View server information.", inline=False)
    embed.add_field(name=";translate <text>", value="Translate text into a fun style.", inline=False)
    embed.add_field(name=";rename <new name>", value="Rename the current channel.", inline=False)
    return embed

def get_moderation_embed():
    embed = discord.Embed(title="Moderation Commands", color=discord.Color.red())
    embed.add_field(name=";timeout <user> <seconds> [reason]", value="Timeout a user for a duration.", inline=False)
    embed.add_field(name=";kick <user> [reason]", value="Kick a user from the server.", inline=False)
    embed.add_field(name=";ban <user> [reason]", value="Ban a user from the server.", inline=False)
    return embed

def get_entertainment_embed():
    embed = discord.Embed(title="Entertainment Commands", color=discord.Color.purple())
    embed.add_field(name=";roast", value="Get a random roast.", inline=False)
    embed.add_field(name=";8ball <question>", value="Ask the magic 8-ball.", inline=False)
    embed.add_field(name=";calc <expression>", value="Calculate a math expression.", inline=False)
    embed.add_field(name=";dare", value="Get a random dare.", inline=False)
    return embed

def get_giveaway_embed():
    embed = discord.Embed(title="Giveaway Commands", color=discord.Color.gold())
    embed.add_field(name=";gw start <prize> <duration in seconds> <winners>", value="Start a giveaway.", inline=False)
    embed.add_field(name=";gw end", value="Manually end a giveaway (placeholder).", inline=False)
    return embed

# --------- UTILITY ---------
@bot.command()
async def afk(ctx, *, reason="AFK"):
    await ctx.send(embed=discord.Embed(description=f"{ctx.author.mention} is now AFK: {reason}", color=discord.Color.blue()))

@bot.command()
async def clearafk(ctx):
    await ctx.send(embed=discord.Embed(description=f"{ctx.author.mention} is no longer AFK.", color=discord.Color.blue()))

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    sniped_messages[message.channel.id] = (message.content, message.author, datetime.datetime.now())

@bot.command()
async def snipe(ctx):
    data = sniped_messages.get(ctx.channel.id)
    if data:
        content, author, time = data
        embed = discord.Embed(description=content, color=discord.Color.orange(), timestamp=time)
        embed.set_author(name=author.name, icon_url=author.display_avatar.url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(description="There's nothing to snipe!", color=discord.Color.red()))

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="chaos ga kiwamaru")
    await bot.change_presence(status=discord.Status.idle, activity=activity)
        
bot.run(TOKEN)
