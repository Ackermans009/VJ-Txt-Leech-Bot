# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import re
import sys
import time
import asyncio
import requests
import subprocess
import unicodedata

import core as helper  # Assumes helper.py contains download, download_video, send_vid functions.
from utils import progress_bar  # Optional for progress indication.
from vars import API_ID, API_HASH, BOT_TOKEN

from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# --- Helper: Normalize and sanitize filenames ---
def sanitize_filename(name, max_length=60):
    # Normalize Unicode and remove non-ASCII characters
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    # Remove unwanted punctuation (keeping alphanumerics, underscores, dashes)
    name = re.sub(r'[^\w\s-]', '', name).strip()
    # Replace all whitespace with underscores
    name = re.sub(r'\s+', '_', name)
    return name[:max_length].rstrip('_')


bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(
        f"<b>Hello {m.from_user.mention} 👋\n\nI Am A Bot For Downloading Links From Your <b>.TXT</b> File And Then Uploading That File To Telegram. "
        f"Send /upload to begin.\n\nUse /stop to terminate any ongoing task.</b>"
    )


@bot.on_message(filters.command("stop"))
async def restart_handler(_, m: Message):
    await m.reply_text("**Stopped**🚦", quote=True)
    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text("𝕤ᴇɴᴅ ᴛxᴛ fæɾ ɪɴᴘᴜᴛ ⚡️")
    input_msg: Message = await bot.listen(editable.chat.id)
    txt_file_path = await input_msg.download()
    await input_msg.delete(True)

    # Build a dedicated download folder for this chat
    download_dir = os.path.join(".", "downloads", str(m.chat.id))
    os.makedirs(download_dir, exist_ok=True)

    try:
        with open(txt_file_path, "r") as f:
            content = f.read()
        lines = content.strip().split("\n")
        links = []
        # Each line is expected to have a label and URL separated by "://"
        for line in lines:
            if "://" in line:
                parts = line.split("://", 1)
                links.append(parts)
        os.remove(txt_file_path)
    except Exception as e:
        await m.reply_text("**Invalid file input.**")
        os.remove(txt_file_path)
        return

    await editable.edit(
        f"**Total links found: {len(links)}**\n\n**Enter the starting index for download (default is 1):**"
    )
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text.strip()
    await input0.delete(True)
    try:
        count = int(raw_text) if raw_text.isdigit() and int(raw_text) > 0 else 1
    except:
        count = 1

    await editable.edit("**Please send your Batch Name.**")
    input1: Message = await bot.listen(editable.chat.id)
    batch_name = input1.text.strip()
    await input1.delete(True)

    await editable.edit("**Enter resolution (choose from 144, 240, 360, 480, 720, 1080):**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text.strip()
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080"
        else:
            res = "UN"
    except Exception:
        res = "UN"

    await editable.edit("**Enter a Caption for your uploaded file:**")
    input3: Message = await bot.listen(editable.chat.id)
    caption = input3.text.strip()
    await input3.delete(True)

    highlighter = f"️ ⁪⁬⁮⁮⁮"
    final_caption = highlighter if caption == "Robin" else caption

    await editable.edit(
        "Now send the Thumb URL (e.g., https://graph.org/file/ce1723991756e48c35aa1.jpg) or type = no if you don't want one"
    )
    input6: Message = await bot.listen(editable.chat.id)
    thumb_input = input6.text.strip()
    await input6.delete(True)
    await editable.delete()

    thumb = None
    if thumb_input.lower() != "no" and (thumb_input.startswith("http://") or thumb_input.startswith("https://")):
        status, _ = getstatusoutput(f"wget '{thumb_input}' -O 'thumb.jpg'")
        if status == 0:
            thumb = "thumb.jpg"

    try:
        for i in range(count - 1, len(links)):
            # Sanitize the label (first part of each TXT line) for a clean filename.
            name_source = links[i][0]
            sanitized_name = sanitize_filename(name_source)
            name = f'{str(count).zfill(3)}_{sanitized_name}'
            # Define the output path (ensuring the file is stored in the proper folder)
            output_file = os.path.join(download_dir, f"{name}.mp4")

            # Reconstruct the URL from the second part.
            url_part = links[i][1].strip()
            url = "https://" + url_part
            url = url.replace("file/d/", "uc?export=download&id=")
            url = url.replace("www.youtube-nocookie.com/embed", "youtu.be")
            url = url.replace("www.youtube.com/embed", "youtu.be")
            url = url.replace("?modestbranding=1", "")
            url = url.replace("/view?usp=sharing", "")

            # Special handling for visionias links:
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
                        m3u8_match = re.search(r"(https://.*?playlist.m3u8.*?)\"", text)
                        if m3u8_match:
                            url = m3u8_match.group(1)

            # Handling for ClassPlusApp videos:
            elif 'videos.classplusapp' in url:
                response = requests.get(
                    f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}',
                    headers={'x-access-token': 'eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9...'}
                )
                if response.status_code == 200:
                    url = response.json().get('url', url)

            # Convert MPD streams to m3u8 if needed:
            elif '/master.mpd' in url:
                id_part = url.split("/")[-2]
                url = "https://d26g5bnklkwsh4.cloudfront.net/" + id_part + "/master.m3u8"

            # For YouTube links, use a custom User-Agent and Referer to try to bypass the sign-in check.
            if "youtu" in url:
                cmd = (
                    f'yt-dlp --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" '
                    f'--add-header "referer: https://www.youtube.com/" -f best "{url}" -o "{output_file}"'
                )
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{output_file}"'

            if "youtu" in url:
                print(f"Downloading YouTube link with command: {cmd}")

            try:
                cc = f'**[📽️] Vid_ID:** {str(count).zfill(3)}.** {name}{final_caption}.mkv\n**𝔹ᴀᴛᴄʜ** » **{batch_name}**'
                cc1 = f'**[📁] Pdf_ID:** {str(count).zfill(3)}. {name}{final_caption}.pdf \n**𝔹ᴀᴛᴄʜ** » **{batch_name}**'

                if "drive" in url:
                    try:
                        file_downloaded = await helper.download(url, name)
                        await bot.send_document(chat_id=m.chat.id, document=file_downloaded, caption=cc1)
                        count += 1
                        os.remove(file_downloaded)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif ".pdf" in url:
                    try:
                        pdf_output = output_file.replace(".mp4", ".pdf")
                        cmd_pdf = f'yt-dlp -o "{pdf_output}" "{url}"'
                        download_cmd = f"{cmd_pdf} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        await bot.send_document(chat_id=m.chat.id, document=pdf_output, caption=cc1)
                        count += 1
                        os.remove(pdf_output)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                else:
                    status_message = (
                        f"**⥥ 🄳🄾🅆🄽🄻🄾🄰🄳🄸🄽🄶⬇️⬇️... »**\n\n"
                        f"**📝Name »** `{name}`\n❄Quality » {raw_text2}\n\n**🔗URL »** `{url}`"
                    )
                    prog = await m.reply_text(status_message)
                    try:
                        res_file = await helper.download_video(url, cmd, name)
                    except Exception as e:
                        err_msg = str(e)
                        # If the output file was not created (due to sign-in errors), skip this video.
                        if "No such file or directory" in err_msg or "Sign in to confirm" in err_msg:
                            await m.reply_text(f"**Skipping video {name}: {err_msg.strip()}**")
                            continue
                        else:
                            await m.reply_text(f"**Download interrupted for Name:** {name}\nError: {err_msg}\n**Link:** `{url}`")
                            continue

                    if not os.path.isfile(res_file):
                        await m.reply_text(f"**Skipping video {name}: File not found after download.**")
                        continue

                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(f"**Download interrupted for Name:** {name}\nError: {str(e)}\n**Link:** `{url}`")
                continue

    except Exception as e:
        await m.reply_text(f"Error occurred: {str(e)}")
    await m.reply_text("**𝔻ᴏɴᴇ 𝔹ᴏ𝕤𝕤😎**")


bot.run()
