import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["راهنما", "h"])
    async def help_command(self, ctx, *, command_name: str = None):
        """راهنمای دستورات | !help [دستور]"""

        if command_name:
            cmd = self.bot.get_command(command_name)
            if not cmd:
                return await ctx.send(f"❌ دستور `{command_name}` پیدا نشد.")
            embed = discord.Embed(title=f"📖 {cmd.name}", color=0x5865F2)
            embed.add_field(name="توضیح", value=cmd.help or "بدون توضیح", inline=False)
            if cmd.aliases:
                embed.add_field(name="نام‌های دیگر", value=", ".join(cmd.aliases))
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="🤖 Management Bot — راهنما",
            description="پیشوند دستورات: `!`",
            color=0x5865F2
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(name="🔨 مدیریت پیام", value="""
`!clear [n]` — پاک کردن n پیام
`!clearuser @user [n]` — پاک کردن پیام‌های یک کاربر
`!slowmode [s]` — تنظیم slowmode (ثانیه)
`!lock` / `!unlock` — قفل/باز کردن کانال
""", inline=False)

        embed.add_field(name="👮 مجازات", value="""
`!warn @user [دلیل]` — اخطار
`!mute @user [دقیقه] [دلیل]` — سکوت
`!unmute @user` — لغو سکوت
`!kick @user [دلیل]` — اخراج
`!ban @user [دلیل]` — بن
`!unban user#0000` — لغو بن
""", inline=False)

        embed.add_field(name="🚫 ضد فحش", value="""
`!swear` — وضعیت
`!swear on/off` — فعال/غیرفعال
`!swear add <کلمه>` — افزودن
`!swear remove <کلمه>` — حذف
`!swear list` — لیست
`!swear log #ch` — کانال لاگ
""", inline=False)

        embed.add_field(name="🚨 ضد اسپم", value="""
`!antispam` — وضعیت
`!antispam on/off` — فعال/غیرفعال
`!antispam set <max> <seconds>` — تنظیم حد
`!antispam action <delete|mute|kick|ban>` — اقدام
`!antispam log #ch` — کانال لاگ
""", inline=False)

        embed.add_field(name="📋 لاگ", value="""
`!log` — وضعیت
`!log set #ch` — تنظیم کانال لاگ
`!log toggle <join|leave|delete|edit|ban>` — فعال/غیرفعال رویداد
""", inline=False)

        embed.add_field(name="ℹ️ اطلاعات", value="""
`!serverinfo` — اطلاعات سرور
`!userinfo [@user]` — اطلاعات کاربر
""", inline=False)

        embed.set_footer(text="برای جزئیات بیشتر: !help <دستور>")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
