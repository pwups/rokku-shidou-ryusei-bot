import discord
from discord.ext import commands, tasks
from discord.ui import Select, View, Button
import asyncio
import datetime
import random
import os

TOKEN = os.environ.get("TOKEN")bot.run(TOKEN)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=';', intents=intents)

GIVEAWAYS = {}
VANITY_STRING = "/rokku"
VANITY_ROLE_ID = 1210210286825644042  # change this to your role ID
VANITY_CHANNEL_ID = 1256253872977215590  # change this to your log channel ID
GIVEAWAY_EMOJI = "<a:z_whiteshimmer:1245959357032562801>"

# ====== DROPDOWN MENU ======
class CategoryView(View):
    @discord.ui.select(
        placeholder="select a category",
        options=[
            discord.SelectOption(label="home page"),
            discord.SelectOption(label="utility"),
            discord.SelectOption(label="moderation")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: Select):
        embed = discord.Embed(color=discord.Color.dark_gray())
        category = select.values[0].lower()

        if category == "utility":
            embed.description = (
                "<:Egoist:1359654205542895960> **utility**\n\n"
                ";snipe • snipes deleted messages\n"
                ";mc • shows the number of members in the guild\n"
                ";avatar <user> • shows a user’s avatar\n"
                ";banner <user> • shows a user’s banner"
            )
        elif category == "moderation":
            embed.description = (
                "<:Egoist:1359654205542895960> **moderation**\n\n"
                ";ban <user> (reason) • bans a member or user\n"
                ";kick <member> (reason) • kicks a member from the guild\n"
                ";mute <member> <time> (reason) • times out a member\n"
                ";unmute <member> (reason) • un-times out a member"
            )
        elif category == "home page":
            embed.description = "welcome to the bot! select a category to view commands.\n\nmore categories will be added soon!"

        await interaction.response.edit_message(embed=embed, view=self)

@bot.command()
async def menu(ctx):
    embed = discord.Embed(description="welcome to the bot! select a category to view commands.\n\nmore categories will be added soon!", color=discord.Color.dark_gray())
    await ctx.send(embed=embed, view=CategoryView())

# ====== UTILITY ======
last_deleted_message = {}

@bot.event
async def on_message_delete(message):
    if message.guild:
        last_deleted_message[message.guild.id] = message

@bot.command()
async def snipe(ctx):
    msg = last_deleted_message.get(ctx.guild.id)
    if msg:
        await ctx.send(f"**{msg.author}:** {msg.content}")
    else:
        await ctx.send("There's nothing to snipe!")

@bot.command()
async def mc(ctx):
    await ctx.send(f"members: {ctx.guild.member_count} ♡")

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.avatar.url)

@bot.command()
async def banner(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = await bot.fetch_user(member.id)
    await ctx.send(user.banner.url if user.banner else "No banner found.")

# ====== MODERATION ======
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    embed = discord.Embed(description=f"**{member} has been banned ⚠️**\nreason: {reason}", color=discord.Color.red())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    embed = discord.Embed(description=f"**{member} has been kicked ⚠️**\nreason: {reason}", color=discord.Color.orange())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, time: int, *, reason="No reason provided"):
    duration = discord.utils.utcnow() + datetime.timedelta(minutes=time)
    await member.timeout(until=duration, reason=reason)
    embed = discord.Embed(description=f"**{member} has been muted for {time} minutes ⚠️**\nreason: {reason}", color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.timeout(until=None, reason=reason)
    embed = discord.Embed(description=f"**{member} has been unmuted ⚠️**\nreason: {reason}", color=discord.Color.green())
    await ctx.send(embed=embed)

# ====== VANITY ROLE FEATURE ======
@tasks.loop(minutes=2)
async def check_vanity_status():
    guild = bot.get_guild(1199304544107114557)  # replace with your guild ID
    role = guild.get_role(VANITY_ROLE_ID)
    channel = bot.get_channel(VANITY_CHANNEL_ID)

    for member in guild.members:
        if member.bot:
            continue
        if member.activity and VANITY_STRING in str(member.activity):
            if role not in member.roles:
                await member.add_roles(role)
                embed = discord.Embed(
                    description=f"{member.mention} repped `{VANITY_STRING}` <a:14:1359119258088505582>",
                    color=discord.Color.from_rgb(255, 255, 255)
                )
                await channel.send(embed=embed)
        elif role in member.roles:
            if not member.activity or VANITY_STRING not in str(member.activity):
                await member.remove_roles(role)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_vanity_status.start()

# ====== GIVEAWAY FEATURE ======
@bot.command()
async def gw(ctx, subcommand=None, prize=None, duration=None, winners: int = 1):
    if subcommand != "start" or not prize or not duration:
        return await ctx.send("Usage: `.gw start <prize> <duration> <winners>`")

    seconds = convert_duration(duration)
    if seconds is None:
        return await ctx.send("Invalid duration format. Use s, m, h, or d (e.g., `1h`).")

    end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
    embed = discord.Embed(description=f"**prize:** {prize}\n- click the button to enter", color=discord.Color.pink())
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text=f"hosted by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    embed.timestamp = end_time

    button = Button(label="Join", style=discord.ButtonStyle.secondary, emoji=GIVEAWAY_EMOJI)
    view = View()
    view.add_item(button)

    message = await ctx.send(embed=embed, view=view)
    entrants = set()

    async def button_callback(interaction):
        if interaction.user.id not in entrants:
            entrants.add(interaction.user.id)
            await interaction.response.send_message("you entered the gw!", ephemeral=True)
        else:
            await interaction.response.send_message("you already entered the gw!", ephemeral=True)

    button.callback = button_callback

    await asyncio.sleep(seconds)

    if entrants:
        winners_list = list(entrants)
        random.shuffle(winners_list)
        picked = winners_list[:winners]
        mentions = " ".join(f"<@{user_id}>" for user_id in picked)
        await ctx.send(f"Congratulations {mentions}, you won **{prize}**!")
    else:
        await ctx.send("No one entered the giveaway.")

def convert_duration(duration_str):
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    try:
        return int(duration_str[:-1]) * units[duration_str[-1]]
    except:
        return None
        
