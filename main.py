import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# --- بيانات البوت والقناة الخاصة بك ---
API_ID = 1234567  
API_HASH = "your_api_hash"
BOT_TOKEN = "9145398764:AAH_kXxTGgszY9buHx8ycf-AXQSC9XopDgY"
CHANNEL_USERNAME = "@krbla17"

app = Client("MyBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def check_subscription(client, user_id):
    try:
        member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception:
        pass
    return False

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    if not await check_subscription(client, user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("اشترك في القناة 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub")]
        ])
        await message.reply("عذراً، يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من استخدامه!", reply_markup=keyboard)
        return
    await message.reply("أهلاً بك! أرسل لي أي رابط فيديو (إنستغرام، تيك توك، يوتيوب) وسأقوم بتحميله فوراً 📥")

@app.on_callback_query(filters.regex("check_sub"))
async def verify_sub(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_subscription(client, user_id):
        await callback_query.message.edit_text("شكراً لاشتراكك! ✅ الآن أرسل لي أي رابط لتحميله.")
    else:
        await callback_query.answer("لم تقم بالاشتراك في القناة بعد! ❌", show_alert=True)

@app.on_message(filters.text & ~filters.command(["start"]))
async def download(client, message):
    user_id = message.from_user.id
    if not await check_subscription(client, user_id):
        await message.reply("يرجى الاشتراك في القناة أولاً. أرسل `/start` للبدء.")
        return

    url = message.text.strip()
    if not url.startswith("http"):
        await message.reply("الرجاء إرسال رابط صحيح يبدأ بـ http.")
        return

    status = await message.reply("جاري جلب وتحميل الملف... ⏳")
    try:
        os.makedirs("downloads", exist_ok=True)
        ydl_opts = {'outtmpl': 'downloads/%(id)s.%(ext)s', 'format': 'best', 'max_filesize': 50 * 1024 * 1024}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)

        await message.reply_video(video=path, caption="تم التحميل بواسطة بوتك الخاص ✨")
        if os.path.exists(path):
            os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text("حدث خطأ أثناء التحميل. تأكد من صحة الرابط أو أن حجم الفيديو مناسب.")

print("Bot is starting...")
app.run()
                
