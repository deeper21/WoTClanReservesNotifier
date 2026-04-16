"""
WoT Clan Reserves Telegram Bot

Notifies users when their World of Tanks clan activates reserves (boosts).
Supports English, Ukrainian, and Russian.
"""

import asyncio
import logging
import secrets
import time
from datetime import datetime, timezone

from aiohttp import web
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

import auth_server
import database as db
import wg_api
from config import (
    AUTH_CALLBACK_PATH,
    PORT,
    TELEGRAM_BOT_TOKEN,
    WG_API_REGIONS,
)
from i18n import detect_language, get_default_timezone, t
from reserve_monitor import monitor_loop

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ── Helpers ─────────────────────────────────────────────────────

def _get_lang(chat_id: int, user_lang_code: str | None = None) -> str:
    """Get stored language or detect from Telegram."""
    chat = db.get_chat(chat_id)
    if chat and chat.get("language"):
        return chat["language"]
    return detect_language(user_lang_code)


# Default UTC offsets per server region (reasonable defaults)
REGION_DEFAULT_OFFSETS = {
    "eu": 2,     # CET/CEST
    "na": -5,    # EST
    "asia": 8,   # SGT/CST
}

TIMEZONE_OPTIONS = [
    ("Europe/Kyiv", "Kyiv (UTC+2/+3)"),
    ("Europe/Moscow", "Moscow (UTC+3)"),
    ("Europe/Berlin", "Berlin (UTC+1/+2)"),
    ("Europe/London", "London (UTC+0/+1)"),
    ("America/New_York", "New York (UTC-5/-4)"),
    ("America/Chicago", "Chicago (UTC-6/-5)"),
    ("America/Denver", "Denver (UTC-7/-6)"),
    ("America/Los_Angeles", "LA (UTC-8/-7)"),
    ("Asia/Singapore", "Singapore (UTC+8)"),
    ("Asia/Tokyo", "Tokyo (UTC+9)"),
    ("Australia/Sydney", "Sydney (UTC+10/+11)"),
    ("Pacific/Auckland", "Auckland (UTC+12/+13)"),
]


def _timezone_keyboard() -> InlineKeyboardMarkup:
    """Build timezone selection keyboard with common cities."""
    rows = []
    for i in range(0, len(TIMEZONE_OPTIONS), 2):
        row = []
        for tz_id, label in TIMEZONE_OPTIONS[i:i + 2]:
            row.append(InlineKeyboardButton(label, callback_data=f"tz:{tz_id}"))
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def _server_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"{info['name']} ({code.upper()})", callback_data=f"server:{code}")]
        for code, info in WG_API_REGIONS.items()
    ]
    return InlineKeyboardMarkup(buttons)


def _language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("English 🇬🇧", callback_data="lang:en")],
            [InlineKeyboardButton("Українська 🇺🇦", callback_data="lang:uk")],
            [InlineKeyboardButton("Русский 🇷🇺", callback_data="lang:ru")],
        ]
    )


# ── Command handlers ────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start – welcome message and server selection."""
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_lang = user.language_code if user else None
    is_group = update.effective_chat.type in ("group", "supergroup")

    lang = detect_language(user_lang)
    default_tz = get_default_timezone(lang)
    db.upsert_chat(chat_id, language=lang, is_active=1, timezone_name=default_tz)

    if is_group:
        await update.message.reply_text(
            t(lang, "group_welcome"), parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            t(lang, "welcome"), parse_mode=ParseMode.HTML
        )

    await update.message.reply_text(
        t(lang, "select_server"),
        reply_markup=_server_keyboard(),
        parse_mode=ParseMode.HTML,
    )


