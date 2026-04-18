import asyncio
import sys

# Fix for Python 3.10+: create event loop before pyrogram import
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Fix for Python 3.14+: pyromod Identifier.__annotations__ compatibility
# In Python 3.14, instance __annotations__ is no longer auto-created,
# causing pyromod callback_query_handler to crash on every button press.
if sys.version_info >= (3, 14):
    try:
        import pyromod.types.identifier as _pyromod_id

        if not hasattr(_pyromod_id.Identifier, '__annotations__'):
            _pyromod_id.Identifier.__annotations__ = {}

        _orig_count_populated = _pyromod_id.Identifier.count_populated

        def _patched_count_populated(self):
            class_annotations = {}
            for klass in reversed(type(self).__mro__):
                class_annotations.update(
                    vars(klass).get('__annotations__', {})
                )
            saved = self.__dict__.get('__annotations__')
            self.__dict__['__annotations__'] = class_annotations
            try:
                return _orig_count_populated(self)
            finally:
                if saved is None:
                    self.__dict__.pop('__annotations__', None)
                else:
                    self.__dict__['__annotations__'] = saved

        _pyromod_id.Identifier.count_populated = _patched_count_populated

        _orig_matches = _pyromod_id.Identifier.matches

        def _patched_matches(self, update):
            class_annotations = {}
            for klass in reversed(type(self).__mro__):
                class_annotations.update(
                    vars(klass).get('__annotations__', {})
                )
            saved = self.__dict__.get('__annotations__')
            self.__dict__['__annotations__'] = class_annotations
            try:
                return _orig_matches(self, update)
            finally:
                if saved is None:
                    self.__dict__.pop('__annotations__', None)
                else:
                    self.__dict__['__annotations__'] = saved

        _pyromod_id.Identifier.matches = _patched_matches

    except Exception as e:
        print(f"Warning: Could not patch pyromod for Python 3.14: {e}")
        pass

import os
import json
import logging
import random
import threading
import time
import zipfile
from typing import Dict, List, Any

import aiohttp
import requests
from flask import Flask

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyrogram.errors import FloodWait
from pyromod import listen  # noqa: F401 (registers bot.listen)
from pyromod.exceptions.listener_timeout import ListenerTimeout

from config import api_id, api_hash, bot_token, auth_users

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# ────────────────────────────────────────────────────────────────────────────
# Bot credentials (env first, config as fallback)
# ────────────────────────────────────────────────────────────────────────────
API_ID = int(os.environ.get("API_ID", api_id))
API_HASH = os.environ.get("API_HASH", api_hash)
BOT_TOKEN = os.environ.get("BOT_TOKEN", bot_token)

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

image_list = [
    "https://i.ibb.co/0p3pmkwn/Angel.jpg",
    "https://i.ibb.co/KjNBPrtk/STRANGER-BOY.jpg",
    "https://i.ibb.co/ccV44ZRS/STRANGER-BOY.jpg",
    "https://i.ibb.co/HffWwnB7/STRANGER-BOY.jpg",
    "https://i.ibb.co/cV4W8BQ/STRANGER-BOY.jpg",
    "https://i.ibb.co/5NgcXjR/STRANGER-BOY.jpg",
    "https://i.ibb.co/HLFvQJd6/STRANGER-BOY.jpg",
    "https://i.ibb.co/dsw2rr27/STRANGER-BOY.jpg",
    "https://i.ibb.co/mCbS89dv/STRANGER-BOY.jpg",
    "https://i.ibb.co/CsTdxj4r/STRANGER-BOY.jpg",
    "https://i.ibb.co/GXrkX7c/STRANGER-BOY.jpg",
    "https://i.ibb.co/KpbdvnMG/STRANGER-BOY.jpg",
    "https://i.ibb.co/CNRcXKZ/STRANGER-BOY.jpg",
    "https://i.ibb.co/CpCGzDfz/STRANGER-BOY.jpg",
]


# ────────────────────────────────────────────────────────────────────────────
# Constants for Physics Wallah (pw.live / api.penpencil.co)
# ────────────────────────────────────────────────────────────────────────────
PW_API_BASE = "https://api.penpencil.co"
PW_ORG_ID = "5eb393ee95fab7468a79d189"
PW_DEFAULT_HEADERS = {
    "Host": "api.penpencil.co",
    "client-id": PW_ORG_ID,
    "client-version": "1952",
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 12; M2101K6P) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
    ),
    "randomid": "72012511-256c-4e1c-b4c7-29d67136af37",
    "client-type": "WEB",
    "content-type": "application/json; charset=utf-8",
    "accept": "application/json, text/plain, */*",
    "origin": "https://www.pw.live",
    "referer": "https://www.pw.live/",
}

