import asyncio
import sys
import re
import os
import logging

if sys.version_info < (3, 8, 0) or not os.environ.get("GOORM"):
    logging.warning("🚫 Error: you are using Python version < 3.8")
    sys.exit(1)

elif __package__ != "shizu":
    print("🚫 Error: you cannot run this as a script; you must execute as a package")
    sys.exit(1)

else:
    try:
        import pyrogram
        from .version import __version__
        from . import main
        from .logger import setup_logger

        setup_logger("INFO")

        aozora = (
            "\n█▀ █ █ █ ▀█ █ █"
            "\n▄█ █▀█ █ █▄ █▄█\n\n"
            f"🐙 Shuzu v{__version__} is starting...\n"
            f"🐍 Python v{sys.version}\n"
            f"👾 Pyrogram v{pyrogram.__version__}\n"
        )
        logging.info(aozora)
    except ModuleNotFoundError as module:
        print(
            "🔁 Trying to install it automatically...\n"
            "⌛ Attempting dependencies installation... Just wait."
        )  
        os.popen("pip3 install -r requirements.txt").read()
        print("👍 Dependencies installed")
        print("🔁 Retrying to run bot again please wait..")
        asyncio.run(main.main())
        

if __name__ == "__main__":
    asyncio.run(main.main())
