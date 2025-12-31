import os
import httpx

from telegram.ext import ApplicationBuilder
from telegram.request import HTTPXRequest
from telegram.constants import ParseMode


class TelegramFunction:
    def __init__(self):
        self.botToken=os.getenv("BOT_TOKEN")
        self.chatId=os.getenv("GROUP_CHAT_ID")

    
    async def sendImageWithCaption(self, imagePath:str,caption: str | None= None):
        httpx_kwargs = {
            "timeout": httpx.Timeout(60, connect=30,read=30,write=30)
        }
        request = HTTPXRequest(
            connect_timeout=30,
            read_timeout=30,
            write_timeout=30,
            httpx_kwargs=httpx_kwargs
        )
        app = ApplicationBuilder().token(self.botToken).request(request).build()

        with open(imagePath, 'rb') as file:
            if caption is not None:
                await app.bot.send_photo(chat_id=self.chatId,photo=file,caption=caption)
            else:
                await app.bot.send_photo(chat_id=self.chatId,photo=file)
        
        await app.shutdown()
    
    async def sendText(self, text: str):
        httpx_kwargs = {
            "timeout": httpx.Timeout(60, connect=30,read=30,write=30)
        }
        request = HTTPXRequest(
            connect_timeout=30,
            read_timeout=30,
            write_timeout=30,
            httpx_kwargs=httpx_kwargs
        )
        app = ApplicationBuilder().token(self.botToken).request(request).build()
        for i in range(0, len(text), 4000):
            await app.bot.send_message(self.chatId, text[i:i + 4000])