# Content types available on PW batches contents listing
PW_CONTENT_TYPES = ("videos", "notes", "DppNotes", "DppVideos")


# ────────────────────────────────────────────────────────────────────────────
# /start
# ────────────────────────────────────────────────────────────────────────────
@bot.on_message(filters.command(["start"]))
async def start(bot, message):
    random_image_url = random.choice(image_list)

    keyboard = [
        [
            InlineKeyboardButton(
                "🧧 STRANGER BOYS ✅🧧",
                url="https://t.me/+aBB53vou0Z5hZWI1",
            )
        ],
        [
            InlineKeyboardButton(
                "🌸 🎉Physics Wallah🎉 BOYS 🌸",
                callback_data="pwwp",
            )
        ],
        [
            InlineKeyboardButton(
                "✨️ समय यात्री ✨️",
                url="https://t.me/+jjYZLW4sTmIwOTdl",
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_photo(
        photo=random_image_url,
        caption=(
            "**❖────[『 WELCOME STRANGER 』]"
            "(https://i.ibb.co/0p3pmkwn/Angel.jpg)────❖**"
        ),
        quote=True,
        reply_markup=reply_markup,
    )


# ────────────────────────────────────────────────────────────────────────────
# Generic JSON fetch with retries
# ────────────────────────────────────────────────────────────────────────────
async def fetch_pwwp_data(
    session: aiohttp.ClientSession,
    url: str,
    headers: Dict = None,
    params: Dict = None,
    data: Dict = None,
    method: str = "GET",
    quiet_statuses: tuple = (404,),
) -> Any:
    """
    Robust JSON fetch.

    - 4xx (except 429) is terminal: no retry, return None.
    - 404s are common when a chapter/contentType has no data; log quietly.
    - 401/403 always surfaced once.
    - 5xx and transient network errors are retried with exponential backoff.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with session.request(
                method, url, headers=headers, params=params, json=data
            ) as response:
                status = response.status

                if status in (401, 403):
                    text = await response.text()
                    logging.error(
                        f"Auth error {status} for {url}: {text[:200]}"
                    )
                    return None

                if 400 <= status < 500 and status != 429:
                    # Terminal client error — don't retry
                    if status in quiet_statuses:
                        logging.debug(f"{status} (expected) for {url}")
                    else:
                        text = await response.text()
                        logging.warning(
                            f"{status} for {url}: {text[:200]}"
                        )
                    return None

                if status >= 500 or status == 429:
                    logging.warning(
                        f"Attempt {attempt + 1}: {status} for {url}, will retry"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return None

                try:
                    return await response.json()
                except Exception:
                    text = await response.text()
                    try:
                        return json.loads(text)
                    except Exception:
                        logging.error(
                            f"Non-JSON response from {url}: {text[:200]}"
                        )
                        return None

        except aiohttp.ClientError as e:
            logging.warning(
                f"Attempt {attempt + 1} network error fetching {url}: {e}"
            )
        except Exception as e:
            logging.exception(
                f"Attempt {attempt + 1} unexpected error fetching {url}: {e}"
            )

        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
        else:
            logging.error(f"Failed to fetch {url} after {max_retries} attempts.")
            return None


# ────────────────────────────────────────────────────────────────────────────
# URL helpers
# ────────────────────────────────────────────────────────────────────────────
def _clean(name: str) -> str:
    if not name:
        return ""
    return str(name).strip().replace("\n", " ").replace("\r", " ")


def _attachment_url(att: Dict) -> str:
    """Build the full attachment URL from a PW attachment object."""
    if not att:
        return ""
    base = att.get("baseUrl") or ""
    key = att.get("key") or ""
    if base or key:
        return f"{base}{key}"
    return att.get("url") or att.get("downloadUrl") or ""


def _build_video_url(data_item: Dict, video_details: Dict) -> str:
    """Prefer direct videoUrl, fall back to embedCode; append PW player ids."""
    if not video_details:
        return ""
    video_url = (
        video_details.get("videoUrl")
        or video_details.get("embedCode")
        or video_details.get("url")
        or ""
    )
    if not video_url:
        return ""
    parent_id = data_item.get("parentId") or ""
    child_id = data_item.get("_id") or ""
    video_id = video_details.get("_id") or ""
    if parent_id and child_id and video_id and "parentId=" not in video_url:
        joiner = "&" if "?" in video_url else "?"
        video_url = (
            f"{video_url}{joiner}parentId={parent_id}"
            f"&childId={child_id}&videoId={video_id}"
        )
    return video_url


def _extract_attachments_from_homeworks(homework_ids: List[Dict]) -> List[str]:
    """Flatten homeworkIds → attachmentIds into 'name:url' lines."""
    lines: List[str] = []
    for homework in homework_ids or []:
        if not isinstance(homework, dict):
            continue
        name = _clean(homework.get("topic") or homework.get("name") or "note")
        for attachment in homework.get("attachmentIds") or []:
            url = _attachment_url(attachment)
            if url:
                lines.append(f"{name}:{url}")
    return lines


# ────────────────────────────────────────────────────────────────────────────
# Schedule-details parser (single lecture/content item)
# ────────────────────────────────────────────────────────────────────────────
async def process_pwwp_chapter_content(
    session: aiohttp.ClientSession,
    chapter_id,
    selected_batch_id,
    subject_id,
    schedule_id,
    content_type,
    headers: Dict,
):
    url = (
        f"{PW_API_BASE}/v1/batches/{selected_batch_id}"
        f"/subject/{subject_id}/schedule/{schedule_id}/schedule-details"
    )
    data = await fetch_pwwp_data(session, url, headers=headers)
    content: List[str] = []

    if not (data and data.get("success") and data.get("data")):
        logging.warning(f"No Data Found For Id - {schedule_id}")
        return {}

    data_item = data["data"] or {}

    # ── Videos / DppVideos ─────────────────────────────────────────────
    if content_type in ("videos", "DppVideos"):
        name = _clean(data_item.get("topic") or "video")

        # Primary videoDetails object
        video_details = data_item.get("videoDetails") or {}
        video_url = _build_video_url(data_item, video_details)
        if video_url:
            content.append(f"{name}:{video_url}")

        # videoUrl can also live at the top level on some schedules
        for key in ("url", "videoUrl", "embedCode"):
            top_url = data_item.get(key)
            if top_url and isinstance(top_url, str) and top_url not in (
                content and content[-1] or ""
            ):
                if not any(top_url in line for line in content):
                    content.append(f"{name}:{top_url}")

        # Some DPP schedules embed the DPP video under `dpp.videos`
        dpp = data_item.get("dpp") or {}
        for vid in dpp.get("videos") or []:
            if isinstance(vid, dict):
                vu = _build_video_url(data_item, vid)
                if vu and not any(vu in line for line in content):
                    vname = _clean(vid.get("name") or name)
                    content.append(f"{vname}:{vu}")

    # ── Notes / DppNotes ───────────────────────────────────────────────
    if content_type in ("notes", "DppNotes"):
        # Lecture PDFs / notes
        content.extend(
            _extract_attachments_from_homeworks(data_item.get("homeworkIds"))
        )

        # Some items expose attachmentIds at the top level
        top_atts = data_item.get("attachmentIds") or []
        if top_atts:
            top_name = _clean(data_item.get("topic") or "note")
            for att in top_atts:
                u = _attachment_url(att)
                if u:
                    content.append(f"{top_name}:{u}")

        # DPP notes live under dpp.homeworkIds for DppNotes schedules
        dpp = data_item.get("dpp") or {}
        content.extend(
            _extract_attachments_from_homeworks(dpp.get("homeworkIds"))
        )

        # Exercise / practice sheets
        for ex in data_item.get("exerciseIds") or []:
            if isinstance(ex, dict):
                ename = _clean(ex.get("topic") or ex.get("name") or "exercise")
                for att in ex.get("attachmentIds") or []:
                    u = _attachment_url(att)
                    if u:
                        content.append(f"{ename}:{u}")

    return {content_type: content} if content else {}


# ────────────────────────────────────────────────────────────────────────────
# Chapter → paginated schedules for a given content type
# ────────────────────────────────────────────────────────────────────────────
async def fetch_pwwp_all_schedule(
    session: aiohttp.ClientSession,
    chapter_id,
    selected_batch_id,
    subject_id,
    content_type,
    headers: Dict,
) -> List[Dict]:
    """
    Page through the v2 contents endpoint.

    An empty `data` array is a legitimate "no content of this type" response,
    not an error — don't fall back to v3 (the v3 URL 404s on pw.live today).
    """
    all_schedule: List[Dict] = []
    page = 1
    while True:
        params = {
            "tag": chapter_id,
            "contentType": content_type,
            "page": page,
        }
        url = (
            f"{PW_API_BASE}/v2/batches/"
            f"{selected_batch_id}/subject/{subject_id}/contents"
        )
        data = await fetch_pwwp_data(
            session, url, headers=headers, params=params
        )

        if not (data and data.get("success")):
            break
        items = data.get("data") or []
        if not items:
            break
        for item in items:
            item["content_type"] = content_type
            all_schedule.append(item)
        page += 1
    return all_schedule


async def process_pwwp_chapters(
    session: aiohttp.ClientSession,
    chapter_id,
    selected_batch_id,
    subject_id,
    headers: Dict,
):
    all_schedule_tasks = [
        fetch_pwwp_all_schedule(
            session, chapter_id, selected_batch_id, subject_id, ct, headers
        )
        for ct in PW_CONTENT_TYPES
    ]
    all_schedules = await asyncio.gather(
        *all_schedule_tasks, return_exceptions=True
    )

    all_schedule: List[Dict] = []
    for schedule in all_schedules:
        if isinstance(schedule, Exception):
            logging.error(f"fetch_pwwp_all_schedule failed: {schedule}")
            continue
        all_schedule.extend(schedule)

    content_tasks = [
        process_pwwp_chapter_content(
            session,
            chapter_id,
            selected_batch_id,
            subject_id,
            item["_id"],
            item["content_type"],
            headers,
        )
        for item in all_schedule
        if item.get("_id")
    ]
    content_results = await asyncio.gather(
        *content_tasks, return_exceptions=True
    )

    combined_content: Dict[str, List[str]] = {}
    for result in content_results:
        if isinstance(result, Exception):
            logging.error(f"process_pwwp_chapter_content failed: {result}")
            continue
        if result:
            for content_type, content_list in result.items():
                combined_content.setdefault(content_type, []).extend(
                    content_list
                )
    return combined_content


async def get_pwwp_all_chapters(
    session: aiohttp.ClientSession,
    selected_batch_id,
    subject_id,
    headers: Dict,
):
    """Page through the v2 topics endpoint for a given subject."""
    all_chapters: List[Dict] = []
    page = 1
    while True:
        url = (
            f"{PW_API_BASE}/v2/batches/"
            f"{selected_batch_id}/subject/{subject_id}/topics?page={page}"
        )
        data = await fetch_pwwp_data(session, url, headers=headers)
        if not (data and data.get("data")):
            break
        chapters = data["data"]
        if not chapters:
            break
        all_chapters.extend(chapters)
        page += 1
    return all_chapters


async def process_pwwp_subject(
    session: aiohttp.ClientSession,
    subject: Dict,
    selected_batch_id: str,
    selected_batch_name: str,
    zipf: zipfile.ZipFile,
    json_data: Dict,
    all_subject_urls: Dict[str, List[str]],
    headers: Dict,
):
    subject_name = subject.get("subject", "Unknown Subject").replace("/", "-")
    subject_id = subject.get("_id")
    json_data[selected_batch_name][subject_name] = {}
    zipf.writestr(f"{subject_name}/", "")

    chapters = await get_pwwp_all_chapters(
        session, selected_batch_id, subject_id, headers
    )

    chapter_tasks = []
    for chapter in chapters:
        chapter_name = chapter.get("name", "Unknown Chapter").replace("/", "-")
        zipf.writestr(f"{subject_name}/{chapter_name}/", "")
        json_data[selected_batch_name][subject_name][chapter_name] = {}

        chapter_tasks.append(
            process_pwwp_chapters(
                session, chapter["_id"], selected_batch_id, subject_id, headers
            )
        )

    chapter_results = await asyncio.gather(
        *chapter_tasks, return_exceptions=True
    )

    all_urls: List[str] = []
    for chapter, chapter_content in zip(chapters, chapter_results):
        chapter_name = chapter.get("name", "Unknown Chapter").replace("/", "-")

        if isinstance(chapter_content, Exception):
            logging.error(
                f"Chapter '{chapter_name}' failed: {chapter_content}"
            )
            continue

        for content_type in PW_CONTENT_TYPES:
            if chapter_content.get(content_type):
                content = chapter_content[content_type]
                content_string = "\n".join(content)
                zipf.writestr(
                    f"{subject_name}/{chapter_name}/{content_type}.txt",
                    content_string.encode("utf-8"),
                )
                json_data[selected_batch_name][subject_name][chapter_name][
                    content_type
                ] = content
                all_urls.extend(content)

    all_subject_urls[subject_name] = all_urls


# ────────────────────────────────────────────────────────────────────────────
# Legacy / expired batch fallback (community mirror)
# ────────────────────────────────────────────────────────────────────────────
def find_pw_old_batch(batch_search):
    try:
        response = requests.get(
            "https://abhiguru143.github.io/AS-MULTIVERSE-PW/batch/batch.json",
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return []

    matching_batches = []
    for batch in data:
        if batch_search.lower() in batch["batch_name"].lower():
            matching_batches.append(batch)
    return matching_batches


# ────────────────────────────────────────────────────────────────────────────
# Today's schedule
# ────────────────────────────────────────────────────────────────────────────
async def get_pwwp_todays_schedule_content_details(
    session: aiohttp.ClientSession,
    selected_batch_id,
    subject_id,
    schedule_id,
    headers: Dict,
) -> List[str]:
    url = (
        f"{PW_API_BASE}/v1/batches/{selected_batch_id}"
        f"/subject/{subject_id}/schedule/{schedule_id}/schedule-details"
    )
    data = await fetch_pwwp_data(session, url, headers)
    content: List[str] = []

    if not (data and data.get("success") and data.get("data")):
        logging.warning(f"No Data Found For Id - {schedule_id}")
        return content

    data_item = data["data"] or {}
    name = _clean(data_item.get("topic") or "video")

    video_details = data_item.get("videoDetails") or {}
    video_url = _build_video_url(data_item, video_details)
    if video_url:
        content.append(f"{name}:{video_url}\n")

    # Lecture PDFs
    for line in _extract_attachments_from_homeworks(
        data_item.get("homeworkIds")
    ):
        content.append(line + "\n")

    # Top-level attachments
    for att in data_item.get("attachmentIds") or []:
        u = _attachment_url(att)
        if u:
            content.append(f"{name}:{u}\n")

    # DPP content (PDF + video)
    dpp = data_item.get("dpp") or {}
    for line in _extract_attachments_from_homeworks(dpp.get("homeworkIds")):
        content.append(line + "\n")
    for vid in dpp.get("videos") or []:
        if isinstance(vid, dict):
            vu = _build_video_url(data_item, vid)
            if vu:
                vname = _clean(vid.get("name") or name)
                content.append(f"{vname}:{vu}\n")

    return content


async def get_pwwp_all_todays_schedule_content(
    session: aiohttp.ClientSession,
    selected_batch_id: str,
    headers: Dict,
) -> List[str]:
    url = f"{PW_API_BASE}/v1/batches/{selected_batch_id}/todays-schedule"
    todays = await fetch_pwwp_data(session, url, headers)
    all_content: List[str] = []

    if not (todays and todays.get("success") and todays.get("data")):
        logging.warning("No today's schedule data found.")
        return all_content

    tasks = []
    for item in todays["data"]:
        schedule_id = item.get("_id")
        subject_id = item.get("batchSubjectId")
        if not (schedule_id and subject_id):
            continue
        tasks.append(
            asyncio.create_task(
                get_pwwp_todays_schedule_content_details(
                    session, selected_batch_id, subject_id, schedule_id, headers
                )
            )
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logging.error(f"todays schedule failed: {result}")
            continue
        all_content.extend(result)
    return all_content


# ────────────────────────────────────────────────────────────────────────────
# Khazana (PW library) — best effort; gracefully reports if not available
# ────────────────────────────────────────────────────────────────────────────
async def process_pwwp_khazana(
    session: aiohttp.ClientSession,
    headers: Dict,
    clean_file_name: str,
) -> str:
    """
    Best-effort khazana extraction.

    Tries the `khazana` subscription endpoints used by pw.live's web app.
    Returns the path to the produced txt file, or raises on failure.
    """
    programs_url = (
        f"{PW_API_BASE}/v1/subscription/khazana/programs?mode=1"
    )
    programs = await fetch_pwwp_data(session, programs_url, headers=headers)
    if not (programs and programs.get("success") and programs.get("data")):
        raise Exception(
            "Khazana not available on this account "
            "(no purchased programs found)."
        )

    lines: List[str] = []
    for program in programs["data"]:
        prog_id = program.get("_id")
        prog_name = _clean(program.get("name") or "program")
        if not prog_id:
            continue

        subjects_url = (
            f"{PW_API_BASE}/v1/subscription/khazana/programs/"
            f"{prog_id}/subjects"
        )
        subjects = await fetch_pwwp_data(session, subjects_url, headers=headers)
        if not (subjects and subjects.get("data")):
            continue

        for subj in subjects["data"]:
            subj_id = subj.get("_id")
            subj_name = _clean(subj.get("name") or "subject")
            if not subj_id:
                continue

            chapters_url = (
                f"{PW_API_BASE}/v1/subscription/khazana/programs/"
                f"{prog_id}/subjects/{subj_id}/chapters"
            )
            chapters = await fetch_pwwp_data(
                session, chapters_url, headers=headers
            )
            if not (chapters and chapters.get("data")):
                continue

            for chap in chapters["data"]:
                chap_id = chap.get("_id")
                chap_name = _clean(chap.get("name") or "chapter")
                if not chap_id:
                    continue

                contents_url = (
                    f"{PW_API_BASE}/v1/subscription/khazana/programs/"
                    f"{prog_id}/subjects/{subj_id}/chapters/{chap_id}/contents"
                )
                page = 1
                while True:
                    c = await fetch_pwwp_data(
                        session,
                        contents_url,
                        headers=headers,
                        params={"page": page},
                    )
                    if not (c and c.get("data")):
                        break
                    for item in c["data"]:
                        topic = _clean(item.get("topic") or item.get("name"))
                        prefix = f"{prog_name} / {subj_name} / {chap_name} / {topic}"
                        vd = item.get("videoDetails") or {}
                        vu = _build_video_url(item, vd)
                        if vu:
                            lines.append(f"{prefix}:{vu}")
                        for att in item.get("attachmentIds") or []:
                            u = _attachment_url(att)
                            if u:
                                lines.append(f"{prefix}:{u}")
                        for hw in item.get("homeworkIds") or []:
                            for att in hw.get("attachmentIds") or []:
                                u = _attachment_url(att)
                                if u:
                                    lines.append(f"{prefix}:{u}")
                    page += 1

    if not lines:
        raise Exception("Khazana returned no extractable content.")

    out_path = f"{clean_file_name}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return out_path


# ────────────────────────────────────────────────────────────────────────────
# /start → pwwp callback → full PW flow
# ────────────────────────────────────────────────────────────────────────────
@bot.on_callback_query(filters.regex("^pwwp$"))
async def pwwp_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    await callback_query.answer()

    auth_user = auth_users[0]
    user = await bot.get_users(auth_user)
    owner_username = "@" + (user.username or "owner")

    if user_id not in auth_users:
        await bot.send_message(
            callback_query.message.chat.id,
            f"**You Are Not Subscribed To This Bot\nContact - {owner_username}**",
        )
        return

    asyncio.create_task(process_pwwp(bot, callback_query.message, user_id))


async def process_pwwp(bot: Client, m: Message, user_id: int):
    editable = await m.reply_text(
        "**Enter Working Access Token\n\nOR\n\nEnter Phone Number**"
    )

    try:
        input1 = await bot.listen(
            chat_id=m.chat.id, filters=filters.user(user_id), timeout=120
        )
        raw_text1 = input1.text
        await input1.delete(True)
    except ListenerTimeout:
        await editable.edit("**Timeout! You took too long to respond**")
        return
    except Exception as e:
        logging.exception(f"Error in input1: {e}")
        await editable.edit(f"**Error: {e}**")
        return

    headers = dict(PW_DEFAULT_HEADERS)

    connector = aiohttp.TCPConnector(limit=1000)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            # ── Login (phone + OTP) or pre-existing token ──────────────
            if raw_text1.isdigit() and len(raw_text1) == 10:
                phone = raw_text1
                otp_payload = {
                    "username": phone,
                    "countryCode": "+91",
                    "organizationId": PW_ORG_ID,
                }
                try:
                    async with session.post(
                        f"{PW_API_BASE}/v1/users/get-otp?smsType=0",
                        json=otp_payload,
                        headers=headers,
                    ) as response:
                        await response.read()
                except Exception as e:
                    await editable.edit(f"**Error : {e}**")
                    return

                editable = await editable.edit("**ENTER OTP YOU RECEIVED**")
                try:
                    input2 = await bot.listen(
                        chat_id=m.chat.id,
                        filters=filters.user(user_id),
                        timeout=120,
                    )
                    otp = input2.text
                    await input2.delete(True)
                except ListenerTimeout:
                    await editable.edit(
                        "**Timeout! You took too long to respond**"
                    )
                    return
                except Exception as e:
                    logging.exception(f"Error in input2: {e}")
                    await editable.edit(f"**Error: {e}**")
                    return

                payload = {
                    "username": phone,
                    "otp": otp,
                    "client_id": "system-admin",
                    "client_secret": "KjPXuAVfC5xbmgreETNMaL7z",
                    "grant_type": "password",
                    "organizationId": PW_ORG_ID,
                    "latitude": 0,
                    "longitude": 0,
                }

                try:
                    async with session.post(
                        f"{PW_API_BASE}/v3/oauth/token",
                        json=payload,
                        headers=headers,
                    ) as response:
                        token_json = await response.json()
                        access_token = token_json["data"]["access_token"]
                        await editable.edit(
                            f"<b>Physics Wallah Login Successful ✅</b>\n\n"
                            f"<pre language='Save this Login Token for future usage'>"
                            f"{access_token}</pre>\n\n"
                        )
                        editable = await m.reply_text(
                            "**Getting Batches In Your I'd**"
                        )
                except Exception as e:
                    await editable.edit(f"**Error : {e}**")
                    return
            else:
                access_token = raw_text1

            headers["authorization"] = f"Bearer {access_token}"

            # ── List purchased batches to validate token ───────────────
            try:
                async with session.get(
                    f"{PW_API_BASE}/v3/batches/all-purchased-batches",
                    headers=headers,
                    params={"mode": "1", "page": "1"},
                ) as response:
                    response.raise_for_status()
                    await response.json()
            except Exception:
                await editable.edit(
                    "**```\nLogin Failed❗TOKEN IS EXPIRED```\n"
                    "Please Enter Working Token\n"
                    "                       OR\nLogin With Phone Number**"
                )
                return

            # ── Batch search ───────────────────────────────────────────
            await editable.edit("**Enter Your Batch Name**")
            try:
                input3 = await bot.listen(
                    chat_id=m.chat.id,
                    filters=filters.user(user_id),
                    timeout=120,
                )
                batch_search = input3.text
                await input3.delete(True)
            except ListenerTimeout:
                await editable.edit(
                    "**Timeout! You took too long to respond**"
                )
                return
            except Exception as e:
                logging.exception(f"Error in input3: {e}")
                await editable.edit(f"**Error: {e}**")
                return

            search_url = (
                f"{PW_API_BASE}/v3/batches/search?name={batch_search}"
            )
            courses = await fetch_pwwp_data(session, search_url, headers=headers)
            courses = courses.get("data", {}) if courses else {}

            if not courses:
                raise Exception("No batches found for the given search name.")

            text = ""
            for cnt, course in enumerate(courses):
                name = course["name"]
                text += f"{cnt + 1}. ```\n{name}```\n"
            await editable.edit(
                "**Send index number of the course to download.\n\n"
                f"{text}\n\n"
                "If Your Batch Not Listed Above Enter - No**"
            )

            try:
                input4 = await bot.listen(
                    chat_id=m.chat.id,
                    filters=filters.user(user_id),
                    timeout=120,
                )
                raw_text4 = input4.text
                await input4.delete(True)
            except ListenerTimeout:
                await editable.edit(
                    "**Timeout! You took too long to respond**"
                )
                return
            except Exception as e:
                logging.exception(f"Error in input4: {e}")
                await editable.edit(f"**Error: {e}**")
                return

            if raw_text4.isdigit() and 1 <= int(raw_text4) <= len(courses):
                selected_course_index = int(raw_text4.strip())
                course = courses[selected_course_index - 1]
                selected_batch_id = course["_id"]
                selected_batch_name = course["name"]
                clean_batch_name = (
                    selected_batch_name.replace("/", "-").replace("|", "-")
                )
                clean_file_name = f"{user_id}_{clean_batch_name}"

            elif "No" in raw_text4:
                old_courses = find_pw_old_batch(batch_search)
                if not old_courses:
                    raise Exception("No batches found in fallback mirror.")

                text = ""
                for cnt, course in enumerate(old_courses):
                    name = course["batch_name"]
                    text += f"{cnt + 1}. ```\n{name}```\n"
                await editable.edit(
                    f"**Send index number of the course to download.\n\n{text}**"
                )

                try:
                    input5 = await bot.listen(
                        chat_id=m.chat.id,
                        filters=filters.user(user_id),
                        timeout=120,
                    )
                    raw_text5 = input5.text
                    await input5.delete(True)
                except ListenerTimeout:
                    await editable.edit(
                        "**Timeout! You took too long to respond**"
                    )
                    return
                except Exception as e:
                    logging.exception(f"Error in input5: {e}")
                    await editable.edit(f"**Error: {e}**")
                    return

                if (
                    raw_text5.isdigit()
                    and 1 <= int(raw_text5) <= len(old_courses)
                ):
                    selected_course_index = int(raw_text5.strip())
                    course = old_courses[selected_course_index - 1]
                    selected_batch_id = course["batch_id"]
                    selected_batch_name = course["batch_name"]
                    clean_batch_name = (
                        selected_batch_name.replace("/", "-").replace("|", "-")
                    )
                    clean_file_name = f"{user_id}_{clean_batch_name}"
                else:
                    raise Exception("Invalid batch index.")
            else:
                raise Exception("Invalid batch index.")

            # ── Choose what to download ─────────────────────────────────
            await editable.edit(
                "1.```\nFull Batch```\n2.```\nToday's Class```\n3.```\nKhazana```"
            )
            try:
                input6 = await bot.listen(
                    chat_id=m.chat.id,
                    filters=filters.user(user_id),
                    timeout=120,
                )
                raw_text6 = input6.text
                await input6.delete(True)
            except ListenerTimeout:
                await editable.edit(
                    "**Timeout! You took too long to respond**"
                )
                return
            except Exception as e:
                logging.exception("Error during option listening:")
                try:
                    await editable.edit(f"**Error: {e}**")
                except Exception:
                    logging.error(
                        f"Failed to send error message to user: {e}"
                    )
                return

            await editable.edit(
                f"**Extracting course : {selected_batch_name} ...**"
            )
            start_time = time.time()

            generated_files: List[str] = []

            if raw_text6 == "1":
                # ── Full batch extraction ───────────────────────────────
                url = f"{PW_API_BASE}/v3/batches/{selected_batch_id}/details"
                batch_details = await fetch_pwwp_data(
                    session, url, headers=headers
                )
                if not (batch_details and batch_details.get("success")):
                    raise Exception(
                        "Error fetching batch details: "
                        f"{(batch_details or {}).get('message')}"
                    )

                subjects = (
                    batch_details.get("data", {}).get("subjects", [])
                )
                json_data = {selected_batch_name: {}}
                all_subject_urls: Dict[str, List[str]] = {}

                zip_path = f"{clean_file_name}.zip"
                json_path = f"{clean_file_name}.json"
                txt_path = f"{clean_file_name}.txt"

                with zipfile.ZipFile(zip_path, "w") as zipf:
                    subject_tasks = [
                        process_pwwp_subject(
                            session,
                            subject,
                            selected_batch_id,
                            selected_batch_name,
                            zipf,
                            json_data,
                            all_subject_urls,
                            headers,
                        )
                        for subject in subjects
                    ]
                    subject_results = await asyncio.gather(
                        *subject_tasks, return_exceptions=True
                    )
                    for i, sr in enumerate(subject_results):
                        if isinstance(sr, Exception):
                            logging.error(
                                f"Subject index {i} failed: {sr}"
                            )

                with open(json_path, "w") as f:
                    json.dump(json_data, f, indent=4)

                total_written = 0
                with open(txt_path, "w", encoding="utf-8") as f:
                    for subject in subjects:
                        subject_name = subject.get(
                            "subject", "Unknown Subject"
                        ).replace("/", "-")
                        lines = all_subject_urls.get(subject_name) or []
                        if lines:
                            f.write("\n".join(lines) + "\n")
                            total_written += len(lines)
                logging.info(
                    f"TXT file written with {total_written} total URLs"
                )

                generated_files = [txt_path, zip_path, json_path]

            elif raw_text6 == "2":
                selected_batch_name = "Today's Class"
                today_schedule = await get_pwwp_all_todays_schedule_content(
                    session, selected_batch_id, headers
                )
                if not today_schedule:
                    raise Exception("No Classes Found Today")
                txt_path = f"{clean_file_name}.txt"
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.writelines(today_schedule)
                generated_files = [txt_path]

            elif raw_text6 == "3":
                selected_batch_name = "Khazana"
                txt_path = await process_pwwp_khazana(
                    session, headers, clean_file_name
                )
                generated_files = [txt_path]

            else:
                raise Exception("Invalid index.")

            # ── Report ──────────────────────────────────────────────────
            end_time = time.time()
            response_time = end_time - start_time
            minutes = int(response_time // 60)
            seconds = int(response_time % 60)
            if minutes == 0:
                if seconds < 1:
                    formatted_time = f"{response_time:.2f} seconds"
                else:
                    formatted_time = f"{seconds} seconds"
            else:
                formatted_time = f"{minutes} minutes {seconds} seconds"

            await editable.delete(True)
            caption = (
                f"**Batch Name : ```\n{selected_batch_name}```"
                f"```\nTime Taken : {formatted_time}```**"
            )

            for file in generated_files:
                if not os.path.exists(file):
                    logging.error(f"File not found: {file}")
                    continue
                file_ext = os.path.splitext(file)[1][1:]
                try:
                    with open(file, "rb") as f:
                        await m.reply_document(
                            document=f,
                            caption=caption,
                            file_name=f"{clean_batch_name}.{file_ext}",
                        )
                except FloodWait as fw:
                    await asyncio.sleep(fw.value)
                except Exception as e:
                    logging.exception(f"Error sending document {file}: {e}")
                finally:
                    try:
                        os.remove(file)
                        logging.info(f"Removed File After Sending : {file}")
                    except OSError as e:
                        logging.error(f"Error deleting {file}: {e}")

        except Exception as e:
            logging.exception(f"An unexpected error occurred: {e}")
            try:
                await editable.edit(f"**Error : {e}**")
            except Exception as ee:
                logging.error(
                    f"Failed to send error message to user in callback: {ee}"
                )


# ────────────────────────────────────────────────────────────────────────────
# Flask keep-alive (for Render / Koyeb healthchecks)
# ────────────────────────────────────────────────────────────────────────────
flask_app = Flask(__name__)


@flask_app.route("/")
def index():
    return "Bot is running!"


def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_flask, daemon=True).start()


if __name__ == "__main__":
    bot.run()
