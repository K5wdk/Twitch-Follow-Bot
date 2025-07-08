import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
import asyncio
import subprocess
import aiohttp
import hashlib
import os
import re
import aiofiles
import random

TOKEN = "MTMxNTMzMTI1MDU2Mjc5NzU5OA.GTZ3Em.1BA-dbfhG7JV8SukHviKyNyrOGHYGmU9SVaaOI"
admin_ids = [982591976392232960]
ALLOWED_GUILD_ID = 1391735132540506113

intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)
queue = []

LAST_HASHES = {
    "Assets/tokens.txt": None,
    "Assets/kahoot.txt": None
}

async def check_and_announce_updates(bot):
    await bot.wait_until_ready()
    channel = bot.get_channel(1391732747365777478)

    while not bot.is_closed():
        for file_path in LAST_HASHES.keys():
            if not os.path.exists(file_path):
                continue

            with open(file_path, "rb") as f:
                content = f.read()
                hash_now = hashlib.md5(content).hexdigest()

            if LAST_HASHES[file_path] != hash_now:
                LAST_HASHES[file_path] = hash_now
                file_name = os.path.basename(file_path)
                await channel.send(f"📦 **{file_name}** was updated!")
        await asyncio.sleep(10)

@bot.event
async def on_ready():
    print(f"✅ LuBot is online as {bot.user}")
    bot.loop.create_task(check_and_announce_updates(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"⚠️ Error: {error}")
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Bro are you trying to trick me? Common G. This bot doesn't work here.")
        return
    raise error

@bot.check
def global_guild_check(ctx):
    return ctx.guild and ctx.guild.id == ALLOWED_GUILD_ID

##################################
# --- Menu ---
##################################
@bot.command()
async def secmenu(ctx):
    if ctx.author.id not in admin_ids:
        return

    embed = nextcord.Embed(
        title="LuBot Command Panel",
        description="> `No Refund Policy – Use responsibly.`",
        color=nextcord.Color.purple()
    )

    embed.set_image(url="https://media.discordapp.net/attachments/1391732747365777478/1391734821449109554/standard.gif")

    embed.add_field(
        name="🆓 Free Bot Commands",
        value=(
            "> **Twitch Follow Bot**: `.tfollow (username)`\n"
            "> **Kahoot Raid Bot**: `.kraid (PIN)`\n"
        ),
        inline=False
    )

    embed.add_field(
        name="💎 Premium Commands",
        value=(
            "> **Twitch Chat Spam**: `.tspam (username) (msg)`\n"
            "> **Twitch Live Views**: `.tlive (username)`\n"
            "> **Twitch Token Checker**: `.checktokens` + `.txt`\n"
            "> **Discord Token Checker**: `.checkdiscord` + `.txt`"
        ),
        inline=False
    )

    embed.add_field(
        name="🦎 Booster Commands",
        value=(
            "> **Account Generator**: `.gen`\n"
            "> **Roblox Follow Bot**: `.rfollow (user ID)`"
        ),
        inline=False
    )

    embed.set_footer(text="Use .help for more | Developed by LuTeam")

    await ctx.send(embed=embed, view=TicketButtonView())

########################
# --- Twitch Followers ---
########################
@bot.command()
async def tfollow(ctx, username: str, amount: int = 30):
    if amount > 30:
        amount = 30
    elif amount < 1:
        amount = 1

    if not username or len(username) < 3:
        embed = nextcord.Embed(
            description="❌ Username not found. Please enter a valid Twitch username.",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    try:
        with open("Assets/tokens.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        tokens = []

    if len(tokens) == 0:
        embed = nextcord.Embed(
            description="⚠️ No tokens available in stock. Please restock and try again.",
            color=nextcord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    embed = nextcord.Embed(
        description=f"Send **{amount}** followers to **{username}**",
        color=nextcord.Color.purple()
    )
    await ctx.send(embed=embed)

########################
# --- Twitch Chat Spam ---
########################
@bot.command()
async def tspam(ctx, channel: str, *, message: str = "Spam Message"):
    embed = nextcord.Embed(
        description=f"Send Spam Message to **{channel}**",
        color=nextcord.Color.purple()
    )
    await ctx.send(embed=embed)

########################
# --- Twitch Live Views ---
########################
@bot.command()
async def tlive(ctx, username: str):
    await ctx.send(f"Live view boost started for **{username}**")


########################
# --- Roblox Follow Bot ---
########################
@bot.command()
async def tclip(ctx, username: str):
    await ctx.send(f"Send Followers to **{username}**")

########################
# --- Gen Command ---
########################
class GenAccountView(View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx

    async def send_account(self, interaction: nextcord.Interaction, service: str, icon_url: str):
        filename = f"Assets/{service.lower()}_accounts.txt"
        try:
            async with aiofiles.open(filename, mode="r") as f:
                lines = await f.readlines()
        except FileNotFoundError:
            await interaction.response.send_message(f"❌ `{service}_accounts.txt` not found.", ephemeral=True)
            return

        if not lines:
            await interaction.response.send_message(f"⚠️ No {service} accounts in stock.", ephemeral=True)
            return

        account = random.choice(lines).strip()
        embed = nextcord.Embed(
            title=f"Your {service} Account",
            description=f"```{account}```",
            color=nextcord.Color.blurple()
        )
        embed.set_thumbnail(url=icon_url)

        try:
            dm = await interaction.user.send(embed=embed)
            await interaction.response.send_message(f"📩 {service} account sent via DM!", ephemeral=True)
            await asyncio.sleep(120)
            await dm.delete()
        except nextcord.Forbidden:
            await interaction.response.send_message("❌ I couldn't DM you. Please enable DMs.", ephemeral=True)

    @nextcord.ui.button(label="Spotify", style=nextcord.ButtonStyle.green)
    async def spotify(self, button: Button, interaction: nextcord.Interaction):
        await self.send_account(interaction, "Spotify", "https://cdn-icons-png.flaticon.com/512/174/174872.png")

    @nextcord.ui.button(label="Netflix", style=nextcord.ButtonStyle.red)
    async def netflix(self, button: Button, interaction: nextcord.Interaction):
        await self.send_account(interaction, "Netflix", "https://cdn-icons-png.flaticon.com/512/732/732228.png")

    @nextcord.ui.button(label="Disney+", style=nextcord.ButtonStyle.blurple)
    async def disney(self, button: Button, interaction: nextcord.Interaction):
        await self.send_account(interaction, "Disney", "https://cdn-icons-png.flaticon.com/512/732/732255.png")

@bot.command()
async def gen(ctx):
    embed = nextcord.Embed(
        title="🎁 Account Generator",
        description="Select a service below to receive a random unchecked account.",
        color=nextcord.Color.dark_purple()
    )
    await ctx.send(embed=embed, view=GenAccountView(ctx))


########################
# --- Stock Command ---
########################
@bot.command()
async def stock(ctx):
    def count_lines(path):
        try:
            with open(path, "r") as f:
                return sum(1 for line in f if line.strip())
        except FileNotFoundError:
            return 0

    token_count = count_lines("Assets/tokens.txt")
    kahoot_count = count_lines("Assets/kahoot.txt")

    embed = nextcord.Embed(
        title="📦 Stock Information",
        color=nextcord.Color.green()
    )
    embed.add_field(name="Tokens", value=f"`{token_count}`", inline=True)
    embed.add_field(name="Kahoot Accounts", value=f"`{kahoot_count}`", inline=True)

    await ctx.send(embed=embed)

########################
# --- Clear Command ---
########################
@bot.command()
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"Cleared `{amount}` messages.")
    await asyncio.sleep(2)
    await msg.delete()

########################
# --- Say Command ---
########################

@bot.command()
async def say(ctx, *, message: str):
    if ctx.author.id not in admin_ids:
        return
    await ctx.send(message)

##################################
# --- Ticket System ---
##################################
class TicketButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="🎟️ Support Ticket / Purchase Ticket", style=nextcord.ButtonStyle.blurple, custom_id="open_ticket")
    async def open_ticket_button(self, button: Button, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await create_ticket(interaction)

async def create_ticket(interaction: nextcord.Interaction):
    guild = interaction.guild
    user = interaction.user

    overwrites = {
        guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
        user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: nextcord.PermissionOverwrite(read_messages=True)
    }

    channel_name = f"ticket-{user.name}".lower().replace(" ", "-")
    existing = nextcord.utils.get(guild.channels, name=channel_name)

    if existing:
        await interaction.followup.send("❗ You already have an open ticket.", ephemeral=True)
        return

    channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

    intro_embed = nextcord.Embed(
        title="🎟️ Ticket Opened",
        description="Welcome! What brings you here?\n\n➔ Choose an option below.\n⏳ You have 5 minutes or the ticket will close.",
        color=nextcord.Color.purple()
    )

    main_view = View(timeout=300)

    async def close_ticket_timeout():
        await asyncio.sleep(300)
        await channel.send("Ticket closed due to inactivity.")
        await channel.delete()

    timeout_task = asyncio.create_task(close_ticket_timeout())

    async def handle_choice(inter: nextcord.Interaction, choice: str):
        if inter.user != user:
            await inter.response.send_message("Only the ticket creator can respond.", ephemeral=True)
            return

        timeout_task.cancel()

        if choice == "technical":
            await inter.response.edit_message(embed=nextcord.Embed(
                title="🔧 Technical Help",
                description="What type of technical problem are you having?",
                color=nextcord.Color.blue()
            ), view=TechnicalHelpView(user, channel))
        else:
            await inter.response.edit_message(embed=nextcord.Embed(
                title="🛒 Purchase Menu",
                description="What would you like to buy?",
                color=nextcord.Color.gold()
            ), view=PurchaseView(user, channel))

        def check(m): return m.channel == channel and m.author == user

        async def listen_for_questions():
            while True:
                try:
                    msg = await bot.wait_for("message", timeout=300, check=check)
                    content = msg.content.lower()
                    if any(word in content for word in ["how much", "cost"]):
                        await channel.send("Premium plan cost **20$** just open your eyes and read.")
                    elif any(word in content for word in ["free", "can you"]):
                        await channel.send("No, nothing is free. Premium features require payment.")
                    elif any(word in content for word in ["when", "how long", "wait", "work"]):
                        await channel.send("Our service usually works within a few minutes. Please stay patient.")
                except asyncio.TimeoutError:
                    await channel.send("Ticket closed due to inactivity.")
                    await channel.delete()
                    break

        asyncio.create_task(listen_for_questions())

    btn1 = Button(label="❓ Technical Help", style=nextcord.ButtonStyle.blurple)
    btn2 = Button(label="💸 I want to buy", style=nextcord.ButtonStyle.green)
    btn1.callback = lambda i: handle_choice(i, "technical")
    btn2.callback = lambda i: handle_choice(i, "purchase")
    main_view.add_item(btn1)
    main_view.add_item(btn2)

    await channel.send(f"{user.mention}", embed=intro_embed, view=main_view)

class PurchaseView(View):
    def __init__(self, user, channel):
        super().__init__(timeout=300)
        self.user = user
        self.channel = channel

    @nextcord.ui.button(label="🌌 Premium Plan", style=nextcord.ButtonStyle.green)
    async def premium_plan(self, button: Button, inter: nextcord.Interaction):
        if inter.user != self.user:
            await inter.response.send_message("Not your ticket.", ephemeral=True)
            return

        await inter.response.edit_message(embed=nextcord.Embed(
            title="💳 Payment Method",
            description="How would you like to pay?",
            color=nextcord.Color.gold()
        ), view=PaymentViewPremium(self.user, self.channel))

    @nextcord.ui.button(label="🛒 Tokens", style=nextcord.ButtonStyle.green)
    async def buy_tokens(self, button: Button, inter: nextcord.Interaction):
        if inter.user != self.user:
            await inter.response.send_message("Not your ticket.", ephemeral=True)
            return

        await inter.response.edit_message(embed=nextcord.Embed(
            title="How many tokens do you want to buy?",
            color=nextcord.Color.gold()
        ), view=TokenViewTokens(self.channel, self.user))

class PaymentViewPremium(View):
    def __init__(self, user, channel):
        super().__init__(timeout=300)
        self.user = user
        self.channel = channel

    @nextcord.ui.button(label="Crypto", style=nextcord.ButtonStyle.blurple)
    async def crypto(self, button: Button, inter: nextcord.Interaction):
        if inter.user != self.user:
            await inter.response.send_message("Not your ticket.", ephemeral=True)
            return

        await inter.response.edit_message(embed=nextcord.Embed(
            title="🪙 Crypto Payment",
            description="Send **20$ USDT** to:\n```YOUR-USDT-ADDRESS```",
            color=nextcord.Color.dark_gold()
        ), view=None)

        await self.channel.send("@Admin A user is ready to pay for **Premium Plan** with **Crypto**.")

    @nextcord.ui.button(label="PayPal", style=nextcord.ButtonStyle.gray)
    async def paypal(self, button: Button, inter: nextcord.Interaction):
        if inter.user != self.user:
            await inter.response.send_message("Not your ticket.", ephemeral=True)
            return

        await inter.response.edit_message(embed=nextcord.Embed(
            title="💸 PayPal Payment",
            description="Send **20$ Friends & Family** with subject 'gas station' to:\n```test@lumail.com```",
            color=nextcord.Color.dark_gray()
        ), view=None)

        await self.channel.send("@Admin A user is ready to pay for **Premium Plan** with **PayPal**.")

class TokenViewTokens(View):
    def __init__(self, channel, user):
        super().__init__(timeout=300)
        self.channel = channel
        self.user = user

    @nextcord.ui.button(label="100 Tokens – 2€", style=nextcord.ButtonStyle.blurple)
    async def buy_100(self, button: Button, inter: nextcord.Interaction):
        if inter.user != self.user:
            await inter.response.send_message("Not your ticket.", ephemeral=True)
            return

        await inter.response.edit_message(embed=nextcord.Embed(
            title="🪙 100 Tokens Purchase",
            description="Send **2€ in Crypto** to:\n```YOUR-ADDRESS-HERE```",
            color=nextcord.Color.dark_gold()
        ), view=None)

        await self.channel.send("@Admin A user is ready to pay for **100 Tokens** via **Crypto**.")

    @nextcord.ui.button(label="1000 Tokens – 8€", style=nextcord.ButtonStyle.green)
    async def buy_1000(self, button: Button, inter: nextcord.Interaction):
        if inter.user != self.user:
            await inter.response.send_message("Not your ticket.", ephemeral=True)
            return

        await inter.response.edit_message(embed=nextcord.Embed(
            title="🪙 1000 Tokens Purchase",
            description="Send **8€ in Crypto** to:\n```YOUR-ADDRESS-HERE```",
            color=nextcord.Color.dark_green()
        ), view=None)

        await self.channel.send("@Admin A user is ready to pay for **1000 Tokens** via **Crypto**.")

    @nextcord.ui.button(label="5000 Tokens – 15€", style=nextcord.ButtonStyle.gray)
    async def buy_5000(self, button: Button, inter: nextcord.Interaction):
        if inter.user != self.user:
            await inter.response.send_message("Not your ticket.", ephemeral=True)
            return

        await inter.response.edit_message(embed=nextcord.Embed(
            title="🪙 5000 Tokens Purchase",
            description="Send **15€ in Crypto** to:\n```YOUR-ADDRESS-HERE```",
            color=nextcord.Color.dark_gray()
        ), view=None)

        await self.channel.send("@Admin A user is ready to pay for **5000 Tokens** via **Crypto**.")

class TechnicalHelpView(View):
    def __init__(self, user, channel):
        super().__init__(timeout=300)
        self.user = user
        self.channel = channel

    @nextcord.ui.button(label="Login Problem", style=nextcord.ButtonStyle.red)
    async def login_issue(self, button: Button, inter: nextcord.Interaction):
        if inter.user != self.user:
            await inter.response.send_message("Not your ticket.", ephemeral=True)
            return

        await inter.response.edit_message(embed=nextcord.Embed(
            title="🔐 Login Help",
            description="Make sure your credentials are correct. An admin will assist you shortly.",
            color=nextcord.Color.blue()
        ), view=None)
        await self.channel.send("@Admin A user reported a **login issue**.")

    @nextcord.ui.button(label="Bot not responding", style=nextcord.ButtonStyle.red)
    async def bot_not_working(self, button: Button, inter: nextcord.Interaction):
        if inter.user != self.user:
            await inter.response.send_message("Not your ticket.", ephemeral=True)
            return

        await inter.response.edit_message(embed=nextcord.Embed(
            title="🤖 Bot Help",
            description="Try restarting the bot or checking logs. An admin will assist you shortly.",
            color=nextcord.Color.blue()
        ), view=None)
        await self.channel.send("@Admin A user reported the **bot is not responding**.")

    class TechnicalHelpView(View):
        def __init__(self):
            super().__init__(timeout=300)

        @nextcord.ui.button(label="Something is not working", style=nextcord.ButtonStyle.red)
        async def login_issue(self, button: Button, inter: nextcord.Interaction):
            if inter.user != user:
                await inter.response.send_message("Not your ticket.", ephemeral=True)
                return

            await inter.response.edit_message(embed=nextcord.Embed(
                title="Help",
                description="Make sure your credentials are correct.\nAn admin will assist you shortly.",
                color=nextcord.Color.blue()
            ), view=None)
            await channel.send("@Admin A user reported a **Error**.")

        @nextcord.ui.button(label="Bot not responding", style=nextcord.ButtonStyle.red)
        async def bot_not_working(self, button: Button, inter: nextcord.Interaction):
            if inter.user != user:
                await inter.response.send_message("Not your ticket.", ephemeral=True)
                return

            await inter.response.edit_message(embed=nextcord.Embed(
                title="🤖 Bot Help",
                description="We will check your problem\nAn admin will assist you shortly.",
                color=nextcord.Color.blue()
            ), view=None)
            await channel.send("@Admin A user reported the **bot is not responding**.")

##################################
# --- Close Command ---
##################################
@bot.command()
async def close(ctx):
    if "ticket" not in ctx.channel.name:
        await ctx.send("❌ This command can only be used in ticket channels.")
        return

    embed = nextcord.Embed(
        title="🔒 Close Ticket",
        description="Are you sure you want to close this ticket?\nThis action **cannot be undone**.",
        color=nextcord.Color.red()
    )
    view = View()

    class ConfirmButton(Button):
        def __init__(self):
            super().__init__(label="✅ Yes, close", style=nextcord.ButtonStyle.red)

        async def callback(self, interaction: nextcord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Only the person who used the command can confirm.", ephemeral=True)
                return
            await interaction.response.send_message("🗑️ Ticket will now be closed.", ephemeral=True)
            await ctx.channel.delete()

    class CancelButton(Button):
        def __init__(self):
            super().__init__(label="❌ Cancel", style=nextcord.ButtonStyle.gray)

        async def callback(self, interaction: nextcord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Only the person who used the command can cancel.", ephemeral=True)
                return
            await interaction.response.edit_message(content="❎ Ticket closure cancelled.", embed=None, view=None)

    view.add_item(ConfirmButton())
    view.add_item(CancelButton())

    await ctx.send(embed=embed, view=view)


######################################
# --- Token Checker (.checktokens)---
######################################
@bot.command()
async def checktokens(ctx):
    import aiohttp, asyncio

    tokens_file = "Assets/tokens.txt"
    log_channel_id = 1391732747365777478

    try:
        with open(tokens_file, "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        await ctx.send("❌ `tokens.txt` not found.")
        return

    if not tokens:
        await ctx.send("⚠️ No tokens in stock.")
        return

    loading_embed = nextcord.Embed(
        title="🔍 Checking Twitch tokens...",
        color=nextcord.Color.orange()
    )
    msg = await ctx.send(embed=loading_embed)

    valid_tokens = []
    invalid_tokens = []

    headers_template = {
        "Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko",
        "Content-Type": "application/json"
    }

    payload = [{
        "operationName": "BitsCard_Bits",
        "variables": {},
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "fe1052e19ce99f10b5bd9ab63c5de15405ce87a1644527498f0fc1aadeff89f2"
            }
        }
    }]

    async with aiohttp.ClientSession() as session:
        for token in tokens:
            headers = headers_template.copy()
            headers["Authorization"] = f"OAuth {token}"

            try:
                async with session.post("https://gql.twitch.tv/gql", headers=headers, json=payload, timeout=5) as resp:
                    text = await resp.text()
                    if "token is invalid" in text.lower():
                        invalid_tokens.append(token)
                    else:
                        valid_tokens.append(token)
            except Exception:
                invalid_tokens.append(token)

            await asyncio.sleep(0.2)

    with open(tokens_file, "w") as f:
        for t in valid_tokens:
            f.write(t + "\n")

    result_embed = nextcord.Embed(
        title="✅ Token Check Complete",
        description=(
            f"**Valid Tokens**: `{len(valid_tokens)}`\n"
            f"**Invalid Tokens**: `{len(invalid_tokens)}`\n"
            f"`Updated tokens.txt`"
        ),
        color=nextcord.Color.green()
    )
    await msg.edit(embed=result_embed)

    log_channel = bot.get_channel(log_channel_id)
    if log_channel:
        await log_channel.send(
            f"✅ Token Restock Complete\n"
            f"Restocked: {len(valid_tokens)}\n"
            f"Outdated: {len(invalid_tokens)}\n"
            f"Updated tokens.txt"
        )

########################
# --- Ban Command ---
########################
@bot.command()
async def ban(ctx, user_id: int, *, reason: str = "No reason."):
    if ctx.author.id not in admin_ids:
        return

    try:
        user = await bot.fetch_user(user_id)
        
        try:
            await user.send(f"You have been banned from **{ctx.guild.name}**.\nReason: `{reason}`")
        except:
            pass

        await ctx.guild.ban(user, reason=reason)

        embed = nextcord.Embed(
            title="User Banned",
            description=f"`{user.name}` (`{user.id}`) was banned.\n\nReason: `{reason}`",
            color=nextcord.Color.dark_gray()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Failed to ban user: `{e}`")


########################
# --- Unban All Command ---
########################
@bot.command(name="unbanall")
async def unban_all(ctx):
    if ctx.author.id not in admin_ids:
        return

    banned_users = await ctx.guild.bans()
    count = 0

    for ban_entry in banned_users:
        user = ban_entry.user
        try:
            await ctx.guild.unban(user)
            count += 1
        except:
            pass

    embed = nextcord.Embed(
        title="Unban Complete",
        description=f"Unbanned `{count}` users from the server.",
        color=nextcord.Color.green()
    )
    await ctx.send(embed=embed)

########################
# --- Blacklist Command ---
########################
blacklisted_users = []

@bot.command()
async def blacklist(ctx, user_id: int):
    if ctx.author.id not in admin_ids:
        return

    if user_id in blacklisted_users:
        await ctx.send(f"`{user_id}` is already blacklisted.")
        return

    blacklisted_users.append(user_id)
    await ctx.send(f"`{user_id}` has been blacklisted.")

@bot.check
async def block_blacklisted_users(ctx):
    if ctx.author.id in blacklisted_users:
        raise commands.CheckFailure("You are blacklisted.")
    return True

########################
# --- Role Command ---
########################
@bot.command()
async def role(ctx, *, role_name):
    if ctx.channel.id != bots_channel:
        await ctx.send("Wrong channel.")
        return

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send("Role not found.")
        return

    if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
        await ctx.send(f"Removed role `{role.name}`.")
    else:
        await ctx.author.add_roles(role)
        await ctx.send(f"Added role `{role.name}`.")

bot.run(TOKEN)
