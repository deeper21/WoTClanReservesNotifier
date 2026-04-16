"""Background task that polls Wargaming API for active clan reserves."""

import asyncio
import logging
import time
from datetime import datetime, timezone

from telegram import Bot
from telegram.constants import ParseMode

import database as db
import wg_api
from config import POLL_INTERVAL
from i18n import t

logger = logging.getLogger(__name__)


def _format_time(unix_ts: int, timezone_name: str = "UTC") -> str:
    """Format a unix timestamp into a human-readable string with user's timezone.
    Uses IANA timezone names for automatic DST handling."""
    from zoneinfo import ZoneInfo
    try:
        tz = ZoneInfo(timezone_name)
    except (KeyError, Exception):
        tz = timezone.utc
    dt = datetime.fromtimestamp(unix_ts, tz=tz)
    # Show timezone abbreviation (e.g., EET, EEST, MSK, CET, EST)
    tz_abbr = dt.strftime("%Z")
    return dt.strftime(f"%Y-%m-%d %H:%M {tz_abbr}")


async def _check_chat_reserves(bot: Bot, chat: dict):
    """Check one chat's clan reserves and send notifications for new ones."""
    chat_id = chat["chat_id"]
    lang = chat["language"]
    region = chat["region"]
    access_token = chat["access_token"]
    tz_name = chat.get("timezone_name") or "UTC"

    try:
        active_reserves = await wg_api.get_clan_reserves(region, access_token)
    except RuntimeError as e:
        logger.warning("API error for chat %s: %s", chat_id, e)
        return

    for reserve in active_reserves:
        # Unique key: type + level + active_till to avoid re-notifying
        reserve_key = f"{reserve.reserve_type}:{reserve.level}:{reserve.active_till}"

        if db.was_reserve_notified(chat_id, reserve_key):
            continue

        # New active reserve – send notification
        msg = t(
            lang,
            "reserve_activated",
            reserve_name=reserve.reserve_name,
            level=reserve.level,
            start_time=_format_time(reserve.activated_at, tz_name),
            end_time=_format_time(reserve.active_till, tz_name),
        )

        try:
            await bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)
            db.mark_reserve_notified(chat_id, reserve_key)
            logger.info("Notified chat %s about reserve %s", chat_id, reserve_key)
        except Exception as e:
            logger.error("Failed to send notification to chat %s: %s", chat_id, e)


async def _check_token_expiry(bot: Bot):
    """Warn users whose tokens are about to expire or have expired."""
    # Expiring soon
    for chat in db.get_chats_with_expiring_tokens():
        lang = chat["language"]
        try:
            await bot.send_message(
                chat_id=chat["chat_id"],
                text=t(lang, "token_expiring_soon"),
                parse_mode=ParseMode.HTML,
            )
            db.upsert_chat(chat["chat_id"], token_warning_sent=1)
        except Exception as e:
            logger.error("Failed to send token warning to %s: %s", chat["chat_id"], e)

    # Already expired
    for chat in db.get_chats_with_expired_tokens():
        lang = chat["language"]
        try:
            await bot.send_message(
                chat_id=chat["chat_id"],
                text=t(lang, "token_expired"),
                parse_mode=ParseMode.HTML,
            )
            db.upsert_chat(chat["chat_id"], access_token=None)
        except Exception as e:
            logger.error("Failed to send expiry notice to %s: %s", chat["chat_id"], e)


async def monitor_loop(bot: Bot):
    """Main polling loop – runs forever."""
    logger.info("Reserve monitor started (interval: %ds)", POLL_INTERVAL)

    while True:
        try:
            # Cleanup old data
            db.cleanup_old_auth_states()
            db.cleanup_old_notifications()

            # Check token expiry
            await _check_token_expiry(bot)

            # Check reserves for all active chats
            active_chats = db.get_active_chats()
            logger.debug("Checking reserves for %d active chats", len(active_chats))

            # Process chats concurrently but with some limit
            semaphore = asyncio.Semaphore(10)

            async def _check_with_limit(chat):
                async with semaphore:
                    await _check_chat_reserves(bot, chat)

            await asyncio.gather(*[_check_with_limit(c) for c in active_chats])

        except Exception:
            logger.exception("Error in monitor loop")

        await asyncio.sleep(POLL_INTERVAL)
