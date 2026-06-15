import discord
from discord.ext import commands
import json
import os
import time
from collections import defaultdict

SETTINGS_FILE = "data/anti_spam.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(data):
    os.makedirs("data", exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = load_settings()
        # {guild_id: {user_id: [timestamps]}}
        self.message_cache = defaultdict(lambda: defaultdict(list))

    def get_guild_settings(self, guild_id: int):
        gid = str(guild_id)
        if gid not in self.settings:
            self.settings[gid] = {
                "enabled": False,
                "max_messages": 5,     # max پیام
                "time_window": 5,      # در X ثانیه
                "action": "mute",      # delete | mute | kick | ban
                "mute_duration": 5,    # دقیقه
                "log_channel": None
            }
            save_settings(self.settings)
        return self.settings[gid]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        s = self.get_guild_settings(message.guild.id)
        if not s["enabled"]:
            return

        if message.author.guild_permissions.manage_messages:
            return

        gid = message.guild.id
        uid = message.author.id
        now = time.time()

        # پاک کردن timestamps قدیمی
        window = s["time_window"]
        self.message_cache[gid][uid] = [
            t for t in self.message_cache[gid][uid] if now - t < window
        ]
        self.message_cache[gid][uid].append(now)

        if len(self.message_cache[gid][uid]) >= s["max_messages"]:
            self.message_cache[gid][uid] = []
            await self.handle_spam(message, s)

    async def handle_spam(self, message: discord.Message, s: dict):
        member = message.author
        channel = message.channel
        action = s.get("action", "mute")

        # حذف پیام‌های اخیر
        try:
            await channel.purge(limit=s["max_messages"] + 2, check=lambda m: m.author == member)
        except:
            pass

        warning = None
        if action == "mute":
            from datetime import timedelta
            until = discord.utils.utcnow() + timedelta(minutes=s.get("mute_duration", 5))
            try:
                await member.timeout(until, reason="اسپم")
                warning = await channel.send(
                    f"🔇 {member.mention} به خاطر اسپم برای **{s['mute_duration']}** دقیقه سکوت شد.",
                    delete_after=10
                )
            except:
                pass
        elif action == "kick":
            try:
                await member.kick(reason="اسپم")
                warning = await channel.send(f"👢 {member.mention} به خاطر اسپم اخراج شد.", delete_after=10)
            except:
                pass
        elif action == "ban":
            try:
                await member.ban(reason="اسپم", delete_message_days=0)
                warning = await channel.send(f"🔨 {member.mention} به خاطر اسپم بن شد.", delete_after=10)
            except:
                pass
        else:
            warning = await channel.send(
                f"⚠️ {member.mention} لطفاً اسپم نکنید!", delete_after=8
            )

        # Log
        log_ch_id = s.get("log_channel")
        if log_ch_id:
            guild = message.guild
            log_ch = guild.get_channel(int(log_ch_id))
            if log_ch:
                embed = discord.Embed(title="🚨 Anti-Spam Triggered", color=0xff4444)
                embed.add_field(name="کاربر", value=f"{member} ({member.id})")
                embed.add_field(name="کانال", value=channel.mention)
                embed.add_field(name="اقدام", value=action)
                await log_ch.send(embed=embed)

    # ─── Commands ─────────────────────────────────────────────────────

    @commands.group(name="antispam", aliases=["ضداسپم"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def antispam(self, ctx):
        """مدیریت سیستم ضد اسپم | !antispam"""
        s = self.get_guild_settings(ctx.guild.id)
        status = "✅ فعال" if s["enabled"] else "❌ غیرفعال"
        embed = discord.Embed(title="🚨 سیستم ضد اسپم", color=0xff4444)
        embed.add_field(name="وضعیت", value=status)
        embed.add_field(name="حد پیام", value=f"{s['max_messages']} پیام در {s['time_window']} ثانیه")
        embed.add_field(name="اقدام", value=s["action"])
        if s["action"] == "mute":
            embed.add_field(name="مدت سکوت", value=f"{s['mute_duration']} دقیقه")
        embed.add_field(name="دستورات", value="`!antispam on/off` | `!antispam set <max> <seconds>` | `!antispam action <delete|mute|kick|ban>` | `!antispam log #ch`", inline=False)
        await ctx.send(embed=embed)

    @antispam.command(name="on")
    @commands.has_permissions(manage_guild=True)
    async def antispam_on(self, ctx):
        s = self.get_guild_settings(ctx.guild.id)
        s["enabled"] = True
        save_settings(self.settings)
        await ctx.send("✅ سیستم ضد اسپم **فعال** شد.")

    @antispam.command(name="off")
    @commands.has_permissions(manage_guild=True)
    async def antispam_off(self, ctx):
        s = self.get_guild_settings(ctx.guild.id)
        s["enabled"] = False
        save_settings(self.settings)
        await ctx.send("❌ سیستم ضد اسپم **غیرفعال** شد.")

    @antispam.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def antispam_set(self, ctx, max_messages: int, time_window: int):
        """تنظیم حد | !antispam set <تعداد پیام> <بازه ثانیه>"""
        s = self.get_guild_settings(ctx.guild.id)
        s["max_messages"] = max(2, min(max_messages, 30))
        s["time_window"] = max(1, min(time_window, 60))
        save_settings(self.settings)
        await ctx.send(f"✅ حد اسپم: **{s['max_messages']}** پیام در **{s['time_window']}** ثانیه.")

    @antispam.command(name="action")
    @commands.has_permissions(manage_guild=True)
    async def antispam_action(self, ctx, action: str):
        """تنظیم اقدام | !antispam action <delete|mute|kick|ban>"""
        valid = ["delete", "mute", "kick", "ban"]
        if action not in valid:
            return await ctx.send(f"❌ اقدام معتبر: {', '.join(valid)}")
        s = self.get_guild_settings(ctx.guild.id)
        s["action"] = action
        save_settings(self.settings)
        await ctx.send(f"✅ اقدام ضد اسپم به **{action}** تغییر کرد.")

    @antispam.command(name="log")
    @commands.has_permissions(manage_guild=True)
    async def antispam_log(self, ctx, channel: discord.TextChannel):
        s = self.get_guild_settings(ctx.guild.id)
        s["log_channel"] = str(channel.id)
        save_settings(self.settings)
        await ctx.send(f"✅ کانال لاگ به {channel.mention} تنظیم شد.")

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
