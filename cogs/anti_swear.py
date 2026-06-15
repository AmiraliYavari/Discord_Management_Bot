import discord
from discord.ext import commands
import json
import os

SETTINGS_FILE = "data/anti_swear.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(data):
    os.makedirs("data", exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# کلمات پیش‌فرض فیلتر (فارسی + انگلیسی)
DEFAULT_WORDS = [
    "کصکش", "کیر", "کس", "جنده", "مادرجنده", "گاییدم",
    "fuck", "shit", "bitch", "asshole", "damn", "crap", "bastard"
]

class AntiSwear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = load_settings()

    def get_guild_settings(self, guild_id: int):
        gid = str(guild_id)
        if gid not in self.settings:
            self.settings[gid] = {
                "enabled": False,
                "words": DEFAULT_WORDS.copy(),
                "log_channel": None,
                "action": "delete",  # delete | warn | mute
                "warn_on_delete": True
            }
            save_settings(self.settings)
        return self.settings[gid]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return

        s = self.get_guild_settings(message.guild.id)
        if not s["enabled"]:
            return

        # ادمین ها رو چک نکن
        if message.author.guild_permissions.manage_messages:
            return

        content_lower = message.content.lower()
        triggered_word = None
        for word in s["words"]:
            if word.lower() in content_lower:
                triggered_word = word
                break

        if not triggered_word:
            return

        await message.delete()

        if s["warn_on_delete"]:
            try:
                warning = await message.channel.send(
                    f"⚠️ {message.author.mention} پیام شما حذف شد چون شامل کلمات ممنوعه بود.",
                    delete_after=5
                )
            except:
                pass

        # Log
        log_ch_id = s.get("log_channel")
        if log_ch_id:
            log_ch = message.guild.get_channel(int(log_ch_id))
            if log_ch:
                embed = discord.Embed(title="🚫 Anti-Swear Filter", color=0xff0000)
                embed.add_field(name="کاربر", value=f"{message.author} ({message.author.id})")
                embed.add_field(name="کانال", value=message.channel.mention)
                embed.add_field(name="کلمه فیلتر شده", value=f"||{triggered_word}||", inline=False)
                embed.add_field(name="متن پیام", value=f"||{message.content[:200]}||", inline=False)
                await log_ch.send(embed=embed)

    # ─── Commands ─────────────────────────────────────────────────────

    @commands.group(name="swear", aliases=["فحش"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def swear(self, ctx):
        """مدیریت سیستم ضد فحش | !swear"""
        s = self.get_guild_settings(ctx.guild.id)
        status = "✅ فعال" if s["enabled"] else "❌ غیرفعال"
        embed = discord.Embed(title="🚫 سیستم ضد فحش", color=0xff6600)
        embed.add_field(name="وضعیت", value=status)
        embed.add_field(name="تعداد کلمات فیلتر", value=len(s["words"]))
        embed.add_field(name="اخطار هنگام حذف", value="✅" if s["warn_on_delete"] else "❌")
        embed.add_field(name="کانال لاگ", value=f"<#{s['log_channel']}>" if s["log_channel"] else "تنظیم نشده", inline=False)
        embed.add_field(name="دستورات", value="`!swear on/off` | `!swear add <کلمه>` | `!swear remove <کلمه>` | `!swear list` | `!swear log #کانال`", inline=False)
        await ctx.send(embed=embed)

    @swear.command(name="on")
    @commands.has_permissions(manage_guild=True)
    async def swear_on(self, ctx):
        s = self.get_guild_settings(ctx.guild.id)
        s["enabled"] = True
        save_settings(self.settings)
        await ctx.send("✅ سیستم ضد فحش **فعال** شد.")

    @swear.command(name="off")
    @commands.has_permissions(manage_guild=True)
    async def swear_off(self, ctx):
        s = self.get_guild_settings(ctx.guild.id)
        s["enabled"] = False
        save_settings(self.settings)
        await ctx.send("❌ سیستم ضد فحش **غیرفعال** شد.")

    @swear.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def swear_add(self, ctx, *, word: str):
        """اضافه کردن کلمه به لیست فیلتر | !swear add <کلمه>"""
        s = self.get_guild_settings(ctx.guild.id)
        if word.lower() in [w.lower() for w in s["words"]]:
            return await ctx.send("⚠️ این کلمه قبلاً در لیست است.")
        s["words"].append(word)
        save_settings(self.settings)
        await ctx.send(f"✅ کلمه `||{word}||` به لیست فیلتر اضافه شد.")

    @swear.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def swear_remove(self, ctx, *, word: str):
        """حذف کلمه از لیست فیلتر | !swear remove <کلمه>"""
        s = self.get_guild_settings(ctx.guild.id)
        words_lower = [w.lower() for w in s["words"]]
        if word.lower() not in words_lower:
            return await ctx.send("❌ این کلمه در لیست نیست.")
        idx = words_lower.index(word.lower())
        s["words"].pop(idx)
        save_settings(self.settings)
        await ctx.send(f"✅ کلمه از لیست حذف شد.")

    @swear.command(name="list")
    @commands.has_permissions(manage_guild=True)
    async def swear_list(self, ctx):
        """لیست کلمات فیلتر شده"""
        s = self.get_guild_settings(ctx.guild.id)
        if not s["words"]:
            return await ctx.send("📋 لیست فیلتر خالی است.")
        words_text = ", ".join([f"||{w}||" for w in s["words"]])
        embed = discord.Embed(title="📋 کلمات فیلتر شده", description=words_text, color=0xff6600)
        await ctx.send(embed=embed)

    @swear.command(name="log")
    @commands.has_permissions(manage_guild=True)
    async def swear_log(self, ctx, channel: discord.TextChannel):
        """تنظیم کانال لاگ | !swear log #کانال"""
        s = self.get_guild_settings(ctx.guild.id)
        s["log_channel"] = str(channel.id)
        save_settings(self.settings)
        await ctx.send(f"✅ کانال لاگ به {channel.mention} تنظیم شد.")

    @swear.command(name="warn")
    @commands.has_permissions(manage_guild=True)
    async def swear_warn_toggle(self, ctx):
        """تغییر وضعیت اخطار هنگام حذف"""
        s = self.get_guild_settings(ctx.guild.id)
        s["warn_on_delete"] = not s["warn_on_delete"]
        save_settings(self.settings)
        status = "فعال" if s["warn_on_delete"] else "غیرفعال"
        await ctx.send(f"✅ اخطار هنگام حذف **{status}** شد.")

async def setup(bot):
    await bot.add_cog(AntiSwear(bot))
