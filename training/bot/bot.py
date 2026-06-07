# -*- coding: utf-8 -*-
"""Telegram-бот: тренажёр Java-собеседования с вариантами ответов.

Режим: вопрос → 3–5 вариантов → сравнение → разбор.
Консоль (отвечено/не отвечено), статистика, фильтры S/A/B/C.
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
BTN_LABEL_MAX = 60
CONSOLE_PAGE = 12


def has_options(q: dict) -> bool:
    return bool(q.get("correct")) and len(q.get("wrong") or []) >= 2


def ud(context: ContextTypes.DEFAULT_TYPE) -> dict:
    d = context.user_data
    d.setdefault("known", [])
    d.setdefault("attempted", [])
    d.setdefault("stats", {})  # qi -> {tries, correct}
    d.setdefault("tiers", {"S": True, "A": True, "B": True, "C": True})
    d.setdefault("err_only", False)
    d.setdefault("shuffle", False)
    d.setdefault("order", [])
    d.setdefault("pos", 0)
    d.setdefault("console_page", 0)
    return d


def filtered_indices(d: dict) -> list[int]:
    return [
        i
        for i, q in enumerate(QUESTIONS)
        if d["tiers"].get(q["t"])
        and (not d["err_only"] or q["err"])
        and has_options(q)
    ]


def rebuild_order(d: dict, unanswered_only: bool = True) -> None:
    order = filtered_indices(d)
    if unanswered_only:
        attempted = set(d["attempted"])
        order = [i for i in order if i not in attempted]
    if d["shuffle"]:
        random.shuffle(order)
    d["order"] = order
    if d["pos"] >= len(order):
        d["pos"] = max(0, len(order) - 1) if order else 0


def current_index(d: dict):
    if not d["order"] or d["pos"] >= len(d["order"]):
        return None
    return d["order"][d["pos"]]


def has_next(d: dict) -> bool:
    return d["pos"] + 1 < len(d["order"])


def record_attempt(d: dict, qi: int, ok: bool) -> None:
    if qi not in d["attempted"]:
        d["attempted"].append(qi)
    st = d["stats"].setdefault(str(qi), {"tries": 0, "correct": 0})
    st["tries"] += 1
    if ok:
        st["correct"] += 1


def build_quiz_options(qi: int) -> tuple[list[str], int]:
    q = QUESTIONS[qi]
    wrong = list(q["wrong"])
    random.shuffle(wrong)
    n_wrong = random.randint(2, min(4, len(wrong)))
    opts = wrong[:n_wrong] + [q["correct"]]
    random.shuffle(opts)
    return opts, opts.index(q["correct"])


def prepare_quiz(d: dict, qi: int) -> bool:
    if not has_options(QUESTIONS[qi]):
        return False
    opts, correct = build_quiz_options(qi)
    d["_options"] = opts
    d["_correct_idx"] = correct
    d["_answered"] = False
    d["_picked"] = None
    return True


# ---------- rendering ----------

def card_header(d: dict, qi: int) -> str:
    q = QUESTIONS[qi]
    known = qi in d["known"]
    attempted = qi in d["attempted"]
    total = len(d["order"])
    head = f"{TIER_EMOJI[q['t']]} <b>{q['t']}</b> · {html.escape(q['topic'])}"
    flags = []
    if q["err"]:
        flags.append("‼️ ошибка на собесе")
    if known:
        flags.append("✓ знаю")
    elif attempted:
        flags.append("◐ пробовал")
    if flags:
        head += "  <i>(" + ", ".join(flags) + ")</i>"
    pos = f"{d['pos'] + 1}/{total}" if total else "0/0"
    filt = filtered_indices(d)
    ans_n = len([i for i in filt if i in d["attempted"]])
    return (
        f"{head}\n<code>{pos}</code> · в очереди · "
        f"отвечено {ans_n}/{len(filt)} · знаю {len(set(d['known']) & set(filt))}/{len(filt)}\n\n"
    )


def quiz_question_text(d: dict, qi: int) -> str:
    q = QUESTIONS[qi]
    return card_header(d, qi) + f"❓ <b>{html.escape(q['q'])}</b>\n\nВыбери один из вариантов:"


def quiz_result_text(d: dict, qi: int, picked_idx: int) -> str:
    q = QUESTIONS[qi]
    correct_idx = d["_correct_idx"]
    ok = picked_idx == correct_idx
    text = card_header(d, qi) + f"❓ <b>{html.escape(q['q'])}</b>\n\n"
    if ok:
        text += "✅ <b>Верно!</b>\n"
    else:
        text += "❌ <b>Неверно.</b>\n"
        text += f"Твой выбор: <i>{html.escape(d['_options'][picked_idx])}</i>\n"
        text += f"Правильно: <b>{html.escape(d['_options'][correct_idx])}</b>\n"
    text += f"\n📖 <b>Разбор:</b>\n{html.escape(q['a'])}"
    if q.get("note"):
        text += f"\n\n⚠️ <i>{html.escape(q['note'])}</i>"
    return text


def done_text(d: dict) -> str:
    filt = filtered_indices(d)
    ans = [i for i in filt if i in d["attempted"]]
    pending = [i for i in filt if i not in d["attempted"]]
    return (
        "🎉 <b>Очередь пройдена!</b>\n\n"
        f"Отвечено: <b>{len(ans)}</b> · осталось: <b>{len(pending)}</b> · "
        f"знаю: <b>{len(set(d['known']) & set(filt))}</b>\n\n"
        "Открой 📋 <b>Консоль</b> — список всех вопросов.\n"
        "📊 <b>Статистика</b> — точность по темам.\n"
        "Сброс очереди: /reset или включи «🔁 Повторять отвеченные» в фильтрах."
    )


def hub_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("▶️ Вопрос", callback_data="go")],
            [
                InlineKeyboardButton("📋 Консоль", callback_data="tab:console"),
                InlineKeyboardButton("📊 Статистика", callback_data="tab:stats"),
            ],
            [InlineKeyboardButton("⚙️ Фильтры", callback_data="menu")],
        ]
    )


def quiz_options_kb(d: dict) -> InlineKeyboardMarkup:
    rows = []
    for i, opt in enumerate(d["_options"]):
        letter = chr(65 + i)
        label = f"{letter}. {opt}"
        if len(label) > BTN_LABEL_MAX:
            label = label[: BTN_LABEL_MAX - 1] + "…"
        rows.append([InlineKeyboardButton(label, callback_data=f"ans{i}")])
    nav = [InlineKeyboardButton("⬅️", callback_data="pv")]
    if has_next(d):
        nav.append(InlineKeyboardButton("➡️", callback_data="nx"))
    nav.append(InlineKeyboardButton("🏠", callback_data="hub"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("📋 Консоль", callback_data="tab:console")])
    return InlineKeyboardMarkup(rows)


def quiz_result_kb(d: dict) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("✅ Знаю", callback_data="kn"),
            InlineKeyboardButton("🔁 Ещё раз", callback_data="rp"),
        ]
    ]
    if has_next(d):
        rows.append([InlineKeyboardButton("➡️ Следующий", callback_data="nx")])
    else:
        rows.append([InlineKeyboardButton("🏁 Готово", callback_data="done")])
    rows.append(
        [
            InlineKeyboardButton("📋 Консоль", callback_data="tab:console"),
            InlineKeyboardButton("📊 Статистика", callback_data="tab:stats"),
        ]
    )
    return InlineKeyboardMarkup(rows)


def menu_kb(d: dict) -> InlineKeyboardMarkup:
    def mark(on):
        return "✅" if on else "▫️"

    rows = [
        [InlineKeyboardButton(f"{mark(d['tiers']['S'])} S", callback_data="ftS")],
        [InlineKeyboardButton(f"{mark(d['tiers']['A'])} A", callback_data="ftA")],
        [InlineKeyboardButton(f"{mark(d['tiers']['B'])} B", callback_data="ftB")],
        [InlineKeyboardButton(f"{mark(d['tiers']['C'])} C", callback_data="ftC")],
        [InlineKeyboardButton(f"{mark(d['err_only'])} ‼️ Только ошибки", callback_data="fte")],
        [InlineKeyboardButton(f"{mark(d['shuffle'])} 🔀 Перемешать", callback_data="fsh")],
        [
            InlineKeyboardButton(
                f"{mark(d.get('repeat_answered', False))} 🔁 Повторять отвеченные",
                callback_data="frp",
            )
        ],
        [InlineKeyboardButton("▶️ К вопросам", callback_data="go")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="hub")],
    ]
    return InlineKeyboardMarkup(rows)


def console_text(d: dict, page: int) -> str:
    filt = filtered_indices(d)
    answered = [i for i in filt if i in d["attempted"]]
    pending = [i for i in filt if i not in d["attempted"]]
    lines = [
        "📋 <b>Консоль вопросов</b>",
        f"Всего по фильтру: <b>{len(filt)}</b>",
        f"✅ Отвечено: <b>{len(answered)}</b> · ⏳ Не отвечено: <b>{len(pending)}</b>",
        f"✓ Знаю: <b>{len(set(d['known']) & set(filt))}</b>\n",
    ]

    def line(i: int) -> str:
        q = QUESTIONS[i]
        if i in d["known"]:
            mark = "✓"
        elif i in d["attempted"]:
            mark = "◐"
        else:
            mark = "○"
        short = q["q"][:55] + ("…" if len(q["q"]) > 55 else "")
        return f"{mark} {TIER_EMOJI[q['t']]} {html.escape(short)}"

    show = pending if pending else answered
    title = "⏳ <b>Не отвечено:</b>" if pending else "✅ <b>Отвечено:</b>"
    lines.append(title)
    if not show:
        lines.append("<i>(пусто)</i>")
    else:
        start = page * CONSOLE_PAGE
        chunk = show[start : start + CONSOLE_PAGE]
        for i in chunk:
            lines.append(line(i))
        total_pages = max(1, (len(show) + CONSOLE_PAGE - 1) // CONSOLE_PAGE)
        lines.append(f"\n<i>Стр. {page + 1}/{total_pages}</i>")
    return "\n".join(lines)


def console_kb(d: dict, page: int) -> InlineKeyboardMarkup:
    filt = filtered_indices(d)
    pending = [i for i in filt if i not in d["attempted"]]
    show = pending if pending else [i for i in filt if i in d["attempted"]]
    total_pages = max(1, (len(show) + CONSOLE_PAGE - 1) // CONSOLE_PAGE)
    rows = []
    if page > 0:
        rows.append([InlineKeyboardButton("◀️ Назад", callback_data=f"con:{page - 1}")])
    if page + 1 < total_pages:
        rows.append([InlineKeyboardButton("▶️ Далее", callback_data=f"con:{page + 1}")])
    rows.append(
        [
            InlineKeyboardButton("▶️ Вопрос", callback_data="go"),
            InlineKeyboardButton("📊 Статистика", callback_data="tab:stats"),
        ]
    )
    rows.append([InlineKeyboardButton("🏠 Меню", callback_data="hub")])
    return InlineKeyboardMarkup(rows)


def stats_text(d: dict) -> str:
    filt = filtered_indices(d)
    known = set(d["known"]) & set(filt)
    attempted = set(d["attempted"]) & set(filt)
    lines = ["📊 <b>Статистика</b>\n"]

    total_tries = 0
    total_ok = 0
    by_tier: dict[str, tuple[int, int, int, int]] = {}
    by_topic: dict[str, tuple[int, int]] = {}

    for i in filt:
        q = QUESTIONS[i]
        t = q["t"]
        tot, kn, att, ok = by_tier.get(t, (0, 0, 0, 0))
        by_tier[t] = (tot + 1, kn + (1 if i in known else 0), att + (1 if i in attempted else 0), ok)
        st = d["stats"].get(str(i), {"tries": 0, "correct": 0})
        total_tries += st["tries"]
        total_ok += st["correct"]
        if st["tries"]:
            top_ok, top_t = by_topic.get(q["topic"], (0, 0))
            by_topic[q["topic"]] = (top_ok + st["correct"], top_t + st["tries"])

    acc = f"{100 * total_ok // total_tries}%" if total_tries else "—"
    lines.append(f"Охват: ответил на <b>{len(attempted)}</b>/{len(filt)}")
    lines.append(f"Знаю: <b>{len(known)}</b>/{len(filt)}")
    lines.append(f"Попыток: <b>{total_tries}</b> · точность: <b>{acc}</b>\n")
    lines.append("<b>По приоритету:</b>")
    for t in ("S", "A", "B", "C"):
        if t in by_tier:
            tot, kn, att, _ = by_tier[t]
            lines.append(f"{TIER_EMOJI[t]} {t}: знаю {kn}/{tot} · отвечено {att}/{tot}")

    if by_topic:
        lines.append("\n<b>Точность по темам</b> (где пробовал):")
        ranked = sorted(
            ((topic, ok, tr) for topic, (ok, tr) in by_topic.items() if tr),
            key=lambda x: x[1] / x[2],
        )
        for topic, ok, tr in ranked[:8]:
            pct = 100 * ok // tr
            lines.append(f"· {html.escape(topic)}: {pct}% ({ok}/{tr})")
    return "\n".join(lines)


def stats_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📋 Консоль", callback_data="tab:console"),
                InlineKeyboardButton("▶️ Вопрос", callback_data="go"),
            ],
            [InlineKeyboardButton("🏠 Меню", callback_data="hub")],
        ]
    )


async def show_card(update_or_q, context, edit: bool):
    d = ud(context)
    repeat = d.get("repeat_answered", False)
    rebuild_order(d, unanswered_only=not repeat)
    qi = current_index(d)

    if qi is None:
        text = done_text(d) if filtered_indices(d) else (
            "Под выбранные фильтры нет вопросов 🤷\nОткрой ⚙️ Фильтры."
        )
        kb = hub_kb()
    elif not prepare_quiz(d, qi):
        d["pos"] += 1
        if edit:
            await show_card(update_or_q, context, edit=True)
        else:
            await show_card(update_or_q, context, edit=False)
        return
    else:
        text = quiz_question_text(d, qi)
        kb = quiz_options_kb(d)

    if edit:
        await update_or_q.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update_or_q.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


async def show_console(q, context, page: int | None = None):
    d = ud(context)
    if page is not None:
        d["console_page"] = page
    p = d["console_page"]
    await q.edit_message_text(
        console_text(d, p), parse_mode=ParseMode.HTML, reply_markup=console_kb(d, p)
    )


async def show_stats(q, context):
    d = ud(context)
    await q.edit_message_text(stats_text(d), parse_mode=ParseMode.HTML, reply_markup=stats_kb())


async def show_hub(q, context):
    d = ud(context)
    filt = filtered_indices(d)
    pending = len([i for i in filt if i not in d["attempted"]])
    text = (
        "🎙️ <b>Java Interview Trainer</b>\n\n"
        f"В базе <b>{len(QUESTIONS)}</b> вопросов · по фильтру <b>{len(filt)}</b>\n"
        f"В очереди: <b>{pending}</b> неотвеченных\n\n"
        "▶️ Вопрос — тренировка\n"
        "📋 Консоль — список отвечено / не отвечено\n"
        "📊 Статистика — прогресс и точность"
    )
    await q.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=hub_kb())


# ---------- handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    log.info("/start from id=%s username=%s", u.id, u.username)
    d = ud(context)
    rebuild_order(d)
    filt = filtered_indices(d)
    pending = len([i for i in filt if i not in d["attempted"]])
    await update.message.reply_text(
        "🎙️ <b>Java Interview Trainer</b>\n\n"
        "На каждый вопрос — <b>3–5 вариантов</b>. После выбора — сравнение и <b>разбор</b>.\n"
        f"В очереди: <b>{pending}</b> вопросов.\n\n"
        "Команды: /card /console /stats /menu /reset",
        parse_mode=ParseMode.HTML,
        reply_markup=hub_kb(),
    )
    await show_card(update, context, edit=False)


async def card_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud(context)
    await show_card(update, context, edit=False)


async def console_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ud(context)
    d["console_page"] = 0
    await update.message.reply_text(
        console_text(d, 0), parse_mode=ParseMode.HTML, reply_markup=console_kb(d, 0)
    )


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ud(context)
    await update.message.reply_text("⚙️ <b>Фильтры</b>", parse_mode=ParseMode.HTML, reply_markup=menu_kb(d))


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ud(context)
    await update.message.reply_text(stats_text(d), parse_mode=ParseMode.HTML, reply_markup=stats_kb())


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ud(context)
    d["known"] = []
    d["attempted"] = []
    d["stats"] = {}
    d["pos"] = 0
    rebuild_order(d)
    await update.message.reply_text("Прогресс сброшен ✅", reply_markup=hub_kb())
    await show_card(update, context, edit=False)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = ud(context)
    data = q.data
    log.info("button '%s' from id=%s", data, update.effective_user.id)

    if data == "hub":
        await show_hub(q, context)
        return
    if data == "menu":
        await q.edit_message_text("⚙️ <b>Фильтры</b>", parse_mode=ParseMode.HTML, reply_markup=menu_kb(d))
        return
    if data == "tab:console":
        d["console_page"] = 0
        await show_console(q, context)
        return
    if data == "tab:stats":
        await show_stats(q, context)
        return
    if data.startswith("con:") and data[4:].isdigit():
        await show_console(q, context, page=int(data[4:]))
        return
    if data == "done":
        rebuild_order(d, unanswered_only=not d.get("repeat_answered", False))
        await q.edit_message_text(done_text(d), parse_mode=ParseMode.HTML, reply_markup=hub_kb())
        return
    if data == "go":
        await show_card(q, context, edit=True)
        return
    if data.startswith("ft") and data[2:] in ("S", "A", "B", "C"):
        d["tiers"][data[2:]] = not d["tiers"][data[2:]]
        rebuild_order(d, unanswered_only=not d.get("repeat_answered", False))
        await q.edit_message_reply_markup(reply_markup=menu_kb(d))
        return
    if data == "fte":
        d["err_only"] = not d["err_only"]
        rebuild_order(d, unanswered_only=not d.get("repeat_answered", False))
        await q.edit_message_reply_markup(reply_markup=menu_kb(d))
        return
    if data == "fsh":
        d["shuffle"] = not d["shuffle"]
        rebuild_order(d, unanswered_only=not d.get("repeat_answered", False))
        await q.edit_message_reply_markup(reply_markup=menu_kb(d))
        return
    if data == "frp":
        d["repeat_answered"] = not d.get("repeat_answered", False)
        rebuild_order(d, unanswered_only=not d["repeat_answered"])
        await q.edit_message_reply_markup(reply_markup=menu_kb(d))
        return

    qi = current_index(d)
    if qi is None:
        await q.edit_message_text(done_text(d), parse_mode=ParseMode.HTML, reply_markup=hub_kb())
        return

    if data.startswith("ans") and data[3:].isdigit():
        if d.get("_answered"):
            return
        picked = int(data[3:])
        if picked < 0 or picked >= len(d.get("_options", [])):
            return
        ok = picked == d["_correct_idx"]
        d["_answered"] = True
        d["_picked"] = picked
        record_attempt(d, qi, ok)
        if not ok and qi in d["known"]:
            d["known"].remove(qi)
        await q.edit_message_text(
            quiz_result_text(d, qi, picked),
            parse_mode=ParseMode.HTML,
            reply_markup=quiz_result_kb(d),
        )
        return
    if data == "rp":
        if not prepare_quiz(d, qi):
            await q.edit_message_text(done_text(d), parse_mode=ParseMode.HTML, reply_markup=hub_kb())
            return
        await q.edit_message_text(
            quiz_question_text(d, qi), parse_mode=ParseMode.HTML, reply_markup=quiz_options_kb(d)
        )
        return
    if data == "kn":
        if qi not in d["known"]:
            d["known"].append(qi)
        if has_next(d):
            d["pos"] += 1
            await show_card(q, context, edit=True)
        else:
            await q.edit_message_text(done_text(d), parse_mode=ParseMode.HTML, reply_markup=hub_kb())
        return
    if data == "nx":
        if not has_next(d):
            await q.edit_message_text(done_text(d), parse_mode=ParseMode.HTML, reply_markup=hub_kb())
            return
        d["pos"] += 1
        await show_card(q, context, edit=True)
        return
    if data == "pv":
        if d["pos"] > 0:
            d["pos"] -= 1
        await show_card(q, context, edit=True)
        return


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN env var (token from @BotFather).")

    persistence = PicklePersistence(filepath=os.environ.get("BOT_STATE_FILE", "bot_state.pickle"))
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
    app.add_handler(CommandHandler("console", console_cmd))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CallbackQueryHandler(on_button))

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    base = os.environ.get("WEBHOOK_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    port = int(os.environ.get("PORT", "0"))
    if base and port:
        path = os.environ.get("WEBHOOK_PATH", "tg-webhook")
        secret = os.environ.get("WEBHOOK_SECRET")
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
