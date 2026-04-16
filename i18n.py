"""Internationalization – English, Ukrainian, Russian translations."""

TRANSLATIONS = {
    "en": {
        "welcome": (
            "👋 Welcome to WoT Clan Reserves Bot!\n\n"
            "I'll notify you when your clan activates reserves (boosts).\n\n"
            "Let's get started — please select your server."
        ),
        "select_server": "🌍 Select your server:",
        "server_selected": "✅ Server set to <b>{server_name}</b>.\n\nNow please log in with your Wargaming account.",
        "login_prompt": "🔑 Click the button below to log in via Wargaming:",
        "login_button": "Log in via Wargaming",
        "login_success": (
            "✅ Login successful!\n\n"
            "Welcome, <b>{nickname}</b>!\n"
            "I'll now monitor your clan's reserves and notify you when one is activated.\n\n"
            "Use /help to see available commands."
        ),
        "login_failed": "❌ Login failed or timed out. Please try again with /login.",
        "login_timeout": (
            "⏰ No login detected in 5 minutes.\n"
            "Please use /login to authenticate with your Wargaming account."
        ),
        "token_expired": (
            "⚠️ Your Wargaming access token has expired.\n"
            "Please use /login to re-authenticate and continue receiving notifications."
        ),
        "token_expiring_soon": (
            "⚠️ Your Wargaming access token expires in less than 24 hours.\n"
            "Use /login to refresh your session."
        ),
        "reserve_activated": (
            "🚀 <b>Clan Reserve Activated!</b>\n\n"
            "📦 <b>{reserve_name}</b> (Level {level})\n"
            "⏱ Start: {start_time}\n"
            "⏳ End: {end_time}\n"
        ),
        "no_active_reserves": "No active clan reserves at the moment.",
        "reserves_cooldown": "⏳ Please wait {seconds}s before checking again.",
        "login_required": "🔑 You need to log in first. Use /login.",
        "delete_confirm": (
            "⚠️ <b>Are you sure you want to delete all your data?</b>\n\n"
            "This will permanently remove your Wargaming account link, "
            "access token, and all settings. This cannot be undone."
        ),
        "delete_confirm_yes": "Yes, delete everything",
        "delete_confirm_no": "Cancel",
        "data_deleted": "✅ All your data has been permanently deleted. Use /start to set up again.",
        "delete_cancelled": "👌 Deletion cancelled. Your data is unchanged.",
        "privacy_notice": (
            "🔒 <b>Privacy notice</b>\n\n"
            "By logging in, this bot will store:\n"
            "• Your Wargaming nickname and account ID\n"
            "• An encrypted access token to check clan reserves\n"
            "• Your Telegram chat ID, language, and timezone\n\n"
            "Your token is encrypted at rest and is only used to read "
            "clan reserve status. You can delete all your data at any time "
            "with /delete."
        ),
        "not_in_clan": "⚠️ Your account doesn't appear to be in a clan. Join a clan to receive reserve notifications.",
        "help": (
            "📋 <b>Available commands:</b>\n\n"
            "/start — Start the bot / reset setup\n"
            "/login — Log in with Wargaming account\n"
            "/reserves — Check active clan reserves now\n"
            "/status — Show current monitoring status\n"
            "/language — Change notification language\n"
            "/server — Change game server\n"
            "/timezone — Change your timezone\n"
            "/stop — Stop notifications\n"
            "/delete — Delete all your stored data\n"
            "/help — Show this help message"
        ),
        "status": (
            "📊 <b>Status</b>\n\n"
            "🌍 Server: {server}\n"
            "👤 Account: {nickname}\n"
            "🔑 Token valid until: {token_expires}\n"
            "📡 Monitoring: {monitoring}"
        ),
        "monitoring_active": "Active ✅",
        "monitoring_inactive": "Inactive ❌",
        "stopped": "🛑 Notifications stopped. Use /start to set up again.",
        "select_language": "🌐 Select notification language:",
        "language_changed": "✅ Language changed to English.",
        "already_logged_in": "You are already logged in as <b>{nickname}</b>. Logging in again will replace your current session.",
        "select_timezone": "🕐 Select your timezone:",
        "timezone_changed": "✅ Timezone set to {timezone}.",
        "api_error": "⚠️ Error communicating with Wargaming API. Will retry shortly.",
        "group_welcome": (
            "👋 Hello! I'm the WoT Clan Reserves Bot.\n\n"
            "To set me up in this group, an admin needs to:\n"
            "1. Use /server to select the game server\n"
            "2. Use /login to authenticate with a Wargaming account\n\n"
            "I'll then notify this chat about clan reserve activations."
        ),
    },
    "uk": {
        "welcome": (
            "👋 Ласкаво просимо до бота кланових резервів WoT!\n\n"
            "Я повідомлятиму вас, коли ваш клан активує резерви (бусти).\n\n"
            "Давайте почнемо — оберіть свій сервер."
        ),
        "select_server": "🌍 Оберіть сервер:",
        "server_selected": "✅ Сервер встановлено: <b>{server_name}</b>.\n\nТепер увійдіть через акаунт Wargaming.",
        "login_prompt": "🔑 Натисніть кнопку нижче для входу через Wargaming:",
        "login_button": "Увійти через Wargaming",
        "login_success": (
            "✅ Вхід успішний!\n\n"
            "Вітаємо, <b>{nickname}</b>!\n"
            "Я тепер відстежуватиму резерви вашого клану та повідомлятиму про їх активацію.\n\n"
            "Використовуйте /help для перегляду доступних команд."
        ),
        "login_failed": "❌ Вхід не вдався або час очікування вичерпано. Спробуйте ще раз: /login.",
        "login_timeout": (
            "⏰ Вхід не виявлено протягом 5 хвилин.\n"
            "Використовуйте /login для автентифікації через Wargaming."
        ),
        "token_expired": (
            "⚠️ Ваш токен доступу Wargaming закінчився.\n"
            "Використовуйте /login для повторної автентифікації."
        ),
        "token_expiring_soon": (
            "⚠️ Ваш токен доступу Wargaming закінчиться менш ніж за 24 години.\n"
            "Використовуйте /login для оновлення сесії."
        ),
        "reserve_activated": (
            "🚀 <b>Клановий резерв активовано!</b>\n\n"
            "📦 <b>{reserve_name}</b> (Рівень {level})\n"
            "⏱ Початок: {start_time}\n"
            "⏳ Кінець: {end_time}\n"
        ),
        "no_active_reserves": "Наразі немає активних кланових резервів.",
        "reserves_cooldown": "⏳ Зачекайте {seconds}с перед наступною перевіркою.",
        "login_required": "🔑 Спочатку потрібно увійти. Використовуйте /login.",
        "delete_confirm": (
            "⚠️ <b>Ви впевнені, що хочете видалити всі свої дані?</b>\n\n"
            "Це назавжди видалить прив'язку акаунту Wargaming, "
            "токен доступу та всі налаштування. Це неможливо скасувати."
        ),
        "delete_confirm_yes": "Так, видалити все",
        "delete_confirm_no": "Скасувати",
        "data_deleted": "✅ Всі ваші дані видалено назавжди. Використовуйте /start для повторного налаштування.",
        "delete_cancelled": "👌 Видалення скасовано. Ваші дані не змінено.",
        "privacy_notice": (
            "🔒 <b>Повідомлення про конфіденційність</b>\n\n"
            "Після входу бот зберігатиме:\n"
            "• Ваш нікнейм та ID акаунту Wargaming\n"
            "• Зашифрований токен доступу для перевірки резервів клану\n"
            "• ID чату Telegram, мову та часовий пояс\n\n"
            "Токен зашифрований та використовується лише для перевірки "
            "статусу кланових резервів. Ви можете видалити всі свої дані "
            "в будь-який момент командою /delete."
        ),
        "not_in_clan": "⚠️ Ваш акаунт не належить до клану. Вступіть до клану, щоб отримувати сповіщення.",
        "help": (
            "📋 <b>Доступні команди:</b>\n\n"
            "/start — Запустити бота / скинути налаштування\n"
            "/login — Увійти через акаунт Wargaming\n"
            "/reserves — Перевірити активні резерви зараз\n"
            "/status — Показати поточний статус\n"
            "/language — Змінити мову сповіщень\n"
            "/server — Змінити ігровий сервер\n"
            "/timezone — Змінити часовий пояс\n"
            "/stop — Зупинити сповіщення\n"
            "/delete — Видалити всі збережені дані\n"
            "/help — Показати цю довідку"
        ),
        "status": (
            "📊 <b>Статус</b>\n\n"
            "🌍 Сервер: {server}\n"
            "👤 Акаунт: {nickname}\n"
            "🔑 Токен дійсний до: {token_expires}\n"
            "📡 Моніторинг: {monitoring}"
        ),
        "monitoring_active": "Активний ✅",
        "monitoring_inactive": "Неактивний ❌",
        "stopped": "🛑 Сповіщення зупинено. Використовуйте /start для повторного налаштування.",
        "select_language": "🌐 Оберіть мову сповіщень:",
        "language_changed": "✅ Мову змінено на українську.",
        "already_logged_in": "Ви вже увійшли як <b>{nickname}</b>. Повторний вхід замінить поточну сесію.",
        "select_timezone": "🕐 Оберіть часовий пояс:",
        "timezone_changed": "✅ Часовий пояс встановлено: {timezone}.",
        "api_error": "⚠️ Помилка зв'язку з API Wargaming. Спробую ще раз.",
        "group_welcome": (
            "👋 Привіт! Я бот кланових резервів WoT.\n\n"
            "Для налаштування в цій групі адміністратор повинен:\n"
            "1. Використати /server для вибору серверу\n"
            "2. Використати /login для автентифікації\n\n"
            "Потім я повідомлятиму цей чат про активацію резервів."
        ),
    },
    "ru": {
        "welcome": (
            "👋 Добро пожаловать в бот клановых резервов WoT!\n\n"
            "Я буду уведомлять вас, когда ваш клан активирует резервы (бусты).\n\n"
            "Давайте начнём — выберите свой сервер."
        ),
        "select_server": "🌍 Выберите сервер:",
        "server_selected": "✅ Сервер установлен: <b>{server_name}</b>.\n\nТеперь войдите через аккаунт Wargaming.",
        "login_prompt": "🔑 Нажмите кнопку ниже для входа через Wargaming:",
        "login_button": "Войти через Wargaming",
        "login_success": (
            "✅ Вход успешен!\n\n"
            "Добро пожаловать, <b>{nickname}</b>!\n"
            "Я буду отслеживать резервы вашего клана и уведомлять об их активации.\n\n"
            "Используйте /help для просмотра доступных команд."
        ),
        "login_failed": "❌ Вход не удался или истекло время ожидания. Попробуйте снова: /login.",
        "login_timeout": (
            "⏰ Вход не обнаружен в течение 5 минут.\n"
            "Используйте /login для аутентификации через Wargaming."
        ),
        "token_expired": (
            "⚠️ Ваш токен доступа Wargaming истёк.\n"
            "Используйте /login для повторной аутентификации."
        ),
        "token_expiring_soon": (
            "⚠️ Ваш токен доступа Wargaming истекает менее чем через 24 часа.\n"
            "Используйте /login для обновления сессии."
        ),
        "reserve_activated": (
            "🚀 <b>Клановый резерв активирован!</b>\n\n"
            "📦 <b>{reserve_name}</b> (Уровень {level})\n"
            "⏱ Начало: {start_time}\n"
            "⏳ Конец: {end_time}\n"
        ),
        "no_active_reserves": "На данный момент нет активных клановых резервов.",
        "reserves_cooldown": "⏳ Подождите {seconds}с перед следующей проверкой.",
        "login_required": "🔑 Сначала нужно войти. Используйте /login.",
        "delete_confirm": (
            "⚠️ <b>Вы уверены, что хотите удалить все свои данные?</b>\n\n"
            "Это навсегда удалит привязку аккаунта Wargaming, "
            "токен доступа и все настройки. Это невозможно отменить."
        ),
        "delete_confirm_yes": "Да, удалить всё",
        "delete_confirm_no": "Отмена",
        "data_deleted": "✅ Все ваши данные удалены навсегда. Используйте /start для повторной настройки.",
        "delete_cancelled": "👌 Удаление отменено. Ваши данные не изменены.",
        "privacy_notice": (
            "🔒 <b>Уведомление о конфиденциальности</b>\n\n"
            "После входа бот будет хранить:\n"
            "• Ваш никнейм и ID аккаунта Wargaming\n"
            "• Зашифрованный токен доступа для проверки резервов клана\n"
            "• ID чата Telegram, язык и часовой пояс\n\n"
            "Токен зашифрован и используется только для проверки "
            "статуса клановых резервов. Вы можете удалить все свои данные "
            "в любой момент командой /delete."
        ),
        "not_in_clan": "⚠️ Ваш аккаунт не состоит в клане. Вступите в клан для получения уведомлений.",
        "help": (
            "📋 <b>Доступные команды:</b>\n\n"
            "/start — Запустить бота / сбросить настройки\n"
            "/login — Войти через аккаунт Wargaming\n"
            "/reserves — Проверить активные резервы сейчас\n"
            "/status — Показать текущий статус\n"
            "/language — Изменить язык уведомлений\n"
            "/server — Изменить игровой сервер\n"
            "/timezone — Изменить часовой пояс\n"
            "/stop — Остановить уведомления\n"
            "/delete — Удалить все сохранённые данные\n"
            "/help — Показать эту справку"
        ),
        "status": (
            "📊 <b>Статус</b>\n\n"
            "🌍 Сервер: {server}\n"
            "👤 Аккаунт: {nickname}\n"
            "🔑 Токен действителен до: {token_expires}\n"
            "📡 Мониторинг: {monitoring}"
        ),
        "monitoring_active": "Активен ✅",
        "monitoring_inactive": "Неактивен ❌",
        "stopped": "🛑 Уведомления остановлены. Используйте /start для повторной настройки.",
        "select_language": "🌐 Выберите язык уведомлений:",
        "language_changed": "✅ Язык изменён на русский.",
        "already_logged_in": "Вы уже вошли как <b>{nickname}</b>. Повторный вход заменит текущую сессию.",
        "select_timezone": "🕐 Выберите часовой пояс:",
        "timezone_changed": "✅ Часовой пояс установлен: {timezone}.",
        "api_error": "⚠️ Ошибка связи с API Wargaming. Попробую ещё раз.",
        "group_welcome": (
            "👋 Привет! Я бот клановых резервов WoT.\n\n"
            "Для настройки в этой группе администратор должен:\n"
            "1. Использовать /server для выбора сервера\n"
            "2. Использовать /login для аутентификации\n\n"
            "Затем я буду уведомлять этот чат об активации резервов."
        ),
    },
}

