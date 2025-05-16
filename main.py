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
    """
    Normalize Unicode, convert to ASCII and remove any unwanted characters.
    """
    # Normalize Unicode and convert to ASCII (ignoring non-convertible chars)
    normalized = unicodedata.normalize('NFKD', name)
    ascii_str = normalized.encode('ASCII', 'ignore').decode('ASCII')
    # Allow alphanumerics, underscores, dashes, and dots; remove others.
    safe = re.sub(r'[^\w\s\.-]', '', ascii_str)
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
    await m.reply_text(
        f"<b>Hello {m.from_user.mention} 👋\n\nI Am A Bot For Download Links From Your <b>.TXT</b> File And Then Upload That File On Telegram. Send /upload to begin.\n\nUse /stop to stop any ongoing task.</b>"
    )

@bot.on_message(filters.command("stop"))
async def restart_handler(_, m: Message):
    await m.reply_text("**Stopped**🚦", quote=True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    # Step 1: Get the TXT file.
    editable = await m.reply_text('𝕤ᴇɴᴅ ᴛxᴛ ғɪʟᴇ ⚡️')
    inp: Message = await bot.listen(editable.chat.id)
    txt_file = await inp.download()
    await inp.delete(True)

    downloads_path = f"./downloads/{m.chat.id}"
    os.makedirs(downloads_path, exist_ok=True)

    # Step 2: Read and parse the file.
    try:
        with open(txt_file, "r") as f:
            content = f.read()
        lines = content.split("\n")
        # Expect lines with "://"; split into [label, url-part]
        links = [line.split("://", 1) for line in lines if "://" in line]
        os.remove(txt_file)
    except Exception as e:
        await m.reply_text("**Invalid file input.**")
        os.remove(txt_file)
        return

    await editable.edit(
        f"**Total links found: {len(links)}**\n\n**Enter the starting index for downloads (default = 1):**"
    )
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
        if raw_quality == "144":
            res = "256x144"
        elif raw_quality == "240":
            res = "426x240"
        elif raw_quality == "360":
            res = "640x360"
        elif raw_quality == "480":
            res = "854x480"
        elif raw_quality == "720":
            res = "1280x720"
        elif raw_quality == "1080":
            res = "1920x1080"
        else:
            res = "UN"
    except Exception:
        res = "UN"

    await editable.edit("**Enter a Caption for your uploaded file:**")
    inp3: Message = await bot.listen(editable.chat.id)
    caption = inp3.text.strip()
    await inp3.delete(True)
    highlighter = "️ ⁪⁬⁮⁮⁮"
    MR = highlighter if caption == "Robin" else caption
   
    await editable.edit("**Now send the Thumbnail URL (e.g., https://graph.org/file/ce1723991756e48c35aa1.jpg) or type = no:**")
    inp6: Message = await bot.listen(editable.chat.id)
    thumb_input = inp6.text.strip()
    await inp6.delete(True)
    await editable.delete()

    thumb = None
    if thumb_input.lower() != "no" and (thumb_input.startswith("http://") or thumb_input.startswith("https://")):
        status, _ = getstatusoutput(f"wget '{thumb_input}' -O 'thumb.jpg'")
        if status == 0:
            thumb = "thumb.jpg"

    cur_index = start_index

    # Process each link.
    try:
        for i in range(cur_index - 1, len(links)):
            # Reconstruct URL from the second part.
            raw_url_part = links[i][1].strip()
            # IMPORTANT: If the original line already starts with "https://", the split will yield:
            # part[0] = "https" and part[1] = "www.example.com/...", so we reassemble with "https://".
            url = "https://" + raw_url_part
            url = url.replace("file/d/", "uc?export=download&id=") \
                     .replace("www.youtube-nocookie.com/embed", "youtu.be") \
                     .replace("?modestbranding=1", "") \
                     .replace("/view?usp=sharing", "")
            
            # Skip links that are not likely media (e.g. Google Fonts).
            if any(x in url for x in ["fonts.googleapis", "fonts.gstatic"]):
                await m.reply_text(f"Skipping invalid link: `{url}`")
                continue

            # Special handling for visionias links: extract m3u8 URL.
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
                r = requests.get(
                    f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}',
                    headers={'x-access-token': 'eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJpZCI6MzgzNjkyMTIsIm9yZ0lkIjoyNjA1LCJ0eXBlIjoxLCJtb2JpbGUiOiI5MTcwODI3NzQyODkiLCJuYW1lIjoiQWNlIiwiZW1haWwiOm51bGwsImlzRmlyc3RMb2dpbiI6dHJ1ZSwiZGVmYXVsdExhbmd1YWdlIjpudWxsLCJjb3VudHJ5Q29kZSI6IklOIiwiaXNJbnRlcm5hdGlvbmFsIjowLCJpYXQiOjE2NDMyODE4NzcsImV4cCI6MTY0Mzg4NjY3N30.hM33P2ai6ivdzxPPfm01LAd4JWv-vnrSxGXqvCirCSpUfhhofpeqyeHPxtstXwe0'
                )
                url = r.json()['url']
            elif '/master.mpd' in url:
                id_part = url.split("/")[-2]
                url = "https://d26g5bnklkwsh4.cloudfront.net/" + id_part + "/master.m3u8"

            # Use the label (first part) and sanitize it.
            raw_label = links[i][0]
            safe_label = sanitize_filename(raw_label)
            fname = f"{str(cur_index).zfill(3)}_{safe_label}"

            # Decide file extension and command based on URL:
            # If the URL indicates a PDF, handle it with requests.
            if ".pdf" in url.lower():
                pdf_filename = f"{fname}.pdf"
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    r = requests.get(url, headers=headers, stream=True, timeout=60)
                    if r.status_code == 200:
                        with open(pdf_filename, "wb") as f_out:
                            for chunk in r.iter_content(chunk_size=8192):
                                f_out.write(chunk)
                    else:
                        await m.reply_text(f"Failed to download PDF {fname}: HTTP {r.status_code}")
                        cur_index += 1
                        continue
                except Exception as e:
                    await m.reply_text(f"Exception downloading PDF {fname}: {e}")
                    cur_index += 1
                    continue
                    
                if os.path.isfile(pdf_filename):
                    cc1 = f'**[📁] Pdf_ID:** {str(cur_index).zfill(3)}. {fname}{MR}.pdf\n**𝔹ᴀᴛᴄʜ** » **{batch_name}**'
                    await bot.send_document(chat_id=m.chat.id, document=pdf_filename, caption=cc1)
                    os.remove(pdf_filename)
                else:
                    await m.reply_text(f"**Skipping PDF {fname}: File not found after download.**")
                cur_index += 1
                time.sleep(1)
                continue

            # Otherwise, assume it's a video/m3u8 link.
            if "youtu" in url:
                ytf = f"b[height<={raw_quality}][ext=mp4]/bv[height<={raw_quality}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_quality}]/bv[height<={raw_quality}]+ba/b/bv+ba"

            if "jw-prod" in url:
                cmd = f'yt-dlp --no-part -o "{fname}.mp4" "{url}"'
            else:
                cmd = f'yt-dlp --no-part -f "{ytf}" "{url}" -o "{fname}.mp4"'

            try:
                cc = f'**[📽️] Vid_ID:** {str(cur_index).zfill(3)}. ** {fname}{MR}.mkv\n**𝔹ᴀᴛᴄʜ** » **{batch_name}**'
                # Show status message.
                status_message = (f"**⥥ 🄳🄾🅆🄽🄻🄾🄰🄳🄸🄽🄶⬇️⬇️... »**\n\n"
                                  f"**📝Name »** `{fname}`\n❄Quality » {raw_quality}\n\n**🔗URL »** `{url}`")
                prog = await m.reply_text(status_message)
                
                # Run yt-dlp command.
                subprocess.run(cmd, shell=True, timeout=300)
                video_filename = f"{fname}.mp4"
                if os.path.isfile(video_filename):
                    await prog.delete(True)
                    # Use helper.send_vid if available, else send as document.
                    await helper.send_vid(bot, m, cc, video_filename, thumb, fname, prog)
                    # Optionally, remove the file after sending.
                    os.remove(video_filename)
                else:
                    await m.reply_text(f"**Skipping video {fname}: File not found after download.**")
                cur_index += 1
                time.sleep(1)
            except Exception as e:
                await m.reply_text(f"**Downloading Interrupted**\n{str(e)}\n**Name »** {fname}\n**Link »** `{url}`")
                cur_index += 1
                continue

    except Exception as e:
        await m.reply_text(str(e))
    await m.reply_text("**𝔻ᴏɴᴇ 𝔹ᴏ𝕤𝕤😎**")

bot.run()
