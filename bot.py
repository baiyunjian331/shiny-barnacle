#!/usr/bin/env python3

import asyncio
import logging
import os
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from upload import upload
from google_utils import configure_gauth, ensure_token_storage
from creds import TELEGRAM_BOT_TOKEN, GOOGLE_TOKEN_FILE
from pySmartDL import SmartDL
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from plugins import TEXT

LOG_LEVEL_NAME = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME, logging.INFO)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=LOG_LEVEL
)

logging.info("🤖 机器人启动中……")

from plugins.tok_rec import is_token
from plugins.dpbox import DPBOX
from plugins.wdl import wget_dl
from mega import Mega

gauth = configure_gauth(GoogleAuth())
TOKEN_FILE_PATH = GOOGLE_TOKEN_FILE


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TEXT.HELP,
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        logging.exception("❌ 发送帮助信息时出现异常")
# command ```auth```
async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'
    drive: GoogleDrive
    http = None
    initial_folder = None
    ensure_token_storage()
    try:
        gauth.LoadCredentialsFile(TOKEN_FILE_PATH)
    except Exception as e:
        logging.warning("⚠️ 未找到凭证文件：%s", e)

    if gauth.credentials is None:
        authurl = gauth.GetAuthUrl()

        AUTH = TEXT.AUTH_URL.format(authurl)
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=AUTH,
                parse_mode=ParseMode.HTML,
            )

    elif gauth.access_token_expired:
        # Refresh Token if expired
        gauth.Refresh()
        ensure_token_storage()
        gauth.SaveCredentialsFile(TOKEN_FILE_PATH)
    else:
        # auth with  saved creds
        gauth.Authorize()
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXT.ALREADY_AUTH,
            )


# It will handle Sent Token By Users
async def token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    msg = update.message.text

    if is_token(msg):
        token = msg.split()[-1]
        logging.info("收到新的授权令牌请求，正在尝试验证。")
        try:
            ensure_token_storage()
            gauth.Auth(token)
            gauth.SaveCredentialsFile(TOKEN_FILE_PATH)
            logging.info("✅ 授权令牌保存成功。")
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=TEXT.AUTH_SUCC,
            )
        except Exception as e:
            logging.error("❌ 授权失败：%s", e)
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=TEXT.AUTH_ERROR,
            )
   

# command `Start`
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=TEXT.START.format(update.message.from_user.first_name),
        parse_mode=ParseMode.HTML,
    )

# command `revoke`
async def revoke_tok(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if os.path.exists(TOKEN_FILE_PATH):
            os.remove(TOKEN_FILE_PATH)
            logging.info("🔒 已撤销本地凭证文件。")
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=TEXT.REVOKE_TOK,
                )
        else:
            logging.warning("⚠️ 未找到可撤销的凭证文件。")
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=TEXT.REVOKE_FAIL,
                )
    except Exception:
        logging.exception("❌ 撤销凭证时发生异常")
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXT.REVOKE_FAIL,
            )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🏓 机器人在线！",
        )

