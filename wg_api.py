"""Wargaming API client for authentication and clan reserves."""

import logging
import time
from dataclasses import dataclass

import aiohttp

from config import WG_APPLICATION_ID, WG_API_REGIONS, AUTH_CALLBACK_URL, WG_TOKEN_MAX_LIFETIME

logger = logging.getLogger(__name__)


def _base_url(region: str) -> str:
    return WG_API_REGIONS[region]["api"]


@dataclass
class AuthResult:
    login_url: str


@dataclass
class ActiveReserve:
    reserve_type: str
    reserve_name: str
    level: int
    active_till: int  # unix timestamp
    activated_at: int  # unix timestamp (computed: active_till - action_time)
    bonus_type: str | None = None


async def get_login_url(region: str, state: str) -> str:
    """
    Call /wot/auth/login/ to get a Wargaming login URL.
    Returns the URL to redirect the user to.
    """
    url = f"{_base_url(region)}/wot/auth/login/"
    params = {
        "application_id": WG_APPLICATION_ID,
        "redirect_uri": f"{AUTH_CALLBACK_URL}?state={state}",
        "nofollow": "1",
        "expires_at": str(WG_TOKEN_MAX_LIFETIME),
        "display": "page",
    }

    logger.info("WG auth request: url=%s, redirect_uri=%s", url, params["redirect_uri"])

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as resp:
            raw_text = await resp.text()
            logger.info("WG auth response [%s]: %s", resp.status, raw_text)
            data = await resp.json(content_type=None) if raw_text else {}

    if data.get("status") != "ok":
        error = data.get("error", {})
        logger.error("WG auth login FAILED: %s | full response: %s", error, data)
        raise RuntimeError(f"WG auth login error: {error}")

    return data["data"]["location"]


async def prolongate_token(region: str, access_token: str) -> dict:
    """Extend the token lifetime. Returns new token info."""
    url = f"{_base_url(region)}/wot/auth/prolongate/"
    params = {
        "application_id": WG_APPLICATION_ID,
        "access_token": access_token,
        "expires_at": str(WG_TOKEN_MAX_LIFETIME),
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as resp:
            data = await resp.json()

    if data.get("status") != "ok":
        raise RuntimeError(f"WG token prolongate error: {data.get('error')}")

    return data["data"]


async def get_account_info(region: str, access_token: str, account_id: int) -> dict | None:
    """Get account info including clan_id."""
    url = f"{_base_url(region)}/wot/account/info/"
    params = {
        "application_id": WG_APPLICATION_ID,
        "access_token": access_token,
        "account_id": str(account_id),
        "fields": "clan_id,nickname",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()

    if data.get("status") != "ok":
        logger.warning("Failed to get account info: %s", data.get("error"))
        return None

    return data["data"].get(str(account_id))


async def get_clan_reserves(region: str, access_token: str) -> list[ActiveReserve]:
    """
    Fetch clan reserves and return only currently active ones.
    Endpoint: /wot/stronghold/clanreserves/
    """
    url = f"{_base_url(region)}/wot/stronghold/clanreserves/"
    params = {
        "application_id": WG_APPLICATION_ID,
        "access_token": access_token,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()

    if data.get("status") != "ok":
        error = data.get("error", {})
        logger.warning("Failed to get clan reserves: %s", error)
        raise RuntimeError(f"Clan reserves API error: {error}")

    now = int(time.time())
    active = []

    # The API returns a list of reserve type objects
    reserves_data = data.get("data")
    if not reserves_data:
        return active

    # reserves_data can be a list of reserve type dicts
    if isinstance(reserves_data, list):
        reserves_list = reserves_data
    elif isinstance(reserves_data, dict):
        # Sometimes the data is keyed differently
        reserves_list = list(reserves_data.values()) if reserves_data else []
    else:
        return active

    for reserve in reserves_list:
        if not isinstance(reserve, dict):
            continue

        reserve_type = reserve.get("type", reserve.get("bonus_type", "unknown"))
        reserve_name = reserve.get("name", reserve_type)

        # Check if this reserve type has an active instance
        active_till = reserve.get("active_till")
        action_time = reserve.get("action_time", 7200)  # default 2h

        if active_till and active_till > now:
            activated_at = active_till - action_time
            active.append(
                ActiveReserve(
                    reserve_type=str(reserve_type),
                    reserve_name=reserve_name,
                    level=reserve.get("level", 0),
                    active_till=active_till,
                    activated_at=activated_at,
                    bonus_type=reserve.get("bonus_type"),
                )
            )
            continue

        # Some API versions nest active reserves in 'in_stock' list
        in_stock = reserve.get("in_stock", [])
        if isinstance(in_stock, list):
            for item in in_stock:
                if not isinstance(item, dict):
                    continue
                item_active_till = item.get("active_till")
                item_action_time = item.get("action_time", action_time)
                if item_active_till and item_active_till > now:
                    activated_at = item_active_till - item_action_time
                    active.append(
                        ActiveReserve(
                            reserve_type=str(reserve_type),
                            reserve_name=reserve_name,
                            level=item.get("level", reserve.get("level", 0)),
                            active_till=item_active_till,
                            activated_at=activated_at,
                            bonus_type=item.get("bonus_type", reserve.get("bonus_type")),
                        )
                    )

    return active
