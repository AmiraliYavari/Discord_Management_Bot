import discord
from discord.ext import commands
import json
import os

SETTINGS_FILE = "data/logging.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(data):
    os.makedirs("data", exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = load_settings()

    def get_log_channel(self, guild: discord.Guild):
        gid = str(guild.id)
        if gid not in self.settings or not self.settings[gid].get("log_channel"):
            return None
        ch_id = self.settings[gid]["log_channel"]
        return guild.get_channel(int(ch_id))

    def is_event_enabled(self, guild_id: int, event: str) -> bool:
        gid = str(guild_id)
        if gid not in self.settings:
            return False
        events = self.settings[gid].get("events", {})
        return events.get(event, True)

    # ─── Events ───────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not self.is_event_enabled(member.guild.id, "join"):
            return
        ch = self.get_log_channel(member.guild)
        if not ch:
            return
        embed = discord.Embed(title="📥 کاربر وارد شد", color=0x00ff88)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="کاربر", value=f"{member} ({member.id})")
        embed.add_field(name="اکانت ساخته شده", value=member.created_at.strftime("%Y-%m-%d"))
        embed.set_footer(text=f"اعضا: {member.guild.member_count}")
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not self.is_event_enabled(member.guild.id, "leave"):
            return
        ch = self.get_log_channel(member.guild)
        if not ch:
            return
        embed = discord.Embed(title="📤 کاربر خارج شد", color=0xff4444)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="کاربر", value=f"{member} ({member.id})")
        embed.set_footer(text=f"اعضا: {member.guild.member_count}")
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if not self.is_event_enabled(message.guild.id, "delete"):
            return
        ch = self.get_log_channel(message.guild)
        if not ch:
            return
        embed = discord.Embed(title="🗑️ پیام حذف شد", color=0xff6600)
        embed.add_field(name="کاربر", value=f"{message.author.mention}")
        embed.add_field(name="کانال", value=message.channel.mention)
        if message.content:
            embed.add_field(name="پیام", value=message.content[:1000], inline=False)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild:
            return
        if before.content == after.content:
            return
        if not self.is_event_enabled(before.guild.id, "edit"):
            return
        ch = self.get_log_channel(before.guild)
        if not ch:
            return
        embed = discord.Embed(title="✏️ پیام ویرایش شد", color=0xffff00)
        embed.add_field(name="کاربر", value=before.author.mention)
        embed.add_field(name="کانال", value=before.channel.mention)
        embed.add_field(name="قبل", value=before.content[:500] or "خالی", inline=False)
        embed.add_field(name="بعد", value=after.content[:500] or "خالی", inline=False)
        embed.add_field(name="لینک", value=f"[برو به پیام]({after.jump_url})", inline=False)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not self.is_event_enabled(guild.id, "ban"):
            return
        ch = self.get_log_channel(guild)
        if not ch:
            return
        embed = discord.Embed(title="🔨 کاربر بن شد", color=0xff0000)
        embed.add_field(name="کاربر", value=f"{user} ({user.id})")
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        if not self.is_event_enabled(guild.id, "ban"):
            return
        ch = self.get_log_channel(guild)
        if not ch:
            return
        embed = discord.Embed(title="✅ بن کاربر برداشته شد", color=0x00ff00)
        embed.add_field(name="کاربر", value=f"{user} ({user.id})")
        await ch.send(embed=embed)

    # ─── Commands ─────────────────────────────────────────────────────

    @commands.group(name="log", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def log_cmd(self, ctx):
        """مدیریت سیستم لاگ | !log"""
        gid = str(ctx.guild.id)
        s = self.settings.get(gid, {})
        ch_id = s.get("log_channel")
        events = s.get("events", {})
        event_list = ["join", "leave", "delete", "edit", "ban"]
        embed = discord.Embed(title="📋 سیستم لاگ", color=0x5865F2)
        embed.add_field(name="کانال لاگ", value=f"<#{ch_id}>" if ch_id else "تنظیم نشده")
        status_text = "\n".join([f"{'✅' if events.get(e, True) else '❌'} {e}" for e in event_list])
        embed.add_field(name="رویدادها", value=status_text, inline=False)
        embed.add_field(name="دستورات", value="`!log set #کانال` | `!log toggle <event>`", inline=False)
        await ctx.send(embed=embed)

    @log_cmd.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def log_set(self, ctx, channel: discord.TextChannel):
        """تنظیم کانال لاگ | !log set #کانال"""
        gid = str(ctx.guild.id)
        if gid not in self.settings:
            self.settings[gid] = {}
        self.settings[gid]["log_channel"] = str(channel.id)
        save_settings(self.settings)
        await ctx.send(f"✅ کانال لاگ به {channel.mention} تنظیم شد.")

    @log_cmd.command(name="toggle")
    @commands.has_permissions(manage_guild=True)
    async def log_toggle(self, ctx, event: str):
        """فعال/غیرفعال کردن رویداد | !log toggle <join|leave|delete|edit|ban>"""
        valid = ["join", "leave", "delete", "edit", "ban"]
        if event not in valid:
            return await ctx.send(f"❌ رویداد معتبر: {', '.join(valid)}")
        gid = str(ctx.guild.id)
        if gid not in self.settings:
            self.settings[gid] = {}
        events = self.settings[gid].get("events", {})
        events[event] = not events.get(event, True)
        self.settings[gid]["events"] = events
        save_settings(self.settings)
        status = "فعال" if events[event] else "غیرفعال"
        await ctx.send(f"✅ رویداد **{event}** **{status}** شد.")

async def setup(bot):
    await bot.add_cog(Logging(bot))