async def UPLOAD(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat_id is None:
        return

    url_text = update.message.text or ""
    url = url_text.split()[-1]

    if not os.path.exists(TOKEN_FILE_PATH):
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=TEXT.NOT_AUTH,
        )
        return

    sent_message = await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=TEXT.PROCESSING,
    )

    download_status = False
    filename = None

    try:
        if "openload" in url or "oload" in url:
            await sent_message.edit_text("⚠️ Openload 服务已下线，无法处理该链接。")
            return

        if 'dropbox.com' in url:
            url = DPBOX(url)
            filename = url.split("/")[-1]
            logging.info("📥 开始下载 Dropbox 文件：%s", filename)
            await sent_message.edit_text(TEXT.DP_DOWNLOAD)
            filename = await asyncio.to_thread(wget_dl, str(url))
            logging.info("✅ Dropbox 文件下载完成：%s", filename)
            await sent_message.edit_text(TEXT.DOWN_COMPLETE)
            download_status = True
        elif 'mega.nz' in url:
            try:
                logging.info("📥 开始下载 Mega 链接")
                await sent_message.edit_text(TEXT.DOWN_MEGA)

                def _download_mega() -> str:
                    m = Mega.from_credentials(TEXT.MEGA_EMAIL, TEXT.MEGA_PASSWORD)
                    return m.download_from_url(url)

                filename = await asyncio.to_thread(_download_mega)
                logging.info("✅ Mega 文件下载完成：%s", filename)
                await sent_message.edit_text(TEXT.DOWN_COMPLETE)
                download_status = True
            except Exception as e:
                logging.error("❌ Mega 下载失败：%s", e)
                await sent_message.edit_text("❌ Mega 下载失败，请稍后重试。")
        else:
            try:
                filename = url.split("/")[-1]
                logging.info("📥 开始下载文件：%s", filename)
                await sent_message.edit_text(TEXT.DOWNLOAD)
                filename = await asyncio.to_thread(wget_dl, str(url))
                logging.info("✅ 下载完成：%s", filename)
                await sent_message.edit_text(TEXT.DOWN_COMPLETE)
                download_status = True
            except Exception as e:
                if TEXT.DOWN_TWO:
                    logging.warning("⚠️ 下载器 1 出现异常，正在尝试备用下载器：%s", e)
                    try:
                        await sent_message.edit_text(
                            f"⚠️ 下载器 1 出错：{e}\n\n ⏳ 下载器 2 正在尝试下载..."
                        )

                        def _smartdl(download_url: str) -> str:
                            obj = SmartDL(download_url)
                            obj.start()
                            return obj.get_dest()

                        filename = await asyncio.to_thread(_smartdl, url)
                        download_status = True
                    except Exception as err:
                        logging.error("❌ 备用下载器下载失败：%s", err)
                        await sent_message.edit_text(f"❌ 下载失败：{err}")
                        download_status = False
                else:
                    logging.error("❌ 下载失败：%s", e)
                    await sent_message.edit_text(f"❌ 下载失败：{e}")
                    download_status = False

        if filename and "error" in os.path.basename(filename).lower():
            await sent_message.edit_text("❌ 下载失败，文件可能已损坏。")
            if os.path.exists(filename):
                os.remove(filename)
            download_status = False

        if download_status and filename:
            await sent_message.edit_text(TEXT.UPLOADING)

            size_mb = round((os.path.getsize(filename)) / 1048576)
            file_display_name = os.path.basename(filename)

            try:
                file_link = await asyncio.to_thread(
                    upload, filename, update, context, TEXT.drive_folder_name
                )
            except Exception as e:
                logging.error("❌ 上传阶段出错（代码 UPX11）：%s", e)
                await sent_message.edit_text(f"❌ 上传失败：{e}")
            else:
                await sent_message.edit_text(
                    TEXT.DOWNLOAD_URL.format(file_display_name, size_mb, file_link),
                    parse_mode=ParseMode.HTML,
                )
            finally:
                logging.info("🧹 删除临时文件：%s", filename)
                try:
                    os.remove(filename)
                except Exception as e:
                    logging.warning("⚠️ 删除临时文件失败：%s", e)
        elif not download_status:
            await sent_message.edit_text("❌ 上传失败：下载未成功。")

    except Exception as e:
        logging.error("❌ 上传流程异常（代码 UXP12）：%s", e)
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as cleanup_error:
                logging.error("⚠️ 清理临时文件失败（代码 UXP13）：%s", cleanup_error)
        await sent_message.edit_text(f"❌ 上传失败：{e}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TEXT.UPDATE,
            parse_mode=ParseMode.HTML,
        )


bot_token = TELEGRAM_BOT_TOKEN
application = ApplicationBuilder().token(bot_token).build()

application.add_handler(CommandHandler("update", status))
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help))
application.add_handler(CommandHandler("auth", auth))
application.add_handler(CommandHandler("revoke", revoke_tok))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(
    MessageHandler(filters.TEXT & filters.Regex(r'http'), UPLOAD)
)
application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.Regex(r'http'),
        token,
    )
)


def main() -> None:
    logging.info("✅ 机器人已成功启动！")
    print("🚀 机器人正在运行。按 Ctrl+C 可停止。")
    print("📡 等待 Telegram 消息中……")
    application.run_polling()


if __name__ == "__main__":
    main()
