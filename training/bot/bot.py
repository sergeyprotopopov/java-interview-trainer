# -*- coding: utf-8 -*-
"""Telegram-бот: диалог-тренажёр для подготовки к Java-собеседованию.

Режим: показывает вопрос → «Показать ответ» → «✅ Знаю / 🔁 Повторить / ➡️ Дальше».
Фильтры по приоритету (S/A/B/C), режим «только ошибки», перемешивание.
Прогресс сохраняется на пользователя (PicklePersistence) и переживает рестарт.

Запуск:
    pip install -r requirements.txt
    export TELEGRAM_BOT_TOKEN=...   # Windows PowerShell: $env:TELEGRAM_BOT_TOKEN="..."
    python bot.py
"""

import asyncio
import html
import logging
import os
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    PicklePersistence,
)
from telegram.request import HTTPXRequest

from questions import QUESTIONS

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
)
log = logging.getLogger("trainer")

TIER_EMOJI = {"S": "🟥", "A": "🟧", "B": "🟦", "C": "🟩"}
TIER_NAME = {"S": "первый приоритет", "A": "высокий", "B": "средний", "C": "низкий"}


# ---------- per-user state helpers ----------

def ud(context: ContextTypes.DEFAULT_TYPE) -> dict:
    d = context.user_data
    d.setdefault("known", [])          # list of int indices
    d.setdefault("tiers", {"S": True, "A": True, "B": True, "C": True})
    d.setdefault("err_only", False)
    d.setdefault("shuffle", False)
    d.setdefault("order", [])
    d.setdefault("pos", 0)
    return d


def rebuild_order(d: dict) -> None:
    order = [i for i, q in enumerate(QUESTIONS)
             if d["tiers"].get(q["t"]) and (not d["err_only"] or q["err"])]
    if d["shuffle"]:
        random.shuffle(order)
    d["order"] = order
    d["pos"] = 0


def current_index(d: dict):
    if not d["order"]:
        return None
    if d["pos"] >= len(d["order"]):
        d["pos"] = 0
    return d["order"][d["pos"]]


# ---------- rendering ----------

def card_text(d: dict, qi: int, revealed: bool) -> str:
    q = QUESTIONS[qi]
    known = qi in d["known"]
    total = len(d["order"])
    head = f"{TIER_EMOJI[q['t']]} <b>{q['t']}</b> · {html.escape(q['topic'])}"
    flags = []
    if q["err"]:
        flags.append("‼️ была ошибка")
    if known:
        flags.append("✓ знаю")
    if flags:
        head += "  <i>(" + ", ".join(flags) + ")</i>"
    pos = f"{d['pos'] + 1}/{total}" if total else "0/0"
    known_n = len(set(d["known"]))
    text = f"{head}\n<code>{pos}</code> · выучено: {known_n}/{len(QUESTIONS)}\n\n"
    text += f"❓ <b>{html.escape(q['q'])}</b>"
    if revealed:
        text += f"\n\n💬 {html.escape(q['a'])}"
        if q.get("note"):
            text += f"\n\n⚠️ <i>{html.escape(q['note'])}</i>"
    return text


def card_kb(revealed: bool) -> InlineKeyboardMarkup:
    if not revealed:
        rows = [[InlineKeyboardButton("👁 Показать ответ", callback_data="rev")],
                [InlineKeyboardButton("⬅️", callback_data="pv"),
                 InlineKeyboardButton("⚙️ Фильтры", callback_data="menu"),
                 InlineKeyboardButton("➡️", callback_data="nx")]]
    else:
        rows = [[InlineKeyboardButton("✅ Знаю", callback_data="kn"),
                 InlineKeyboardButton("🔁 Повторить", callback_data="ag")],
                [InlineKeyboardButton("⬅️", callback_data="pv"),
                 InlineKeyboardButton("➡️ Дальше", callback_data="nx")]]
    return InlineKeyboardMarkup(rows)


def menu_kb(d: dict) -> InlineKeyboardMarkup:
    def mark(on):
        return "✅" if on else "▫️"
    rows = [
        [InlineKeyboardButton(f"{mark(d['tiers']['S'])} S — первый приоритет", callback_data="ftS")],
        [InlineKeyboardButton(f"{mark(d['tiers']['A'])} A — высокий", callback_data="ftA")],
        [InlineKeyboardButton(f"{mark(d['tiers']['B'])} B — средний", callback_data="ftB")],
        [InlineKeyboardButton(f"{mark(d['tiers']['C'])} C — низкий", callback_data="ftC")],
        [InlineKeyboardButton(f"{mark(d['err_only'])} ‼️ Только ошибки", callback_data="fte")],
        [InlineKeyboardButton(f"{mark(d['shuffle'])} 🔀 Перемешать", callback_data="fsh")],
        [InlineKeyboardButton("▶️ К карточкам", callback_data="go")],
    ]
    return InlineKeyboardMarkup(rows)


async def show_card(update_or_q, context, edit: bool):
    d = ud(context)
    qi = current_index(d)
    if qi is None:
        text = "Под выбранные фильтры нет вопросов 🤷\nОткрой ⚙️ Фильтры и включи хотя бы один приоритет."
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Фильтры", callback_data="menu")]])
    else:
        context.user_data["_revealed"] = False
        text = card_text(d, qi, revealed=False)
        kb = card_kb(revealed=False)
    if edit:
        await update_or_q.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update_or_q.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


