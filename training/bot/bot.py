# -*- coding: utf-8 -*-
"""Telegram-бот: диалог-тренажёр для подготовки к Java-собеседованию.

Режим: вопрос → 3–5 вариантов ответа → сравнение с правильным → разбор.
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
BTN_LABEL_MAX = 60


# ---------- quiz options ----------

def short_label(text: str, max_len: int = BTN_LABEL_MAX) -> str:
    text = " ".join(text.split())
    for sep in (". ", "; ", " — ", " - ", ", "):
        chunk = text.split(sep, 1)[0]
        if sep.strip():
            chunk += sep.rstrip()
        if 12 <= len(chunk) <= max_len:
            return chunk
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def build_quiz_options(qi: int) -> tuple[list[str], int]:
    """Return 3–5 shuffled option labels; index of the correct one."""
    q = QUESTIONS[qi]
    correct_full = q["a"]
    correct_label = short_label(correct_full)

    ranked: list[tuple[int, str, str]] = []
    for i, other in enumerate(QUESTIONS):
        if i == qi:
            continue
        score = 0
        if other["topic"] == q["topic"]:
            score += 2
        if other["t"] == q["t"]:
            score += 1
        ranked.append((score, other["a"], short_label(other["a"])))

    ranked.sort(key=lambda x: (-x[0], x[2]))
    n_wrong = random.randint(2, 4)
    wrong: list[str] = []
    seen = {correct_full.strip().lower(), correct_label.strip().lower()}
    for _, full, label in ranked:
        key = full.strip().lower()
        if key in seen or label.strip().lower() in seen:
            continue
        wrong.append(label)
        seen.add(key)
        seen.add(label.strip().lower())
        if len(wrong) >= n_wrong:
            break

    while len(wrong) < 2:
        filler = f"Другой ответ по теме «{q['topic']}»"
        if filler not in wrong:
            wrong.append(filler)

    options = wrong + [correct_label]
    random.shuffle(options)
    return options, options.index(correct_label)


def prepare_quiz(d: dict, qi: int) -> None:
    opts, correct = build_quiz_options(qi)
    d["_options"] = opts
    d["_correct_idx"] = correct
    d["_answered"] = False
    d["_picked"] = None


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

def card_header(d: dict, qi: int) -> str:
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
    return f"{head}\n<code>{pos}</code> · выучено: {known_n}/{len(QUESTIONS)}\n\n"


def quiz_question_text(d: dict, qi: int) -> str:
    q = QUESTIONS[qi]
    text = card_header(d, qi)
    text += f"❓ <b>{html.escape(q['q'])}</b>\n\n"
    text += "Выбери один из вариантов:"
    return text


def quiz_result_text(d: dict, qi: int, picked_idx: int) -> str:
    q = QUESTIONS[qi]
    correct_idx = d["_correct_idx"]
    ok = picked_idx == correct_idx
    text = card_header(d, qi)
    text += f"❓ <b>{html.escape(q['q'])}</b>\n\n"
    if ok:
        text += "✅ <b>Верно!</b>\n"
    else:
        text += "❌ <b>Неверно.</b>\n"
        text += f"Твой выбор: <i>{html.escape(d['_options'][picked_idx])}</i>\n"
        text += f"Правильный вариант: <b>{html.escape(d['_options'][correct_idx])}</b>\n"
    text += f"\n📖 <b>Разбор:</b>\n{html.escape(q['a'])}"
    if q.get("note"):
        text += f"\n\n⚠️ <i>{html.escape(q['note'])}</i>"
    return text


def quiz_options_kb(d: dict) -> InlineKeyboardMarkup:
    rows = []
    for i, opt in enumerate(d["_options"]):
        letter = chr(65 + i)
        label = f"{letter}. {opt}"
        if len(label) > BTN_LABEL_MAX:
            label = label[: BTN_LABEL_MAX - 1] + "…"
        rows.append([InlineKeyboardButton(label, callback_data=f"ans{i}")])
    rows.append(
        [
            InlineKeyboardButton("⬅️", callback_data="pv"),
            InlineKeyboardButton("⚙️ Фильтры", callback_data="menu"),
            InlineKeyboardButton("➡️", callback_data="nx"),
        ]
    )
    return InlineKeyboardMarkup(rows)


def quiz_result_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Знаю", callback_data="kn"),
                InlineKeyboardButton("🔁 Ещё раз", callback_data="rp"),
            ],
            [InlineKeyboardButton("➡️ Следующий", callback_data="nx")],
        ]
    )


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
        prepare_quiz(d, qi)
        text = quiz_question_text(d, qi)
        kb = quiz_options_kb(d)
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
        "🎙️ <b>Java Interview — тренажёр с вариантами</b>\n\n"
        "На каждый вопрос — <b>3–5 вариантов</b> ответа. Выбираешь один → бот сравнивает "
        "с правильным и показывает <b>разбор</b>.\n"
        "Отмечай <b>✅ Знаю</b> или жми <b>🔁 Ещё раз</b>. Прогресс сохраняется.\n\n"
        "Команды: /card — вопрос · /menu — фильтры · /stats — прогресс · /reset — сброс",
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

    if data.startswith("ans") and data[3:].isdigit():
        if d.get("_answered"):
            return
        picked = int(data[3:])
        if picked < 0 or picked >= len(d.get("_options", [])):
            return
        d["_answered"] = True
        d["_picked"] = picked
        if picked != d["_correct_idx"] and qi in d["known"]:
            d["known"].remove(qi)
        await q.edit_message_text(
            quiz_result_text(d, qi, picked),
            parse_mode=ParseMode.HTML,
            reply_markup=quiz_result_kb(),
        )
        return
    if data == "rp":
        prepare_quiz(d, qi)
        await q.edit_message_text(
            quiz_question_text(d, qi),
            parse_mode=ParseMode.HTML,
            reply_markup=quiz_options_kb(d),
        )
        return
    if data == "kn":
        if qi not in d["known"]:
            d["known"].append(qi)
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
