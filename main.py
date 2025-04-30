import discord
from discord.ext import commands
import asyncio, random, datetime
import os

TOKEN = os.environ.get("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)

PINK = discord.Color.from_str("#FFB6C1")
BLUE = discord.Color.from_str("#A9D7F1")
GREEN = discord.Color.from_str("#9DB19F")
GRAY = discord.Color.from_str("#1A1A1E")
RED = discord.Color.from_str("#FF5151")

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
async def menu(ctx):
    embed = discord.Embed(title="<:infoo:1366957200442130484> help menu", description="- select a category below to view commands\n- more commands coming soon", color=PINK)
    await ctx.send(embed=embed, view=HelpMenu())

# --------- HELP EMBEDS ---------
def get_utility_embed():
    embed = discord.Embed(title="<:swan_whitedot:1200263463214260274>utility commands", color=BLUE)
    embed.add_field(name=";afk [reason]", value="set your afk status", inline=False)
    embed.add_field(name=";clearafk", value="clear your afk status", inline=False)
    embed.add_field(name=";snipe", value="show the last deleted message", inline=False)
    embed.add_field(name=";avatar [user]", value="get the avatar of a user", inline=False)
    embed.add_field(name=";banner [user]", value="get the banner of a user", inline=False)
    embed.add_field(name=";userinfo [user]", value="show user information", inline=False)
    embed.add_field(name=";mc", value="show the server's member count", inline=False)
    embed.add_field(name=";serverinfo", value="view server information", inline=False)
    embed.add_field(name=";translate <text>", value="translate text into a fun style", inline=False)
    embed.add_field(name=";rename <new name>", value="rename the current channel", inline=False)
    return embed

def get_moderation_embed():
    embed = discord.Embed(title="<:swan_whitedot:1200263463214260274>moderation commands", color=BLUE)
    embed.add_field(name=";timeout <user> <seconds> [reason]", value="timeout a user for a duration", inline=False)
    embed.add_field(name=";kick <user> [reason]", value="kick a user from the server", inline=False)
    embed.add_field(name=";ban <user> [reason]", value="ban a user from the server", inline=False)
    return embed

def get_entertainment_embed():
    embed = discord.Embed(title="<:swan_whitedot:1200263463214260274>entertainment commands", color=BLUE)
    embed.add_field(name=";roast", value="get a random roast", inline=False)
    embed.add_field(name=";8ball <question>", value="ask the magic 8-ball", inline=False)
    embed.add_field(name=";calc <expression>", value="calculate a math expression", inline=False)
    embed.add_field(name=";dare", value="get a random dare", inline=False)
    return embed

def get_giveaway_embed():
    embed = discord.Embed(title="<:swan_whitedot:1200263463214260274>giveaway commands", color=BLUE)
    embed.add_field(name=";gw start <prize> <duration in seconds> <winners>", value="start a giveaway", inline=False)
    embed.add_field(name=";gw end", value="manually end a giveaway", inline=False)
    return embed

# --------- UTILITY ---------
@bot.command()
async def afk(ctx, *, reason="AFK"):
    await ctx.send(embed=discord.Embed(description=f"{ctx.author.mention} is now afk: {reason} ʚଓ", color=GREEN))

@bot.command()
async def clearafk(ctx):
    await ctx.send(embed=discord.Embed(description=f"{ctx.author.mention} is no longer afk ⊹", color=GREEN))

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
        embed = discord.Embed(description=content, color=GREEN, timestamp=time)
        embed.set_author(name=author.name, icon_url=author.display_avatar.url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(description="there's **nothing** to snipe!", color=discord.Color.red()))

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(embed=discord.Embed(title=f"{member.name}'s avatar", color=GREEN).set_image(url=member.display_avatar.url))

@bot.command()
async def banner(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = await bot.fetch_user(member.id)
    if user.banner:
        await ctx.send(embed=discord.Embed(title=f"{member.name}'s banner", color=GREEN).set_image(url=user.banner.url))
    else:
        await ctx.send(embed=discord.Embed(description="user has no banner.", color=discord.Color.red()))

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member}", color=GREEN)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="joined", value=member.joined_at.strftime('%Y-%m-%d'))
    embed.add_field(name="created", value=member.created_at.strftime('%Y-%m-%d'))
    await ctx.send(embed=embed)

@bot.command()
async def mc(ctx):
    await ctx.send(embed=discord.Embed(description=f"current server member count: {ctx.guild.member_count} <a:souop:1365540831460589679>", color=GREEN))

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=guild.name, description="server information", color=GREEN)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
    embed.add_field(name="members", value=guild.member_count)
    embed.add_field(name="created", value=guild.created_at.strftime('%Y-%m-%d'))
    embed.add_field(name="owner", value=guild.owner)
    await ctx.send(embed=embed)

