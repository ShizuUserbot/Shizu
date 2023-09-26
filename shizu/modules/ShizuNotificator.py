# █ █ █ █▄▀ ▄▀█ █▀▄▀█ █▀█ █▀█ █ █
# █▀█ █ █ █ █▀█ █ ▀ █ █▄█ █▀▄ █▄█

# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# 👤 https://t.me/hikamoru

import git
import os
import time
import atexit
import sys
import logging
from .. import utils, loader, version
from pyrogram import Client
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


logger = logging.getLogger(__name__)

@loader.module("ShizuNotificator", "hikamoru")
class ShizuNotificator(loader.Module):
    """Notify about new commits in the repo by sending a message to the bot """
    
    strings = {
        'more': "<b>... and more {}</b>",
        'update_required': "📬 <b>Shizu Update available!</b>\n\nNew Shizu version released.\n🔮 <b>Shizu <s>{}</s> -> {}</b>",
        'updaing': "🔄 Updating...",
    }
    _notified = None
    
    def update_keyboard(self):
        markup = InlineKeyboardMarkup()
        upd = InlineKeyboardButton("🔄 Update", callback_data="update")
        markup.add(upd)
        return markup
    
    
    def get_changelog(self) -> str:
        try:
            repo = git.Repo()

            for remote in repo.remotes:
                remote.fetch()

            if not (
                diff := repo.git.log([f"HEAD..origin/{version.branch}", "--oneline"])
            ):
                return False
        except Exception:
            return False

        res = "\n".join(
            f"<b>{commit.split()[0]}</b>:"
            f" <i>{utils.escape_html(' '.join(commit.split()[1:]))}</i>"
            for commit in diff.splitlines()[:10]
        )

        if diff.count("\n") >= 10:
            res += self.strings["more"].format(len(diff.splitlines()) - 10)

        return res
        
    
    def get_latest(self) -> str:
        try:
            return next(
                git.Repo().iter_commits(f"origin/{version.branch}", max_count=1)
            ).hexsha
        except Exception:
            return ""
        
    @loader.on_bot(lambda self, app, call: call.data == "update")
    async def update_callback_handler(self, app: Client, call: CallbackQuery):
        os.system("git pull")
        await app.send_message(
            call.message.chat.id,
            self.strings["updaing"],
        )
        self.db.set("shizu.updater", "restart", {
            "chat": call.message.chat.id,
            "id": call.message.id,
            "start": str(round(time.time())),
            "type": "update",
        })
        atexit.register(os.execl(sys.executable, sys.executable, "-m", "shizu"))
        return sys.exit(0)
        
    @loader.loop(interval=20, autostart=True)
    async def check_updst(self) -> None:
        last_ = self.db.get("shizu.updater", "commit_last", "")
        if last_ == self.get_latest():
            return 
        await self.bot.bot.send_message(
            self.tg_id,
            self.strings["update_required"].format(
                utils.get_git_hash()[:6],
                f'<a href="https://github.com/AmoreForever/Shizu/compare/{utils.get_git_hash()[:12]}...{self.get_latest()[:12]}">{self.get_latest()[:6]}</a>',
            ),
            reply_markup=self.update_keyboard(),
        )
        logging.info("send updst")
        self.db.set("shizu.updater", "commit_last", self.get_latest())