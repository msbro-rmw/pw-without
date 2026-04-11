
# maindone.py
import asyncio
import aiohttp
import zipfile
import logging
import json
import requests
from typing import Dict, List, Any
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(level=logging.INFO)

# ===================== FETCH =====================
async def fetch_pwwp_data(session, url, headers=None, params=None, data=None, method="GET"):
    for attempt in range(3):
        try:
            async with session.request(method, url, headers=headers, params=params, json=data) as res:
                res.raise_for_status()
                return await res.json()
        except Exception as e:
            logging.error(f"[Retry {attempt+1}] {url} -> {e}")
            await asyncio.sleep(2 * (attempt + 1))
    return None


# ===================== CONTENT =====================
async def process_pwwp_chapter_content(session, batch_id, subject_id, schedule_id, content_type, headers):
    url = f"https://api.penpencil.co/v1/batches/{batch_id}/subject/{subject_id}/schedule/{schedule_id}/schedule-details"
    data = await fetch_pwwp_data(session, url, headers)

    result = []
    if not data or not data.get("data"):
        return {}

    d = data["data"]

    if content_type in ["videos", "DppVideos"]:
        vd = d.get("videoDetails", {})
        url = vd.get("videoUrl") or vd.get("embedCode")
        if url:
            result.append(f"{d.get('topic')}:{url}")

    for hw in d.get("homeworkIds", []):
        for att in hw.get("attachmentIds", []):
            url = att.get("baseUrl", "") + att.get("key", "")
            if url:
                result.append(f"{hw.get('topic')}:{url}")

    return {content_type: result} if result else {}


# ===================== SCHEDULE =====================
async def fetch_schedule(session, batch_id, subject_id, chapter_id, content_type, headers):
    all_items = []
    page = 1

    while True:
        params = {"tag": chapter_id, "contentType": content_type, "page": page}
        url = f"https://api.penpencil.co/v2/batches/{batch_id}/subject/{subject_id}/contents"

        data = await fetch_pwwp_data(session, url, headers, params=params)

        if not data or not data.get("data"):
            break

        for i in data["data"]:
            i["content_type"] = content_type
            all_items.append(i)

        page += 1

    return all_items


# ===================== CHAPTER =====================
async def process_chapter(session, batch_id, subject_id, chapter_id, headers):
    types = ["videos", "notes", "DppNotes", "DppVideos"]

    schedules = await asyncio.gather(*[
        fetch_schedule(session, batch_id, subject_id, chapter_id, t, headers)
        for t in types
    ])

    all_sched = []
    for s in schedules:
        all_sched.extend(s)

    tasks = [
        process_pwwp_chapter_content(
            session, batch_id, subject_id, item["_id"], item["content_type"], headers
        )
        for item in all_sched
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    final = {}
    for r in results:
        if isinstance(r, dict):
            for k, v in r.items():
                final.setdefault(k, []).extend(v)

    return final


# ===================== CHAPTER LIST =====================
async def get_chapters(session, batch_id, subject_id, headers):
    page = 1
    chapters = []

    while True:
        url = f"https://api.penpencil.co/v2/batches/{batch_id}/subject/{subject_id}/topics?page={page}"
        data = await fetch_pwwp_data(session, url, headers)

        if not data or not data.get("data"):
            break

        chapters.extend(data["data"])
        page += 1

    return chapters


# ===================== SUBJECT =====================
async def process_subject(session, batch_id, subject, zipf, headers):
    subject_name = subject.get("subject", "Unknown").replace("/", "-")
    subject_id = subject["_id"]

    chapters = await get_chapters(session, batch_id, subject_id, headers)

    for ch in chapters:
        ch_name = ch["name"].replace("/", "-")
        content = await process_chapter(session, batch_id, subject_id, ch["_id"], headers)

        for k, v in content.items():
            if v:
                text = "\n".join(v)
                zipf.writestr(f"{subject_name}/{ch_name}/{k}.txt", text)


# ===================== MAIN DOWNLOAD =====================
async def download_batch(bot, m, batch_id, batch_name, headers):
    file_name = f"{batch_name.replace('/', '-')}.zip"

    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        with zipfile.ZipFile(file_name, "w", zipfile.ZIP_DEFLATED) as zipf:

            url = f"https://api.penpencil.co/v3/batches/{batch_id}/details"
            data = await fetch_pwwp_data(session, url, headers)

            subjects = data["data"]["subjects"]

            for sub in subjects:
                await process_subject(session, batch_id, sub, zipf, headers)

    await bot.send_document(m.chat.id, file_name, caption="✅ Batch Downloaded")


# ===================== BOT HANDLER =====================
@bot.on_message(filters.command("pw"))
async def start_pw(bot: Client, m: Message):
    msg = await m.reply("Send Access Token:")

    inp = await bot.listen(m.chat.id)
    token = inp.text

    headers = {
        "authorization": f"Bearer {token}",
        "client-id": "5eb393ee95fab7468a79d189"
    }

    async with aiohttp.ClientSession() as session:
        data = await fetch_pwwp_data(session,
            "https://api.penpencil.co/v3/batches/all-purchased-batches",
            headers
        )

    batches = data["data"]

    text = "\n".join([f"{i+1}. {b['name']}" for i, b in enumerate(batches)])
    await msg.edit(f"Select Batch:\n{text}")

    inp2 = await bot.listen(m.chat.id)
    idx = int(inp2.text) - 1

    batch = batches[idx]

    await m.reply("Downloading... ⏳")

    await download_batch(bot, m, batch["_id"], batch["name"], headers)