# ---------- handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    log.info("/start from id=%s username=%s name=%s", u.id, u.username, u.full_name)
    d = ud(context)
    if not d["order"]:
        rebuild_order(d)
    await update.message.reply_text(
        "🎙️ <b>Java Interview — диалог-тренажёр</b>\n\n"
        "Читаешь вопрос → отвечаешь вслух → жмёшь «Показать ответ» и сверяешься.\n"
        "Отмечай <b>✅ Знаю</b> или <b>🔁 Повторить</b>. Прогресс сохраняется.\n\n"
        "Команды: /card — карточка · /menu — фильтры · /stats — прогресс · /reset — сброс",
        parse_mode=ParseMode.HTML,
    )
    await show_card(update, context, edit=False)


async def card_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ud(context)
    if not d["order"]:
        rebuild_order(d)
    await show_card(update, context, edit=False)


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ud(context)
    await update.message.reply_text("⚙️ <b>Фильтры</b>", parse_mode=ParseMode.HTML, reply_markup=menu_kb(d))


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ud(context)
    known = set(d["known"])
    by_tier = {}
    for i, q in enumerate(QUESTIONS):
        t = q["t"]
        tot, kn = by_tier.get(t, (0, 0))
        by_tier[t] = (tot + 1, kn + (1 if i in known else 0))
    lines = [f"📊 <b>Прогресс:</b> {len(known)}/{len(QUESTIONS)} выучено\n"]
    for t in ("S", "A", "B", "C"):
        if t in by_tier:
            tot, kn = by_tier[t]
            lines.append(f"{TIER_EMOJI[t]} {t}: {kn}/{tot}")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ud(context)
    d["known"] = []
    rebuild_order(d)
    await update.message.reply_text("Прогресс сброшен ✅")
    await show_card(update, context, edit=False)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = ud(context)
    data = q.data
    log.info("button '%s' from id=%s", data, update.effective_user.id)

    if data == "menu":
        await q.edit_message_text("⚙️ <b>Фильтры</b>", parse_mode=ParseMode.HTML, reply_markup=menu_kb(d))
        return
    if data == "go":
        if not d["order"]:
            rebuild_order(d)
        await show_card(q, context, edit=True)
        return
    if data.startswith("ft") and data[2:] in ("S", "A", "B", "C"):
        t = data[2:]
        d["tiers"][t] = not d["tiers"][t]
        rebuild_order(d)
        await q.edit_message_reply_markup(reply_markup=menu_kb(d))
        return
    if data == "fte":
        d["err_only"] = not d["err_only"]
        rebuild_order(d)
        await q.edit_message_reply_markup(reply_markup=menu_kb(d))
        return
    if data == "fsh":
        d["shuffle"] = not d["shuffle"]
        rebuild_order(d)
        await q.edit_message_reply_markup(reply_markup=menu_kb(d))
        return

    qi = current_index(d)
    if qi is None:
        await show_card(q, context, edit=True)
        return

    if data == "rev":
        context.user_data["_revealed"] = True
        await q.edit_message_text(card_text(d, qi, revealed=True),
                                  parse_mode=ParseMode.HTML, reply_markup=card_kb(revealed=True))
        return
    if data == "kn":
        if qi not in d["known"]:
            d["known"].append(qi)
        d["pos"] = (d["pos"] + 1) % len(d["order"])
        await show_card(q, context, edit=True)
        return
    if data == "ag":
        if qi in d["known"]:
            d["known"].remove(qi)
        d["pos"] = (d["pos"] + 1) % len(d["order"])
        await show_card(q, context, edit=True)
        return
    if data == "nx":
        d["pos"] = (d["pos"] + 1) % len(d["order"])
        await show_card(q, context, edit=True)
        return
    if data == "pv":
        d["pos"] = (d["pos"] - 1) % len(d["order"])
        await show_card(q, context, edit=True)
        return


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN env var (token from @BotFather).")

    persistence = PicklePersistence(filepath=os.environ.get("BOT_STATE_FILE", "bot_state.pickle"))

    # Generous timeouts: api.telegram.org can be very slow / throttled on some networks.
    t = float(os.environ.get("TG_TIMEOUT", "60"))
    req = HTTPXRequest(connect_timeout=t, read_timeout=t, write_timeout=t, pool_timeout=t)
    poll_req = HTTPXRequest(connect_timeout=t, read_timeout=t + 30, write_timeout=t, pool_timeout=t)
    app = (
        Application.builder()
        .token(token)
        .request(req)
        .get_updates_request(poll_req)
        .persistence(persistence)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("card", card_cmd))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CallbackQueryHandler(on_button))

    # Python 3.14+ no longer auto-creates an event loop on the main thread.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    # Webhook mode on hosting (Render sets RENDER_EXTERNAL_URL + PORT); polling locally.
    base = os.environ.get("WEBHOOK_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    port = int(os.environ.get("PORT", "0"))
    if base and port:
        path = os.environ.get("WEBHOOK_PATH", "tg-webhook")
        secret = os.environ.get("WEBHOOK_SECRET")  # optional, alnum + _- only
        log.info("Starting WEBHOOK on :%s path=/%s base=%s", port, path, base)
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=path,
            webhook_url=base.rstrip("/") + "/" + path,
            secret_token=secret,
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        print("Bot started (long polling). Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
