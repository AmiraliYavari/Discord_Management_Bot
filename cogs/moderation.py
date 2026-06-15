import discord
from discord.ext import commands
import asyncio
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─── Clear Messages ───────────────────────────────────────────────
    @commands.command(name="clear", aliases=["purge", "پاک"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        """پاک کردن پیام‌ها | !clear [تعداد]"""
        if amount < 1 or amount > 500:
            return await ctx.send("❌ تعداد باید بین ۱ تا ۵۰۰ باشد.")
        await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"✅ **{amount}** پیام پاک شد.")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(name="clearuser", aliases=["purgeuser"])
    @commands.has_permissions(manage_messages=True)
    async def clear_user(self, ctx, member: discord.Member, amount: int = 20):
        """پاک کردن پیام‌های یک کاربر | !clearuser @کاربر [تعداد]"""
        def check(m):
            return m.author == member
        deleted = await ctx.channel.purge(limit=200, check=check, bulk=True)
        msg = await ctx.send(f"✅ **{len(deleted)}** پیام از {member.mention} پاک شد.")
        await asyncio.sleep(3)
        await msg.delete()

    # ─── Kick ─────────────────────────────────────────────────────────
    @commands.command(name="kick", aliases=["اخراج"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "دلیلی ذکر نشده"):
        """اخراج کاربر | !kick @کاربر [دلیل]"""
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ شما نمی‌توانید این کاربر را اخراج کنید.")
        try:
            await member.send(f"⚠️ شما از سرور **{ctx.guild.name}** اخراج شدید.\n**دلیل:** {reason}")
        except:
            pass
        await member.kick(reason=reason)
        embed = discord.Embed(title="👢 کاربر اخراج شد", color=0xff9900)
        embed.add_field(name="کاربر", value=member.mention)
        embed.add_field(name="توسط", value=ctx.author.mention)
        embed.add_field(name="دلیل", value=reason, inline=False)
        await ctx.send(embed=embed)

    # ─── Ban ──────────────────────────────────────────────────────────
    @commands.command(name="ban", aliases=["بن"])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "دلیلی ذکر نشده"):
        """بن کردن کاربر | !ban @کاربر [دلیل]"""
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ شما نمی‌توانید این کاربر را بن کنید.")
        try:
            await member.send(f"🚫 شما از سرور **{ctx.guild.name}** بن شدید.\n**دلیل:** {reason}")
        except:
            pass
        await member.ban(reason=reason, delete_message_days=0)
        embed = discord.Embed(title="🔨 کاربر بن شد", color=0xff0000)
        embed.add_field(name="کاربر", value=str(member))
        embed.add_field(name="توسط", value=ctx.author.mention)
        embed.add_field(name="دلیل", value=reason, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="unban", aliases=["آنبن"])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user_str: str):
        """لغو بن | !unban user#0000"""
        banned = [entry async for entry in ctx.guild.bans()]
        for entry in banned:
            if str(entry.user) == user_str or str(entry.user.id) == user_str:
                await ctx.guild.unban(entry.user)
                return await ctx.send(f"✅ بن **{entry.user}** برداشته شد.")
        await ctx.send("❌ کاربر بنی با این مشخصات پیدا نشد.")

    # ─── Mute / Timeout ───────────────────────────────────────────────
    @commands.command(name="mute", aliases=["سکوت"])
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 10, *, reason: str = "دلیلی ذکر نشده"):
        """سکوت کردن کاربر | !mute @کاربر [دقیقه] [دلیل]"""
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ شما نمی‌توانید این کاربر را سکوت کنید.")
        until = discord.utils.utcnow() + timedelta(minutes=duration)
        await member.timeout(until, reason=reason)
        embed = discord.Embed(title="🔇 کاربر سکوت شد", color=0xffa500)
        embed.add_field(name="کاربر", value=member.mention)
        embed.add_field(name="مدت", value=f"{duration} دقیقه")
        embed.add_field(name="دلیل", value=reason, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="unmute", aliases=["آنمیوت"])
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """لغو سکوت | !unmute @کاربر"""
        await member.timeout(None)
        await ctx.send(f"✅ سکوت {member.mention} برداشته شد.")

    # ─── Warn ─────────────────────────────────────────────────────────
    @commands.command(name="warn", aliases=["اخطار"])
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "دلیلی ذکر نشده"):
        """اخطار دادن به کاربر | !warn @کاربر [دلیل]"""
        try:
            await member.send(f"⚠️ شما در سرور **{ctx.guild.name}** اخطار گرفتید.\n**دلیل:** {reason}")
        except:
            pass
        embed = discord.Embed(title="⚠️ اخطار صادر شد", color=0xffff00)
        embed.add_field(name="کاربر", value=member.mention)
        embed.add_field(name="توسط", value=ctx.author.mention)
        embed.add_field(name="دلیل", value=reason, inline=False)
        await ctx.send(embed=embed)

    # ─── Slowmode ─────────────────────────────────────────────────────
    @commands.command(name="slowmode", aliases=["کندحالت"])
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """تنظیم slowmode | !slowmode [ثانیه]"""
        if seconds < 0 or seconds > 21600:
            return await ctx.send("❌ مقدار باید بین ۰ تا ۲۱۶۰۰ ثانیه باشد.")
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.send("✅ Slowmode غیرفعال شد.")
        else:
            await ctx.send(f"✅ Slowmode روی **{seconds}** ثانیه تنظیم شد.")

    # ─── Lock / Unlock Channel ────────────────────────────────────────
    @commands.command(name="lock", aliases=["قفل"])
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        """قفل کردن کانال | !lock"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔒 کانال قفل شد.")

    @commands.command(name="unlock", aliases=["بازکردن"])
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        """باز کردن قفل کانال | !unlock"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔓 قفل کانال برداشته شد.")

    # ─── Server Info ──────────────────────────────────────────────────
    @commands.command(name="serverinfo", aliases=["سرور"])
    async def serverinfo(self, ctx):
        """اطلاعات سرور"""
        g = ctx.guild
        embed = discord.Embed(title=f"📊 {g.name}", color=0x5865F2)
        embed.set_thumbnail(url=g.icon.url if g.icon else None)
        embed.add_field(name="👑 Owner", value=g.owner.mention)
        embed.add_field(name="👥 Members", value=g.member_count)
        embed.add_field(name="💬 Channels", value=len(g.channels))
        embed.add_field(name="🎭 Roles", value=len(g.roles))
        embed.add_field(name="📅 Created", value=g.created_at.strftime("%Y-%m-%d"))
        await ctx.send(embed=embed)

    @commands.command(name="userinfo", aliases=["کاربر"])
    async def userinfo(self, ctx, member: discord.Member = None):
        """اطلاعات کاربر"""
        member = member or ctx.author
        embed = discord.Embed(title=f"👤 {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🆔 ID", value=member.id)
        embed.add_field(name="📅 Joined Server", value=member.joined_at.strftime("%Y-%m-%d"))
        embed.add_field(name="📅 Account Created", value=member.created_at.strftime("%Y-%m-%d"))
        embed.add_field(name="🎭 Top Role", value=member.top_role.mention)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
