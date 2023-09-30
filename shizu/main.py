# █ █ █ █▄▀ ▄▀█ █▀▄▀█ █▀█ █▀█ █ █
# █▀█ █ █ █ █▀█ █ ▀ █ █▄█ █▀▄ █▄█

# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# 👤 https://t.me/hikamoru

import contextlib
import logging
import time

from pyrogram.methods.utilities.idle import idle

from . import auth, database, loader, utils
from .bot import core


async def main():
    """Main function"""
    me, app = await auth.Auth().authorize()
    await app.initialize()
    db = database.db
    modules = loader.ModulesManager(app, db, me)

    await modules.load(app)

    with contextlib.suppress(Exception):
        app.inline_bot = core.bot
    me = db.get("shizu.me", "me", None)

    if not me:
        id_ = (await app.get_me()).id
        db.set("shizu.me", "me", id_)
        
    g_commit_last = db.get("shizu.updater", "commit_last", None)
    if not g_commit_last:
        db.set("shizu.updater", "commit_last", str(utils.get_git_hash()))

    if restart := db.get("shizu.updater", "restart"):
        if restart["type"] == "restart":
            restarted_text = (
                f"<emoji id=5017470156276761427>🔄</emoji> <b>The reboot was successful!</b>\n<emoji id=5451646226975955576>⌛️</emoji> The reboot took <code>{round(time.time())-int(restart['start'])}</code> seconds"
            )
        else:
            restarted_text = (
                f"<emoji id=5258420634785947640>🔄</emoji> <b>The update was successful!</b>\n<emoji id=5451646226975955576>⌛️</emoji> The update took <code>{round(time.time())-int(restart['start'])}</code> seconds"
            )

        try:
            await app.edit_message_text(restart["chat"], restart["id"], restarted_text)
        except Exception:
            await app.inline_bot.send_message(
                app.db.get("shizu.me", "me", None),
                "🔄 The reboot was successful!\n"
                f'⌛️ The reboot took <code>{round(time.time())-int(restart["start"])}</code> seconds'
                "\n\nℹ️ <b>Userbot couldn't edit that message due to an error thats why I am sending it to you instead :)</b>",
                parse_mode="HTML",
            )
        logging.info("Successfully started!")
        db.pop("shizu.updater", "restart")

    await idle()

    logging.info("Shizu is shutting down...")
    return True