async def cmd_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /login – send Wargaming auth link."""
    chat_id = update.effective_chat.id
    lang = _get_lang(chat_id, update.effective_user.language_code if update.effective_user else None)
    chat = db.get_chat(chat_id)

    if not chat or not chat.get("region"):
        await update.message.reply_text(
            t(lang, "select_server"),
            reply_markup=_server_keyboard(),
            parse_mode=ParseMode.HTML,
        )
        return

    region = chat["region"]

    # Warn if already logged in
    if chat.get("nickname") and chat.get("access_token"):
        await update.message.reply_text(
            t(lang, "already_logged_in", nickname=chat["nickname"]),
            parse_mode=ParseMode.HTML,
        )

    # Generate state token and save
    state = secrets.token_urlsafe(32)
    db.save_auth_state(state, chat_id)

    try:
        login_url = await wg_api.get_login_url(region, state)
    except RuntimeError as e:
        logger.error("Failed to get login URL: %s", e)
        await update.message.reply_text(
            t(lang, "api_error"), parse_mode=ParseMode.HTML
        )
        return

    # Show privacy notice before login
    await update.message.reply_text(
        t(lang, "privacy_notice"), parse_mode=ParseMode.HTML
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(t(lang, "login_button"), url=login_url)]]
    )
    await update.message.reply_text(
        t(lang, "login_prompt"),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )

    # Schedule a 5-minute timeout check
    context.job_queue.run_once(
        _login_timeout_check,
        when=300,
        data={"chat_id": chat_id, "state": state},
        name=f"login_timeout_{chat_id}",
    )


async def _login_timeout_check(context: ContextTypes.DEFAULT_TYPE):
    """Check if user completed login within 5 minutes."""
    data = context.job.data
    chat_id = data["chat_id"]
    state = data["state"]

    # If the state still exists, the user didn't complete login
    remaining_chat_id = db.pop_auth_state(state)
    if remaining_chat_id is not None:
        chat = db.get_chat(chat_id)
        # Only warn if user still has no valid token
        if not chat or not chat.get("access_token") or chat["token_expires"] < int(time.time()):
            lang = chat["language"] if chat else "en"
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=t(lang, "login_timeout"),
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                logger.error("Failed to send timeout message: %s", e)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = _get_lang(chat_id, update.effective_user.language_code if update.effective_user else None)
    await update.message.reply_text(t(lang, "help"), parse_mode=ParseMode.HTML)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = _get_lang(chat_id, update.effective_user.language_code if update.effective_user else None)
    chat = db.get_chat(chat_id)

    if not chat or not chat.get("access_token"):
        monitoring = t(lang, "monitoring_inactive")
        nickname = "—"
        token_expires = "—"
        server = chat.get("region", "—").upper() if chat else "—"
    else:
        now = int(time.time())
        is_valid = chat["token_expires"] > now
        monitoring = t(lang, "monitoring_active") if is_valid else t(lang, "monitoring_inactive")
        nickname = chat.get("nickname", "—")
        from zoneinfo import ZoneInfo
        tz_name = chat.get("timezone_name") or "UTC"
        try:
            tz = ZoneInfo(tz_name)
        except (KeyError, Exception):
            tz = timezone.utc
        dt = datetime.fromtimestamp(chat["token_expires"], tz=tz)
        token_expires = dt.strftime(f"%Y-%m-%d %H:%M %Z")
        server = chat.get("region", "—").upper()

    await update.message.reply_text(
        t(lang, "status", server=server, nickname=nickname, token_expires=token_expires, monitoring=monitoring),
        parse_mode=ParseMode.HTML,
    )


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = _get_lang(chat_id, update.effective_user.language_code if update.effective_user else None)
    await update.message.reply_text(
        t(lang, "select_language"),
        reply_markup=_language_keyboard(),
        parse_mode=ParseMode.HTML,
    )


async def cmd_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = _get_lang(chat_id, update.effective_user.language_code if update.effective_user else None)
    await update.message.reply_text(
        t(lang, "select_server"),
        reply_markup=_server_keyboard(),
        parse_mode=ParseMode.HTML,
    )


async def cmd_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = _get_lang(chat_id, update.effective_user.language_code if update.effective_user else None)
    logger.info("Timezone command from chat %s", chat_id)
    try:
        await update.message.reply_text(
            t(lang, "select_timezone"),
            reply_markup=_timezone_keyboard(),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error("Failed to send timezone keyboard: %s", e)


# Rate limit: track last /reserves call per chat
_reserves_cooldown: dict[int, float] = {}
RESERVES_COOLDOWN_SECONDS = 30


async def cmd_reserves(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually check and display current clan reserves."""
    chat_id = update.effective_chat.id
    lang = _get_lang(chat_id, update.effective_user.language_code if update.effective_user else None)
    chat = db.get_chat(chat_id)

    if not chat or not chat.get("access_token"):
        await update.message.reply_text(
            t(lang, "login_required"), parse_mode=ParseMode.HTML
        )
        return

    # Rate limit check
    now = time.time()
    last_call = _reserves_cooldown.get(chat_id, 0)
    if now - last_call < RESERVES_COOLDOWN_SECONDS:
        remaining = int(RESERVES_COOLDOWN_SECONDS - (now - last_call))
        await update.message.reply_text(
            t(lang, "reserves_cooldown", seconds=remaining),
            parse_mode=ParseMode.HTML,
        )
        return
    _reserves_cooldown[chat_id] = now

    # Check token validity
    if chat["token_expires"] <= int(now):
        await update.message.reply_text(
            t(lang, "token_expired"), parse_mode=ParseMode.HTML
        )
        return

    try:
        active_reserves = await wg_api.get_clan_reserves(chat["region"], chat["access_token"])
    except RuntimeError as e:
        logger.warning("Manual reserves check failed for chat %s: %s", chat_id, e)
        await update.message.reply_text(
            t(lang, "api_error"), parse_mode=ParseMode.HTML
        )
        return

    if not active_reserves:
        await update.message.reply_text(
            t(lang, "no_active_reserves"), parse_mode=ParseMode.HTML
        )
        return

    tz_name = chat.get("timezone_name") or "UTC"
    from reserve_monitor import _format_time
    lines = []
    for reserve in active_reserves:
        lines.append(
            t(
                lang,
                "reserve_activated",
                reserve_name=reserve.reserve_name,
                level=reserve.level,
                start_time=_format_time(reserve.activated_at, tz_name),
                end_time=_format_time(reserve.active_till, tz_name),
            )
        )
    await update.message.reply_text(
        "\n".join(lines), parse_mode=ParseMode.HTML
    )


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = _get_lang(chat_id, update.effective_user.language_code if update.effective_user else None)
    db.deactivate_chat(chat_id)
    await update.message.reply_text(t(lang, "stopped"), parse_mode=ParseMode.HTML)


