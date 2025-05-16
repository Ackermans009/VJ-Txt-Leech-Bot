# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess
import unicodedata

import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- Helper: Sanitize file names ---
def sanitize_filename(name, max_length=60):
    # Normalize Unicode characters and convert to ASCII.
    normalized = unicodedata.normalize('NFKD', name)
    ascii_str = normalized.encode('ASCII', 'ignore').decode('ASCII')
    # Remove unwanted characters (allow letters, digits, underscore, dash, dot)
    safe = re.sub(r'[^\w\s\.-]', '', ascii_str)
    # Replace spaces with underscore and strip extra underscores.
    safe = re.sub(r'\s+', '_', safe).strip('_')
    return safe[:max_length]

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(f"<b>Hello {m.from_user.mention} 👋\n\nI Am A Bot For Download Links From Your <b>.TXT</b> File And Then Upload That File On Telegram. Send /upload to begin.\n\nUse /stop to stop any ongoing task.</b>")

@bot.on_message(filters.command("stop"))
async def restart_handler(_, m: Message):
    await m.reply_text("**Stopped**🚦", quote=True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text('𝕤ᴇɴᴅ ᴛxᴛ ғɪʟᴇ ⚡️')
    inp: Message = await bot.listen(editable.chat.id)
    txt_file = await inp.download()
    await inp.delete(True)

    downloads_path = f"./downloads/{m.chat.id}"
    os.makedirs(downloads_path, exist_ok=True)

    try:
        with open(txt_file, "r") as f:
            content = f.read()
        lines = content.split("\n")
        # Each line is split into two parts on "://"
        links = [line.split("://", 1) for line in lines if "://" in line]
        os.remove(txt_file)
    except Exception as e:
        await m.reply_text("**Invalid file input.**")
        os.remove(txt_file)
        return

    await editable.edit(f"**𝕋ᴏᴛᴀʟ ʟɪɴᴋ𝕤 ғᴏᴜɴᴅ ᴀʀᴇ 🔗: {len(links)}**\n\n**Enter the starting index for downloads (default = 1):**")
    inp0: Message = await bot.listen(editable.chat.id)
    raw_index = inp0.text.strip()
    await inp0.delete(True)
    try:
        start_index = int(raw_index) if raw_index.isdigit() and int(raw_index) > 0 else 1
    except:
        start_index = 1

    await editable.edit("**Now, send your Batch Name.**")
    inp1: Message = await bot.listen(editable.chat.id)
    batch_name = inp1.text.strip()
    await inp1.delete(True)
    
    await editable.edit("**Enter Resolution 📸 (choose among 144,240,360,480,720,1080):**")
    inp2: Message = await bot.listen(editable.chat.id)
    raw_quality = inp2.text.strip()
    await inp2.delete(True)
    try:
        if raw_quality == "144": res = "256x144"
        elif raw_quality == "240": res = "426x240"
        elif raw_quality == "360": res = "640x360"
        elif raw_quality == "480": res = "854x480"
        elif raw_quality == "720": res = "1280x720"
        elif raw_quality == "1080": res = "1920x1080"
        else: res = "UN"
    except Exception:
        res = "UN"

    await editable.edit("**Enter a Caption for your uploaded file:**")
    inp3: Message = await bot.listen(editable.chat.id)
    caption = inp3.text.strip()
    await inp3.delete(True)
    highlighter = "️ ⁪⁬⁮⁮⁮"
    MR = highlighter if caption == "Robin" else caption

    await editable.edit("**Now, send the Thumbnail URL (e.g., https://graph.org/file/ce1723991756e48c35aa1.jpg) or type = no:**")
    inp6: Message = await bot.listen(editable.chat.id)
    thumb_input = inp6.text.strip()
    await inp6.delete(True)
    await editable.delete()

    thumb = None
    if thumb_input.lower() != "no" and (thumb_input.startswith("http://") or thumb_input.startswith("https://")):
        # Download the thumbnail using wget.
        status, _ = getstatusoutput(f"wget '{thumb_input}' -O 'thumb.jpg'")
        if status == 0:
            thumb = "thumb.jpg"

    if len(links) == 1:
        cur_index = 1
    else:
        cur_index = start_index

    try:
        for i in range(cur_index - 1, len(links)):
            # Reconstruct URL
            raw_url_part = links[i][1].strip()
            url = "https://" + raw_url_part
            url = url.replace("file/d/", "uc?export=download&id=")\
                     .replace("www.youtube-nocookie.com/embed", "youtu.be")\
                     .replace("?modestbranding=1", "")\
                     .replace("/view?usp=sharing", "")

            # Special handling for visionias links: get m3u8 link from webpage
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Pragma': 'no-cache',
                        'Referer': 'http://www.visionias.in/',
                        'Sec-Fetch-Dest': 'iframe',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'cross-site',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
                    }) as resp:
                        text = await resp.text()
                        match = re.search(r'(https://.*?playlist\.m3u8.*?)"', text)
                        if match:
                            url = match.group(1)
            elif 'videos.classplusapp' in url:
                r = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}',
                                 headers={'x-access-token': 'eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJpZCI6MzgzNjkyMTIsIm9yZ0lkIjoyNjA1LCJ0eXBlIjoxLCJtb2JpbGUiOiI5MTcwODI3NzQyODkiLCJuYW1lIjoiQWNlIiwiZW1haWwiOm51bGwsImlzRmlyc3RMb2dpbiI6dHJ1ZSwiZGVmYXVsdExhbmd1YWdlIjpudWxsLCJjb3VudHJ5Q29kZSI6IklOIiwiaXNJbnRlcm5hdGlvbmFsIjowLCJpYXQiOjE2NDMyODE4NzcsImV4cCI6MTY0Mzg4NjY3N30.hM33P2ai6ivdzxPPfm01LAd4JWv-vnrSxGXqvCirCSpUfhhofpeqyeHPxtstXwe0'})
                url = r.json()['url']
            elif '/master.mpd' in url:
                id_part = url.split("/")[-2]
                url = "https://d26g5bnklkwsh4.cloudfront.net/" + id_part + "/master.m3u8"

            # Sanitize the file label
            raw_label = links[i][0]
            safe_label = sanitize_filename(raw_label)
            name = f"{str(cur_index).zfill(3)}_{safe_label}"

            # Choose format string based on URL type
            if "youtu" in url:
                ytf = f"b[height<={raw_quality}][ext=mp4]/bv[height<={raw_quality}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_quality}]/bv[height<={raw_quality}]+ba/b/bv+ba"

            # Build yt-dlp command. For "jw-prod" URLs use a simpler command.
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                # Build captions
                cc = f'**[📽️] Vid_ID:** {str(cur_index).zfill(3)}. ** {name}{MR}.mkv\n**𝔹ᴀᴛᴄʜ** » **{batch_name}**'
                cc1 = f'**[📁] Pdf_ID:** {str(cur_index).zfill(3)}. {name}{MR}.pdf\n**𝔹ᴀᴛᴄʜ** » **{batch_name}**'
                
                if "drive" in url:
                    try:
                        file_path = await helper.download(url, name)
                        if file_path and os.path.isfile(file_path):
                            await bot.send_document(chat_id=m.chat.id, document=file_path, caption=cc1)
                        cur_index += 1
                        os.remove(file_path)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                
                elif ".pdf" in url:
                    try:
                        # Download PDF using subprocess and check if file exists.
                        pdf_filename = f"{name}.pdf"
                        cmd_pdf = f'yt-dlp -o "{pdf_filename}" "{url}" -R 25 --fragment-retries 25'
                        result = subprocess.run(cmd_pdf, shell=True)
                        if os.path.isfile(pdf_filename):
                            await bot.send_document(chat_id=m.chat.id, document=pdf_filename, caption=cc1)
                            os.remove(pdf_filename)
                        else:
                            await m.reply_text(f"**Skipping PDF {name}: File not found after download.**")
                        cur_index += 1
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                else:
                    # For video links (e.g. mp4, m3u8)
                    status_message = (f"**⥥ 🄳🄾🅆🄽🄻🄾🄰🄳🄸🄽🄶⬇️⬇️... »**\n\n"
                                      f"**📝Name »** `{name}`\n❄Quality » {raw_quality}\n\n**🔗URL »** `{url}`")
                    prog = await m.reply_text(status_message)
                    res_file = await helper.download_video(url, cmd, name)
                    if res_file and os.path.isfile(res_file):
                        await prog.delete(True)
                        await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                    else:
                        await m.reply_text(f"**Skipping video {name}: File not found after download.**")
                    cur_index += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(f"**Downloading Interrupted**\n{str(e)}\n**Name »** {name}\n**Link »** `{url}`")
                continue

    except Exception as e:
        await m.reply_text(str(e))
    await m.reply_text("**𝔻ᴏɴᴇ 𝔹ᴏ𝕤𝕤😎**")

bot.run()