@bot.command()
async def translate(ctx, *, text):
    translated = text[::-1]  # Just for fun (fake "translation")
    await ctx.send(embed=discord.Embed(description=translated, color=GREEN))

@bot.command()
async def rename(ctx, *, name):
    await ctx.channel.edit(name=name)
    await ctx.send(embed=discord.Embed(description=f"renamed channel to **{name}**", color=GREEN))

# --------- MODERATION ---------
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, seconds: int, *, reason="No reason"):
    duration = datetime.timedelta(seconds=seconds)
    await member.timeout(duration, reason=reason)
    await ctx.send(embed=discord.Embed(description=f"> <:white_checkmark:1365575468958355568> timed out {member.mention} for {seconds} seconds.", color=PINK))

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(embed=discord.Embed(description=f"> <:white_checkmark:1365575468958355568> kicked {member.mention}", color=BLUE))

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(embed=discord.Embed(description=f"> <:white_checkmark:1365575468958355568> banned {member.mention}", color=GREEN))

# --------- ENTERTAINMENT ---------
@bot.command()
async def roast(ctx):
    roasts = ["You're like a cloud. When you disappear, it's a beautiful day.", "You have a face that would make onions cry.", "I was thinking about you today. It reminded me to take out the trash.", "You just might be why the middle finger was invented in the first place.", "Is your name Wi-Fi? Because I'm not feeling a connection.", "I'd smack you, but I'm against animal abuse."]
    await ctx.send(embed=discord.Embed(description=random.choice(roasts), color=GREEN))

@bot.command()
async def dare(ctx):
    dares = ["Send the lyrics to your favorite song to your friend.", "Change your nickname to 'Sussy Baka' for 10 mins.", "Block the fifth person in your DMs.", "Slap your face.", "Tell the 3rd person in your DMs that you love them.", "Show everyone here your screen time.", "Type with only one hand for the next minute.", "Change your status to 'I'm a furry, deal with it uwu'"]
    await ctx.send(embed=discord.Embed(description=random.choice(dares), color=BLUE))

@bot.command(name="8ball")
async def _8ball(ctx, *, question):
    responses = ["Yes", "No", "Maybe", "Absolutely!", "Ask again later."]
    await ctx.send(embed=discord.Embed(title="<a:8ball:1366964824214343742> 8ball", description=random.choice(responses), color=GRAY))

@bot.command()
async def calc(ctx, *, expression):
    try:
        result = eval(expression)
        await ctx.send(embed=discord.Embed(description=f"> result: **{result}** ♡", color=PINK))
    except:
        await ctx.send(embed=discord.Embed(description="Invalid expression.", color=discord.Color.red()))

# --------- GIVEAWAYS ---------
giveaways = {}

@bot.command(name="gw")
async def gw(ctx, subcommand=None, *args):
    if subcommand == "start":
        if len(args) < 3:
            return await ctx.send(embed=discord.Embed(description="usage: **;gw start <prize> <duration in seconds> <winners>**", color=discord.Color.red()))

        prize, duration, winners = args[0], int(args[1]), int(args[2])
        embed = discord.Embed(
            title="new giveaway!",
            description=f"prize: **{prize}**\n<a:starspin1:1366981590172831814> react with 🎉 to enter!",
            color=RED,
            timestamp=datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
        )
        embed.set_footer(text=f"hosted by {ctx.author}")
        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")

        await asyncio.sleep(duration)
        new_msg = await ctx.channel.fetch_message(message.id)
        users = await new_msg.reactions[0].users().flatten()
        users = [u for u in users if not u.bot]
        
        if not users:
            await ctx.send(embed=discord.Embed(description="No valid entries.", color=discord.Color.red()))
        else:
            winners_list = random.sample(users, min(winners, len(users)))
            await ctx.send(embed=discord.Embed(
                title="giveaway ended!",
                description=f"<a:OrangeStar:1366981753675452509> winners: {', '.join(u.mention for u in winners_list)}",
                color=GREEN
            ))

    elif subcommand == "end":
        await ctx.send(embed=discord.Embed(description="Manual giveaway ending is not implemented yet.", color=discord.Color.orange()))

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="over /rokku ⚽")
    await bot.change_presence(status=discord.Status.idle, activity=activity)
        
bot.run(TOKEN)
