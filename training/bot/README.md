# 🤖 Telegram-бот — диалог-тренажёр

Бот для подготовки к Java-собеседованию в режиме «вопрос → ответ».
Вопросы лежат в `questions.py` (те же, что в `../dialog-trainer.md` и `../index.html`).

## 1. Получить токен
1. В Telegram открой [@BotFather](https://t.me/BotFather).
2. `/newbot` → задай имя и username (должен заканчиваться на `bot`).
3. BotFather пришлёт токен вида `123456789:AA....` — скопируй.

## 2. Запуск локально (быстрая проверка с телефона)

Windows PowerShell:
```powershell
cd C:\PREPARE_TO_INTERVIEW\JAVA_AI_ANALYTICS\training\bot
python -m pip install -r requirements.txt
$env:TELEGRAM_BOT_TOKEN="ВСТАВЬ_ТОКЕН"
python bot.py
```

Пока скрипт запущен на ПК — пиши боту `/start` с телефона, он отвечает.
Закрыл скрипт — бот «уснул». Для режима 24/7 см. деплой ниже.

## 3. Команды бота
- `/start` — приветствие + первая карточка
- `/card` — следующая карточка
- `/menu` — фильтры (приоритеты S/A/B/C, только ошибки, перемешать)
- `/stats` — прогресс по уровням
- `/reset` — сбросить прогресс

В карточке: 👁 Показать ответ → ✅ Знаю / 🔁 Повторить / ➡️ Дальше.
Прогресс сохраняется в `bot_state.pickle`.

## 4. Деплой на Render (24/7, бесплатно-ish)
Бот работает на long polling — публичный URL не нужен, подходит тип **Background Worker**.
Конфиг лежит в `render.yaml` (корень репозитория). После пуша репозитория на GitHub:
1. Render → New → Blueprint → выбрать репозиторий.
2. В переменных окружения задать `TELEGRAM_BOT_TOKEN` (sync: false).
3. Deploy. Бот поднимется и будет отвечать всегда.
