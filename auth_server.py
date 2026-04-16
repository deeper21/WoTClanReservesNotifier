"""Lightweight HTTP server to handle Wargaming OAuth callback."""

import logging

from aiohttp import web

import database as db

logger = logging.getLogger(__name__)

# This will be set by bot.py at startup
_bot = None
_app_bot = None


def set_bot(bot):
    global _bot, _app_bot
    _bot = bot
    _app_bot = bot


async def handle_auth_callback(request: web.Request) -> web.Response:
    """
    Wargaming redirects here after login:
      /auth/callback?status=ok&access_token=...&nickname=...&account_id=...&expires_at=...&state=...
    """
    status = request.query.get("status")
    state = request.query.get("state")

    if not state:
        return web.Response(text="Missing state parameter.", status=400)

    chat_id = db.pop_auth_state(state)
    if not chat_id:
        return web.Response(
            text="Session expired or invalid. Please use /login in the bot again.",
            status=400,
            content_type="text/html",
        )

    if status != "ok":
        error_msg = request.query.get("message", "Unknown error")
        logger.warning("Auth failed for chat %s: %s", chat_id, error_msg)

        chat = db.get_chat(chat_id)
        lang = chat["language"] if chat else "en"

        if _bot:
            from i18n import t
            from telegram.constants import ParseMode

            try:
                await _bot.send_message(
                    chat_id=chat_id,
                    text=t(lang, "login_failed"),
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                logger.error("Failed to send login failure message: %s", e)

        return web.Response(
            text="<html><body><h2>Login failed</h2><p>You can close this window and try again in the bot.</p></body></html>",
            content_type="text/html",
        )

    # Successful auth
    access_token = request.query.get("access_token")
    nickname = request.query.get("nickname")
    account_id = request.query.get("account_id")
    expires_at = request.query.get("expires_at")

    if not all([access_token, nickname, account_id, expires_at]):
        return web.Response(text="Missing parameters in callback.", status=400)

    account_id = int(account_id)
    expires_at = int(expires_at)

    chat = db.get_chat(chat_id)
    lang = chat["language"] if chat else "en"
    region = chat["region"] if chat else "eu"

    # Fetch clan_id from account info
    clan_id = None
    try:
        from wg_api import get_account_info

        account_info = await get_account_info(region, access_token, account_id)
        if account_info:
            clan_id = account_info.get("clan_id")
    except Exception as e:
        logger.warning("Failed to fetch account info: %s", e)

    # Save to database
    db.upsert_chat(
        chat_id,
        access_token=access_token,
        nickname=nickname,
        account_id=account_id,
        token_expires=expires_at,
        clan_id=clan_id,
        is_active=1,
        token_warning_sent=0,
    )

    # Send success message to the bot chat
    if _bot:
        from i18n import t
        from telegram.constants import ParseMode

        try:
            await _bot.send_message(
                chat_id=chat_id,
                text=t(lang, "login_success", nickname=nickname),
                parse_mode=ParseMode.HTML,
            )

            # Warn if not in a clan
            if not clan_id:
                await _bot.send_message(
                    chat_id=chat_id,
                    text=t(lang, "not_in_clan"),
                    parse_mode=ParseMode.HTML,
                )
        except Exception as e:
            logger.error("Failed to send success message: %s", e)

    return web.Response(
        text=(
            "<html><body>"
            f"<h2>Welcome, {nickname}!</h2>"
            "<p>Login successful! You can close this window and return to Telegram.</p>"
            "</body></html>"
        ),
        content_type="text/html",
    )


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/auth/callback", handle_auth_callback)
    # Health check for Railway
    app.router.add_get("/health", lambda _: web.Response(text="ok"))
    return app
