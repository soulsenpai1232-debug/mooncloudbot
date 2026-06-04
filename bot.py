import discord
from discord.ext import commands
import os
import asyncio
import random

# Core Privileged Gateways Setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

# Global Variables & Prefix Configuration
bot = commands.Bot(command_prefix=".", intents=intents)

# Core Repository Manifest
STOCKS = {
    "mcfa": "mcfa_stock.txt",
    "roblox": "roblox_stock.txt"
}

# Establish Local Database Repositories
for db_file in STOCKS.values():
    if not os.path.exists(db_file):
        with open(db_file, "w", encoding="utf-8") as file:
            pass

@bot.event
async def on_ready():
    """Triggers instantly when connection establishes successfully."""
    await bot.change_presence(activity=discord.Game(name="Minecraft & Roblox | .stock"))
    print(f"Logged in securely as {bot.user}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. VISITOR AUTOMATION & ACTIVITY LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.event
async def on_member_join(member):
    """Instantly roles incoming traffic and records join metrics."""
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        try:
            await member.add_roles(role)
        except Exception as error:
            print(f"Unable to assign Member role: {error}")
            
    log_chan = discord.utils.get(member.guild.text_channels, name="logs")
    if log_chan:
        embed = discord.Embed(
            title="Member Joined", 
            description=f"{member.mention} entered the server.", 
            color=discord.Color.green()
        )
        await log_chan.send(embed=embed)

@bot.event
async def on_member_remove(member):
    """Triggers logs whenever a user leaves."""
    log_chan = discord.utils.get(member.guild.text_channels, name="logs")
    if log_chan:
        embed = discord.Embed(
            title="Member Left", 
            description=f"**{member.name}** left the server.", 
            color=discord.Color.red()
        )
        await log_chan.send(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. ADVANCED STOCK GENERATION INFRASTRUCTURE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(administrator=True)
async def addservice(ctx, name: str = None):
    """Dynamically adds a brand new service type and creates its text stock file."""
    try:
        await ctx.message.delete()
    except:
        pass

    if not name:
        await ctx.send("Error: Provide a name. Usage: .addservice [name]", delete_after=5)
        return

    category = name.lower()
    if category in STOCKS:
        await ctx.send(f"Error: Service '{category}' already exists.", delete_after=5)
        return

    file_name = f"{category}_stock.txt"
    STOCKS[category] = file_name

    if not os.path.exists(file_name):
        with open(file_name, "w", encoding="utf-8") as file:
            pass

    await ctx.send(f"Success: Added new service channel '{category.upper()}'. File linked successfully.", delete_after=5)

    log_chan = discord.utils.get(ctx.guild.text_channels, name="logs")
    if log_chan:
        await log_chan.send(f"Structure Update: {ctx.author.name} dynamically added a new service type: {category.upper()}")

@bot.command()
@commands.has_permissions(administrator=True)
async def add(ctx, category: str = None, *, details: str = None):
    """Securely uploads raw stock to text storage. Purges command context immediately."""
    try:
        await ctx.message.delete()
    except:
        pass

    if not category or category.lower() not in STOCKS or not details:
        valid_cats = "/".join(STOCKS.keys())
        await ctx.send(f"Error: Use format: .add [{valid_cats}] mail:pass", delete_after=5)
        return

    if ":" not in details:
        await ctx.send("Format Error: Account details must be strictly in mail:pass format.", delete_after=5)
        return

    target = STOCKS[category.lower()]
    
    with open(target, "a", encoding="utf-8") as file:
        file.write(details.strip() + "\n")
    
    await ctx.send(f"Success: Stored package within {category.upper()} database layer.", delete_after=5)
    
    log_chan = discord.utils.get(ctx.guild.text_channels, name="logs")
    if log_chan:
        await log_chan.send(f"Stock Update: {ctx.author.name} added 1x item to {category.upper()} stock.")

@bot.command()
async def stock(ctx):
    """Displays localized visual stock array matrix."""
    try:
        await ctx.message.delete()
    except:
        pass

    embed = discord.Embed(title="CURRENT SERVER STOCK", color=discord.Color.blue())
    
    for category, file_name in STOCKS.items():
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                metrics = len([line for line in file.readlines() if line.strip()])
        except FileNotFoundError:
            metrics = 0
        embed.add_field(name=f"{category.upper()} Accounts", value=f"`{metrics}` units active", inline=False)
        
    valid_gens = " or .gen ".join(STOCKS.keys())
    embed.set_footer(text=f"Execute .gen {valid_gens} to claim your item.")
    await ctx.send(embed=embed, delete_after=15)

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def gen(ctx, category: str = None):
    """Extracts a singular index entry from DB and routes via direct transmission pipeline."""
    if not category or category.lower() not in STOCKS:
        valid_gens = " or .gen ".join(STOCKS.keys())
        await ctx.send(f"Error: Please declare target: .gen {valid_gens}")
        ctx.command.reset_cooldown(ctx)
        return

    target = STOCKS[category.lower()]

    with open(target, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]

    if not lines:
        await ctx.send(f"Out of Stock: Critical empty state on {category.lower()}. Please wait for restock.")
        ctx.command.reset_cooldown(ctx)
        return

    extracted_payload = lines[0]
    residual_payload = lines[1:]

    with open(target, "w", encoding="utf-8") as file:
        for remaining in residual_payload:
            file.write(remaining + "\n")

    try:
        embed = discord.Embed(title=f"YOUR {category.upper()} ACCOUNT", description=f"```\n{extracted_payload}\n```", color=discord.Color.gold())
        embed.set_footer(text="Format is mail:pass. Keep this details private!")
        await ctx.author.send(embed=embed)
        await ctx.send(f"Check your DMs {ctx.author.mention} for your account!")
        
        log_chan = discord.utils.get(ctx.guild.text_channels, name="logs")
        if log_chan:
            await log_chan.send(f"Stock Claimed: {ctx.author.name} generated 1x unit of {category.upper()} inventory.")
            
    except discord.Forbidden:
        with open(target, "a", encoding="utf-8") as file:
            file.write(extracted_payload + "\n")
        await ctx.send(f"Error: I cannot DM you {ctx.author.mention}. Please open your DMs and try again.", delete_after=5)
        ctx.command.reset_cooldown(ctx)

@gen.error
async def gen_cooldown_handler(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Cooldown Active: Please wait `{error.retry_after:.1f}` seconds.", delete_after=5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. SERVER SECURITY & ACCESS CONTROL (.lock / .unlock)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    """Locks down text channel traffic permissions for the default @everyone tier."""
    try:
        await ctx.message.delete()
    except:
        pass

    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    if overwrite.send_messages is False:
        await ctx.send("This channel channel status is already flagged as locked.", delete_after=5)
        return

    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("Channel lockdown sequence engaged. Text transmission privileges revoked.")

    log_chan = discord.utils.get(ctx.guild.text_channels, name="logs")
    if log_chan:
        await log_chan.send(f"Security Alert: Channel {ctx.channel.mention} was locked by {ctx.author.name}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    """Restores standard message submission capabilities across text channels."""
    try:
        await ctx.message.delete()
    except:
        pass

    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    if overwrite.send_messages is True or overwrite.send_messages is None:
        await ctx.send("This channel interface is already fully open.", delete_after=5)
        return

    overwrite.send_messages = None
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("Channel lockdown lifted. Text transmission privileges successfully restored.")

    log_chan = discord.utils.get(ctx.guild.text_channels, name="logs")
    if log_chan:
        await log_chan.send(f"Security Alert: Channel {ctx.channel.mention} was unlocked by {ctx.author.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. CUSTOM ASSET HANDLING PIPELINES (.addemoji / .addmanyemojis)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(manage_expressions=True)
async def addemoji(ctx, emoji: discord.PartialEmoji = None, name: str = None):
    """Fetches an asset via its identifier layout and loads it to local assets."""
    try:
        await ctx.message.delete()
    except:
        pass

    if not emoji:
        await ctx.send("Error: Provide an emoji. Usage: .addemoji [emoji] [optional_custom_name]", delete_after=5)
        return

    emoji_name = name if name else emoji.name
    try:
        for emoji in emojis:
            try:
                emoji_bytes = await emoji.read()
                await ctx.guild.create_custom_emoji(name=emoji.name, image=emoji_bytes)
                success_count += 1
            except:
                fail_count += 1
            await asyncio.sleep(1) # Safety delay to prevent Discord rate limits

        await status_msg.edit(content=f"Batch Update: Finished asset array. Loaded: `{success_count}`. Failed/Skipped: `{fail_count}`.", delete_after=10)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. INTERACTIVE GIVEAWAY CORE ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx, duration: str = None, *, item_prize: str = None):
    """Deploys real-time event sweeps based on system countdown metrics."""
    try:
        await ctx.message.delete()
    except:
        pass

    if not duration or not item_prize:
        return await ctx.send("Syntax Error: Use format: .giveaway [10s/5m/2h] [prize]", delete_after=5)

    suffix_identifier = duration[-1].lower()
    try:
        parsed_quantum = int(duration[:-1])
    except ValueError:
        return await ctx.send("Error: Invalid time format. Use numbers followed by s, m, or h.", delete_after=5)

    converted_ticks = parsed_quantum if suffix_identifier == 's' else parsed_quantum * 60 if suffix_identifier == 'm' else parsed_quantum * 3600 if suffix_identifier == 'h' else 0
    if converted_ticks <= 0:
        return await ctx.send("Error: Runtime duration cannot stay at or below zero.", delete_after=5)

    event_embed = discord.Embed(title="GIVEAWAY STARTED", description=f"Prize: **{item_prize}**\nDuration: **{duration}**\n\nReact below to join!", color=discord.Color.purple())
    
    live_msg = await ctx.send(embed=event_embed)
    await live_msg.add_reaction("🎉")

    await asyncio.sleep(converted_ticks)

    live_msg = await ctx.channel.fetch_message(live_msg.id)
    target_reaction = discord.utils.get(live_msg.reactions, emoji="🎉")
    target_pool = [identity async for identity in target_reaction.users() if not identity.bot]

    if not target_pool:
        await ctx.send(f"No one entered the giveaway. **{item_prize}** has no winner!")
        return

    selected_winner = random.choice(target_pool)
    victory_embed = discord.Embed(title="GIVEAWAY WINNER", description=f"Winner: {selected_winner.mention}\nPrize: **{item_prize}**", color=discord.Color.gold())
    await ctx.send(embed=victory_embed)
    await ctx.send(f"Congratulations {selected_winner.mention}! Open a ticket channel to claim your prize.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. FAST FLUSH PURGE & SEVER ENFORCEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit_range: int):
    """Wipes raw message matrices from text targets completely."""
    if limit_range < 1:
        return await ctx.send("Specify a valid number over zero.")
    flushed_count = await ctx.channel.purge(limit=limit_range + 1)
    await ctx.send(f"Cleared `{len(flushed_count)-1}` messages cleanly.", delete_after=4)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, target_user: discord.Member, *, reason_str="No reason specified"):
    try:
        await ctx.message.delete()
    except:
        pass
    await target_user.kick(reason=reason_str)
    await ctx.send(f"{target_user.name} was kicked successfully.", delete_after=5)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, target_user: discord.Member, *, reason_str="No reason specified"):
    try:
        await ctx.message.delete()
    except:
        pass
    await target_user.ban(reason=reason_str)
    await ctx.send(f"{target_user.name} has been banned permanently.", delete_after=5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. PRIVATE TICKET THREAD SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Claim Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        thread_id = f"ticket-{user.name.lower()}"
        
        running_thread = discord.utils.get(guild.text_channels, name=thread_id)
        if running_thread:
            await interaction.response.send_message(f"Error: You already have a ticket open at: {running_thread.mention}", ephemeral=True)
            return

        matrix_overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        allocated_chan = await guild.create_text_channel(name=thread_id, overwrites=matrix_overwrites)
        control_deck = CloseTicketView()
        onboarding_embed = discord.Embed(title="PRIVATE SUPPORT TERMINAL", description=f"Welcome {user.mention},\nStaff will arrive shortly. Click the button below to close this ticket channel when finished.", color=discord.Color.blurple())
        await allocated_chan.send(embed=onboarding_embed, view=control_deck)
        await interaction.response.send_message(f"Ticket generated cleanly! Go to: {allocated_chan.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing channel and deleting thread in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    """Deploys physical interaction visual decks to root rooms."""
    try:
        await ctx.message.delete()
    except:
        pass
    onboarding_deck = discord.Embed(title="CORE SUPPORT AND CLAIMS DESK", description="Looking to claim specific benchmark level rewards or process partnerships?\nClick the button down below to start a private hidden line with server staff.", color=discord.Color.dark_grey())
    await ctx.send(embed=onboarding_deck, view=TicketButtons())

# Secure bot deployment run authentication line via local Environment Variable configuration
import os
bot.run(os.getenv("DISCORD_TOKEN"))
