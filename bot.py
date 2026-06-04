import discord
from discord.ext import commands
import os
import asyncio

# Setup required gateway intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

# Bot Prefix is set to .
bot = commands.Bot(command_prefix=".", intents=intents)
STOCK_FILE = "mcfa_stock.txt"

# Ensure the stock file exists
if not os.path.exists(STOCK_FILE):
    with open(STOCK_FILE, "w") as f:
        pass

@bot.event
async def on_ready():
    # Set a cool custom status for MoonGenBot
    await bot.change_presence(activity=discord.Game(name="Minecraft | .stock"))
    print(f"✅ Logged in securely as {bot.user}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. AUTO ROLE & JOIN LOGS SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.event
async def on_member_join(member):
    # Automatically assigns the 'Member' role when someone joins
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Auto-role error: {e}")
            
    # Send a join log to a channel named 'logs'
    log_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if log_channel:
        embed = discord.Embed(title="📥 Member Joined", description=f"{member.mention} entered the server.", color=discord.Color.green())
        await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    # Send a leave log to a channel named 'logs'
    log_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if log_channel:
        embed = discord.Embed(title="📤 Member Left", description=f"**{member.name}** left the server.", color=discord.Color.red())
        await log_channel.send(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. MCFA STOCK SYSTEM (.add mcfa, .stock, .gen mcfa)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(administrator=True)
async def add(ctx, category: str = None, *, account_details: str = None):
    """Adds a Minecraft Full Access account (mail:pass) to the stock file. Deletes cmd instantly."""
    try:
        await ctx.message.delete()
    except:
        pass

    if not category or category.lower() != "mcfa" or not account_details:
        await ctx.send("❌ **Error:** Incorrect format! Use: `.add mcfa mail:pass`", delete_after=5)
        return

    if ":" not in account_details:
        await ctx.send("❌ **Format Error:** Account details must be strictly in `mail:pass` format.", delete_after=5)
        return

    # Add the account line safely to the file
    with open(STOCK_FILE, "a") as f:
        f.write(account_details.strip() + "\n")
    
    await ctx.send("📥 **Success:** MCFA account stored safely. Command cleared for privacy!", delete_after=5)
    
    # Send to logs channel
    log_channel = discord.utils.get(ctx.guild.text_channels, name="logs")
    if log_channel:
        await log_channel.send(f"🛠️ **Stock Update:** `{ctx.author.name}` added 1 item to MCFA stock.")

@bot.command()
async def stock(ctx):
    """Displays the exact number of accounts available. Deletes cmd instantly."""
    try:
        await ctx.message.delete()
    except:
        pass

    with open(STOCK_FILE, "r") as f:
        lines = f.readlines()
    
    count = len([line for line in lines if line.strip()])
    
    embed = discord.Embed(title="📦 CURRENT SERVER STOCK", color=discord.Color.blue())
    embed.add_field(name="🔹 MCFA Accounts (mail:pass)", value=f"`{count}` available items", inline=False)
    embed.set_footer(text="Use .gen mcfa to claim yours!")
    await ctx.send(embed=embed, delete_after=15) # Embed deletes after 15 seconds to keep chat clean

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user) # 1-minute cooldown to stop spamming
async def gen(ctx, type: str = None):
    """DMs a single stock line to the user. DOES NOT delete the command message."""
    if not type or type.lower() != "mcfa":
        await ctx.send("❌ **Error:** Please type `.gen mcfa` explicitly.")
        ctx.command.reset_cooldown(ctx)
        return

    with open(STOCK_FILE, "r") as f:
        lines = f.readlines()

    # Clean empty lines
    lines = [line.strip() for line in lines if line.strip()]

    if not lines:
        await ctx.send("😭 **Out of Stock!** Please wait for an Admin to restock `.add mcfa`.")
        ctx.command.reset_cooldown(ctx)
        return

    # Take the top item out of stock
    claimed_account = lines[0]
    remaining_stock = lines[1:]

    # Write remaining stock back to the file
    with open(STOCK_FILE, "w") as f:
        for line in remaining_stock:
            f.write(line + "\n")

    # Attempt to DM the user
    try:
        embed = discord.Embed(title="🔑 YOUR MCFA ACCOUNT", description=f"```\n{claimed_account}\n```", color=discord.Color.gold())
        embed.set_footer(text="Format is mail:pass. Keep this confidential!")
        await ctx.author.send(embed=embed)
        await ctx.send(f"📬 {ctx.author.mention}, **Check your DMs!** Your MCFA item has been sent safely.")
        
        # Log Claim
        log_channel = discord.utils.get(ctx.guild.text_channels, name="logs")
        if log_channel:
            await log_channel.send(f"🎁 **Stock Claimed:** `{ctx.author.name}` generated 1x MCFA account.")
            
    except discord.Forbidden:
        # If user DMs are closed, return the item to stock list
        with open(STOCK_FILE, "a") as f:
            f.write(claimed_account + "\n")
        await ctx.send(f"❌ {ctx.author.mention}, **Error:** I cannot DM you. Please turn on **'Allow Direct Messages from server members'** in privacy settings and try again.")
        ctx.command.reset_cooldown(ctx)

# Error handling for cooldowns
@gen.error
async def gen_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ **Cooldown Active:** Please wait `{error.retry_after:.1f}` seconds before generating again.", delete_after=5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. MODERATION & PURGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """Deletes bulk messages instantly. Clears cmd line text too."""
    if amount < 1:
        return await ctx.send("Specify a valid number above 0.")
    
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared `{len(deleted)-1}` messages cleanly.", delete_after=4)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason specified"):
    """Kicks a member from the guild"""
    try:
        await ctx.message.delete()
    except:
        pass
    await member.kick(reason=reason)
    await ctx.send(f"🔨 **{member.name}** was kicked successfully.", delete_after=5)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason specified"):
    """Bans a member from the guild"""
    try:
        await ctx.message.delete()
    except:
        pass
    await member.ban(reason=reason)
    await ctx.send(f"🔴 **{member.name}** has been banned permanently.", delete_after=5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. TICKET SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Open Claim Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"⚠️ You already have an open ticket running: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_chan = await guild.create_text_channel(name=f"ticket-{user.name}", overwrites=overwrites)
        
        view = CloseTicketView()
        embed = discord.Embed(title="🎟️ Ticket Created", description=f"Welcome {user.mention},\nStaff will arrive shortly. Click below to close the room when finished.", color=discord.Color.blurple())
        await ticket_chan.send(embed=embed, view=view)
        
        await interaction.response.send_message(f"✅ Ticket created successfully! Go to: {ticket_chan.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 *Closing room in 5 seconds...*")
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    """Sends the persistent landing panel button into your support channel"""
    try:
        await ctx.message.delete()
    except:
        pass
    embed = discord.Embed(title="🎟️ SERVER SUPPORT & CLAIMS", description="Need help or claiming invite/level milestone rewards?\nClick the button below to start a private discussion channel with staff.", color=discord.Color.dark_grey())
    await ctx.send(embed=embed, view=TicketButtons())

# MoonGenBot Secret Authentication Token
import discord
from discord.ext import commands
import os
import asyncio

# Setup required gateway intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

# Bot Prefix is set to .
bot = commands.Bot(command_prefix=".", intents=intents)
STOCK_FILE = "mcfa_stock.txt"

# Ensure the stock file exists
if not os.path.exists(STOCK_FILE):
    with open(STOCK_FILE, "w") as f:
        pass

@bot.event
async def on_ready():
    # Set a cool custom status for MoonGenBot
    await bot.change_presence(activity=discord.Game(name="Minecraft | .stock"))
    print(f"✅ Logged in securely as {bot.user}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. AUTO ROLE & JOIN LOGS SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.event
async def on_member_join(member):
    # Automatically assigns the 'Member' role when someone joins
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Auto-role error: {e}")
            
    # Send a join log to a channel named 'logs'
    log_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if log_channel:
        embed = discord.Embed(title="📥 Member Joined", description=f"{member.mention} entered the server.", color=discord.Color.green())
        await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    # Send a leave log to a channel named 'logs'
    log_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if log_channel:
        embed = discord.Embed(title="📤 Member Left", description=f"**{member.name}** left the server.", color=discord.Color.red())
        await log_channel.send(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. MCFA STOCK SYSTEM (.add mcfa, .stock, .gen mcfa)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(administrator=True)
async def add(ctx, category: str = None, *, account_details: str = None):
    """Adds a Minecraft Full Access account (mail:pass) to the stock file. Deletes cmd instantly."""
    try:
        await ctx.message.delete()
    except:
        pass

    if not category or category.lower() != "mcfa" or not account_details:
        await ctx.send("❌ **Error:** Incorrect format! Use: `.add mcfa mail:pass`", delete_after=5)
        return

    if ":" not in account_details:
        await ctx.send("❌ **Format Error:** Account details must be strictly in `mail:pass` format.", delete_after=5)
        return

    # Add the account line safely to the file
    with open(STOCK_FILE, "a") as f:
        f.write(account_details.strip() + "\n")
    
    await ctx.send("📥 **Success:** MCFA account stored safely. Command cleared for privacy!", delete_after=5)
    
    # Send to logs channel
    log_channel = discord.utils.get(ctx.guild.text_channels, name="logs")
    if log_channel:
        await log_channel.send(f"🛠️ **Stock Update:** `{ctx.author.name}` added 1 item to MCFA stock.")

@bot.command()
async def stock(ctx):
    """Displays the exact number of accounts available. Deletes cmd instantly."""
    try:
        await ctx.message.delete()
    except:
        pass

    with open(STOCK_FILE, "r") as f:
        lines = f.readlines()
    
    count = len([line for line in lines if line.strip()])
    
    embed = discord.Embed(title="📦 CURRENT SERVER STOCK", color=discord.Color.blue())
    embed.add_field(name="🔹 MCFA Accounts (mail:pass)", value=f"`{count}` available items", inline=False)
    embed.set_footer(text="Use .gen mcfa to claim yours!")
    await ctx.send(embed=embed, delete_after=15) # Embed deletes after 15 seconds to keep chat clean

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user) # 1-minute cooldown to stop spamming
async def gen(ctx, type: str = None):
    """DMs a single stock line to the user. DOES NOT delete the command message."""
    if not type or type.lower() != "mcfa":
        await ctx.send("❌ **Error:** Please type `.gen mcfa` explicitly.")
        ctx.command.reset_cooldown(ctx)
        return

    with open(STOCK_FILE, "r") as f:
        lines = f.readlines()

    # Clean empty lines
    lines = [line.strip() for line in lines if line.strip()]

    if not lines:
        await ctx.send("😭 **Out of Stock!** Please wait for an Admin to restock `.add mcfa`.")
        ctx.command.reset_cooldown(ctx)
        return

    # Take the top item out of stock
    claimed_account = lines[0]
    remaining_stock = lines[1:]

    # Write remaining stock back to the file
    with open(STOCK_FILE, "w") as f:
        for line in remaining_stock:
            f.write(line + "\n")

    # Attempt to DM the user
    try:
        embed = discord.Embed(title="🔑 YOUR MCFA ACCOUNT", description=f"```\n{claimed_account}\n```", color=discord.Color.gold())
        embed.set_footer(text="Format is mail:pass. Keep this confidential!")
        await ctx.author.send(embed=embed)
        await ctx.send(f"📬 {ctx.author.mention}, **Check your DMs!** Your MCFA item has been sent safely.")
        
        # Log Claim
        log_channel = discord.utils.get(ctx.guild.text_channels, name="logs")
        if log_channel:
            await log_channel.send(f"🎁 **Stock Claimed:** `{ctx.author.name}` generated 1x MCFA account.")
            
    except discord.Forbidden:
        # If user DMs are closed, return the item to stock list
        with open(STOCK_FILE, "a") as f:
            f.write(claimed_account + "\n")
        await ctx.send(f"❌ {ctx.author.mention}, **Error:** I cannot DM you. Please turn on **'Allow Direct Messages from server members'** in privacy settings and try again.")
        ctx.command.reset_cooldown(ctx)

# Error handling for cooldowns
@gen.error
async def gen_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ **Cooldown Active:** Please wait `{error.retry_after:.1f}` seconds before generating again.", delete_after=5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. MODERATION & PURGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """Deletes bulk messages instantly. Clears cmd line text too."""
    if amount < 1:
        return await ctx.send("Specify a valid number above 0.")
    
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared `{len(deleted)-1}` messages cleanly.", delete_after=4)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason specified"):
    """Kicks a member from the guild"""
    try:
        await ctx.message.delete()
    except:
        pass
    await member.kick(reason=reason)
    await ctx.send(f"🔨 **{member.name}** was kicked successfully.", delete_after=5)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason specified"):
    """Bans a member from the guild"""
    try:
        await ctx.message.delete()
    except:
        pass
    await member.ban(reason=reason)
    await ctx.send(f"🔴 **{member.name}** has been banned permanently.", delete_after=5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. TICKET SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Open Claim Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"⚠️ You already have an open ticket running: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_chan = await guild.create_text_channel(name=f"ticket-{user.name}", overwrites=overwrites)
        
        view = CloseTicketView()
        embed = discord.Embed(title="🎟️ Ticket Created", description=f"Welcome {user.mention},\nStaff will arrive shortly. Click below to close the room when finished.", color=discord.Color.blurple())
        await ticket_chan.send(embed=embed, view=view)
        
        await interaction.response.send_message(f"✅ Ticket created successfully! Go to: {ticket_chan.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 *Closing room in 5 seconds...*")
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    """Sends the persistent landing panel button into your support channel"""
    try:
        await ctx.message.delete()
    except:
        pass
    embed = discord.Embed(title="🎟️ SERVER SUPPORT & CLAIMS", description="Need help or claiming invite/level milestone rewards?\nClick the button below to start a private discussion channel with staff.", color=discord.Color.dark_grey())
    await ctx.send(embed=embed, view=TicketButtons())

# MoonGenBot Secret Authentication Token
import os
bot.run(os.getenv("DISCORD_TOKEN"))

