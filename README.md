# 🤖 Discord Management Bot - Beta

یک بات مدیریتی کامل برای دیسکورد با قابلیت‌های مدیریت پیام، ضد فحش، ضد اسپم و لاگ‌گیری.

---

## ✨ امکانات

| قابلیت | توضیح |
|---|---|
| 🔨 مدیریت پیام | پاک کردن، قفل کانال، slowmode |
| 👮 مجازات | warn / mute / kick / ban / unban |
| 🚫 ضد فحش | فیلتر خودکار کلمات ممنوعه (فارسی + انگلیسی) |
| 🚨 ضد اسپم | تشخیص و مجازات خودکار اسپمرها |
| 📋 لاگ | ثبت ورود/خروج، حذف/ویرایش پیام، بن |

---

## 🚀 راه‌اندازی

### ۱. پیش‌نیازها
```bash
python 3.10+
pip install -r requirements.txt
```

### ۲. ساخت بات در Discord Developer Portal
1. به [Discord Developer Portal](https://discord.com/developers/applications) بروید
2. **New Application** بزنید
3. به تب **Bot** بروید و توکن را کپی کنید
4. در بخش **Privileged Gateway Intents** همه را فعال کنید:
   - ✅ Presence Intent
   - ✅ Server Members Intent  
   - ✅ Message Content Intent

### ۳. تنظیم توکن
```bash
cp .env.example .env
```
فایل `.env` را باز کنید و توکن بات را وارد کنید:
```
DISCORD_TOKEN=توکن_بات_خود_را_اینجا_بنویسید
```

### ۴. اجرا
```bash
python bot.py
```

---

## 📖 دستورات

### 🔨 مدیریت پیام
| دستور | توضیح |
|---|---|
| `!clear [n]` | پاک کردن n پیام (پیش‌فرض: 10) |
| `!clearuser @user [n]` | پاک کردن پیام‌های یک کاربر |
| `!slowmode [ثانیه]` | تنظیم slowmode (0 = غیرفعال) |
| `!lock` | قفل کردن کانال |
| `!unlock` | باز کردن قفل کانال |

### 👮 مجازات
| دستور | توضیح |
|---|---|
| `!warn @user [دلیل]` | اخطار به کاربر |
| `!mute @user [دقیقه] [دلیل]` | سکوت کردن کاربر |
| `!unmute @user` | لغو سکوت |
| `!kick @user [دلیل]` | اخراج از سرور |
| `!ban @user [دلیل]` | بن کردن |
| `!unban user#0000` | لغو بن |

### 🚫 سیستم ضد فحش
| دستور | توضیح |
|---|---|
| `!swear` | مشاهده وضعیت |
| `!swear on` | فعال کردن |
| `!swear off` | غیرفعال کردن |
| `!swear add <کلمه>` | افزودن کلمه به لیست فیلتر |
| `!swear remove <کلمه>` | حذف کلمه از لیست |
| `!swear list` | مشاهده کلمات فیلتر شده |
| `!swear log #کانال` | تنظیم کانال لاگ |
| `!swear warn` | فعال/غیرفعال اخطار هنگام حذف |

### 🚨 سیستم ضد اسپم
| دستور | توضیح |
|---|---|
| `!antispam` | مشاهده وضعیت |
| `!antispam on/off` | فعال/غیرفعال |
| `!antispam set <max> <ثانیه>` | تنظیم حد (مثال: `!antispam set 5 5`) |
| `!antispam action <delete\|mute\|kick\|ban>` | تنظیم اقدام |
| `!antispam log #کانال` | تنظیم کانال لاگ |

### 📋 سیستم لاگ
| دستور | توضیح |
|---|---|
| `!log` | مشاهده وضعیت |
| `!log set #کانال` | تنظیم کانال لاگ |
| `!log toggle join` | فعال/غیرفعال لاگ ورود |
| `!log toggle leave` | فعال/غیرفعال لاگ خروج |
| `!log toggle delete` | فعال/غیرفعال لاگ حذف پیام |
| `!log toggle edit` | فعال/غیرفعال لاگ ویرایش پیام |
| `!log toggle ban` | فعال/غیرفعال لاگ بن |

### ℹ️ اطلاعات
| دستور | توضیح |
|---|---|
| `!serverinfo` | اطلاعات سرور |
| `!userinfo [@user]` | اطلاعات کاربر |
| `!help [دستور]` | راهنما |

---

## 📁 ساختار پروژه
```
discord-management-bot/
├── bot.py              # فایل اصلی
├── requirements.txt
├── .env                # توکن (نباید آپلود شود)
├── .env.example
├── .gitignore
├── data/               # تنظیمات سرورها (auto-generated)
└── cogs/
    ├── moderation.py   # مدیریت و مجازات
    ├── anti_swear.py   # ضد فحش
    ├── anti_spam.py    # ضد اسپم
    ├── logging.py      # لاگ رویدادها
    └── help.py         # راهنما
```

---

## 🛡️ مجوزهای مورد نیاز برای بات
در پنل Developer Portal هنگام invite کردن بات، این permissions را فعال کنید:
- Manage Messages
- Kick Members
- Ban Members
- Moderate Members (Timeout)
- Manage Channels
- View Audit Log

---

## 📝 لایسنس
MIT License
