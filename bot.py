import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

COGS = ["cogs.moderation", "cogs.anti_spam", "cogs.anti_swear", "cogs.logging", "cogs.help"]

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    print(f"🔗 Connected to {len(bot.guilds)} server(s)")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="!help | Management Bot")
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ شما دسترسی لازم برای این دستور را ندارید.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ کاربر پیدا نشد.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ آرگومان مورد نیاز وارد نشده. از `!help {ctx.command}` کمک بگیرید.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ خطا: {str(error)}")

async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"✅ Loaded: {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("❌ DISCORD_TOKEN not found in .env file!")
            return
        await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