# Map Telegram language codes to our supported languages
LANGUAGE_CODE_MAP = {
    "uk": "uk",
    "ru": "ru",
    "be": "ru",  # Belarusian -> Russian
    "kk": "ru",  # Kazakh -> Russian
}


def detect_language(telegram_language_code: str | None) -> str:
    """Detect bot language from Telegram user's interface language."""
    if not telegram_language_code:
        return "en"
    code = telegram_language_code.lower().split("-")[0]
    return LANGUAGE_CODE_MAP.get(code, "en")


# Map detected language to most likely IANA timezone
LANGUAGE_TIMEZONE_MAP = {
    "uk": "Europe/Kyiv",      # Ukraine → EET/EEST (UTC+2/+3)
    "ru": "Europe/Kyiv",     # Russian-speaking on EU → same timezone as Ukraine
    "en": None,               # English → use server-based default
}

# Fallback: server region to IANA timezone (for English users)
REGION_TIMEZONE_MAP = {
    "eu": "Europe/Berlin",    # CET/CEST (UTC+1/+2)
    "na": "America/New_York", # EST/EDT (UTC-5/-4)
    "asia": "Asia/Singapore", # SGT (UTC+8)
}


def get_default_timezone(lang: str, region: str | None = None) -> str:
    """Get the best default IANA timezone based on language and region."""
    tz = LANGUAGE_TIMEZONE_MAP.get(lang)
    if tz:
        return tz
    if region:
        return REGION_TIMEZONE_MAP.get(region, "UTC")
    return "UTC"


def t(lang: str, key: str, **kwargs) -> str:
    """Get translated string with optional formatting."""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text
