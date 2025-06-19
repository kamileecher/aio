from bot import Config

from bot.helpers.translations import lang
from bot.helpers.tidal_func.events import checkLoginTidal
from bot.helpers.database.postgres_impl import users_db, admins_db, chats_db, user_settings, set_db

allowed_chats: set[int] = set()
allowed_users: set[int] = set()
admins: set[int] = set()

# NOOB WAY TO HANDLE BOTH ENV AND DB XD

async def get_chats(return_msg=False):
    database_chats = chats_db.get_chats() or []
    allowed_chats.update(Config.AUTH_CHAT)
    allowed_chats.update(chat[0] for chat in database_chats if chat and chat[0])

    database_admins = admins_db.get_admins() or []
    admins.update(Config.ADMINS)
    admins.update(admin[0] for admin in database_admins if admin and admin[0])

    if Config.IS_BOT_PUBLIC != "True":
        database_users = users_db.get_users() or []
        if Config.AUTH_USERS:
            allowed_users.update(Config.AUTH_USERS)
        allowed_users.update(user[0] for user in database_users if user and user[0])

    if return_msg:
        msg = "<b>ALLOWED CHATS</b>"
        for chat in sorted(allowed_chats):
            msg += f"\n<code>{chat}</code>"

        msg += "\n\n<b>ALLOWED USERS</b>"
        if Config.IS_BOT_PUBLIC == "True":
            msg += "\nAllowed For Everyone"
        else:
            for user in sorted(allowed_users):
                msg += f"\n<code>{user}</code>"

        msg += "\n\n<b>ADMINS</b>"
        for admin in sorted(admins):
            msg += f"\n<code>{admin}</code>"

        return msg

async def check_id(id=None, message=None, restricted=False):
    all_list = allowed_chats | allowed_users | admins
    if restricted:
        if id in admins:
            return True
        else:
            return False
    else:
        # Seperating Group and PM
        if message.from_user.id != message.chat.id:
            id = message.chat.id
        else:
            id = message.from_user.id

        if Config.ANIT_SPAM_MODE == "True":
            check = user_settings.get_var(id, "ON_TASK")      
            if check:
                await message.reply_text(lang.select.ANTI_SPAM_WAIT)
                return False          

        if Config.IS_BOT_PUBLIC == "True":
            return True
        elif id in all_list:
            return True
        else:
            return False

async def checkLogins(provider):
    # return Error and Error Message
    if provider == "tidal":
        auth, msg = await checkLoginTidal()
        if auth:
            return False, msg
        else:
            return True, msg
    elif provider == "qobuz":
        auth, _ = set_db.get_variable("QOBUZ_AUTH")
        if not auth:
            return True, lang.select.QOBUZ_NOT_AUTH
        return False, None
    elif provider == "deezer":
        auth, _ = set_db.get_variable("DEEZER_AUTH")
        if not auth:
            return True, lang.select.DEEZER_NOT_AUTH
        return False, None
    elif provider == "kkbox":
        auth, _ = set_db.get_variable("KKBOX_AUTH")
        if not auth:
            return True, lang.select.KKBOX_NOT_AUTH
        return False, None
    elif provider == "spotify":
        auth, _ = set_db.get_variable("SPOTIFY_AUTH")
        if not auth:
            return True, lang.select.SPOTIFY_NOT_AUTH
        return False, None
    else:
        pass