async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete all stored data for this chat and confirm."""
    chat_id = update.effective_chat.id
    lang = _get_lang(chat_id, update.effective_user.language_code if update.effective_user else None)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(t(lang, "delete_confirm_yes"), callback_data="delete:yes"),
                InlineKeyboardButton(t(lang, "delete_confirm_no"), callback_data="delete:no"),
            ]
        ]
    )
    await update.message.reply_text(
        t(lang, "delete_confirm"), reply_markup=keyboard, parse_mode=ParseMode.HTML
    )


# ── Callback query handlers ─────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    data = query.data

    if data.startswith("server:"):
        region = data.split(":", 1)[1]
        region_name = WG_API_REGIONS[region]["name"]
        lang = _get_lang(chat_id)
        # Refine timezone: language-based tz takes priority, region is fallback
        chat_data = db.get_chat(chat_id)
        current_tz = chat_data.get("timezone_name") if chat_data else None
        # If current timezone is still a generic region-based one or unset, update it
        from i18n import LANGUAGE_TIMEZONE_MAP, REGION_TIMEZONE_MAP
        lang_tz = LANGUAGE_TIMEZONE_MAP.get(lang)
        if lang_tz:
            tz_to_set = lang_tz  # language-specific always wins
        else:
            tz_to_set = REGION_TIMEZONE_MAP.get(region, "UTC")
        db.upsert_chat(chat_id, region=region, timezone_name=tz_to_set)

        await query.edit_message_text(
            t(lang, "server_selected", server_name=f"{region_name} ({region.upper()})"),
            parse_mode=ParseMode.HTML,
        )

        # Auto-prompt login
        state = secrets.token_urlsafe(32)
        db.save_auth_state(state, chat_id)
        try:
            login_url = await wg_api.get_login_url(region, state)

            # Show privacy notice before login
            await query.message.reply_text(
                t(lang, "privacy_notice"), parse_mode=ParseMode.HTML
            )

            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(t(lang, "login_button"), url=login_url)]]
            )
            await query.message.reply_text(
                t(lang, "login_prompt"),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )

            # Schedule timeout
            context.job_queue.run_once(
                _login_timeout_check,
                when=300,
                data={"chat_id": chat_id, "state": state},
                name=f"login_timeout_{chat_id}",
            )
        except RuntimeError as e:
            logger.error("Failed to get login URL: %s", e)
            await query.message.reply_text(
                t(lang, "api_error"), parse_mode=ParseMode.HTML
            )

    elif data.startswith("lang:"):
        new_lang = data.split(":", 1)[1]
        # Update timezone to match new language
        chat_data = db.get_chat(chat_id)
        region = chat_data.get("region") if chat_data else None
        new_tz = get_default_timezone(new_lang, region)
        db.upsert_chat(chat_id, language=new_lang, timezone_name=new_tz)
        await query.edit_message_text(
            t(new_lang, "language_changed"),
            parse_mode=ParseMode.HTML,
        )

    elif data.startswith("tz:"):
        tz_id = data.split(":", 1)[1]
        db.upsert_chat(chat_id, timezone_name=tz_id)
        lang = _get_lang(chat_id)
        # Get a friendly label
        tz_label = tz_id
        for opt_id, opt_label in TIMEZONE_OPTIONS:
            if opt_id == tz_id:
                tz_label = opt_label
                break
        await query.edit_message_text(
            t(lang, "timezone_changed", timezone=tz_label),
            parse_mode=ParseMode.HTML,
        )

    elif data.startswith("delete:"):
        choice = data.split(":", 1)[1]
        lang = _get_lang(chat_id)
        if choice == "yes":
            db.delete_chat(chat_id)
            logger.info("Chat %s deleted all their data", chat_id)
            await query.edit_message_text(
                t(lang, "data_deleted"), parse_mode=ParseMode.HTML
            )
        else:
            await query.edit_message_text(
                t(lang, "delete_cancelled"), parse_mode=ParseMode.HTML
            )


# ── Application setup ───────────────────────────────────────────

async def run_web_server(bot: Bot):
    """Start the aiohttp web server for auth callbacks."""
    auth_server.set_bot(bot)
    app = auth_server.create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("Auth callback server started on port %d", PORT)
    return runner


def main():
    """Entry point."""
    db.init_db()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("login", cmd_login))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("language", cmd_language))
    application.add_handler(CommandHandler("server", cmd_server))
    application.add_handler(CommandHandler("timezone", cmd_timezone))
    application.add_handler(CommandHandler("reserves", cmd_reserves))
    application.add_handler(CommandHandler("delete", cmd_delete))
    application.add_handler(CommandHandler("stop", cmd_stop))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Global error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error("Unhandled exception: %s", context.error, exc_info=context.error)

    application.add_error_handler(error_handler)

    # Post-init: start web server and reserve monitor
    async def post_init(app: Application):
        bot = app.bot
        app.bot_data["web_runner"] = await run_web_server(bot)
        asyncio.create_task(monitor_loop(bot))

    async def post_shutdown(app: Application):
        runner = app.bot_data.get("web_runner")
        if runner:
            await runner.cleanup()

    application.post_init = post_init
    application.post_shutdown = post_shutdown

    logger.info("Bot starting...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
