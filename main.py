import asyncio
import json
import logging
import random
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F, Router, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.markdown import hbold, hlink
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

if TOKEN is None:
    print("Error: BOT_TOKEN environment variable not found.")
    sys.exit(1)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

# Load quotes from JSON
with open("quotes.json", "r") as f:
    quotes_data = json.load(f)
    quotes = quotes_data["quotes"]

# Current quote index
current_quote_index = 0

# Function to get a quote and format the message
async def get_quote_message(index):
    quote = quotes[index]
    message_text = f"{hbold(quote['quote'])}\n\n— {hbold(quote['author'])}"
    return message_text

# Handle /generate_quote command
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    bot_info = await bot.get_me()
    bot_name = bot_info.first_name
    await message.answer(
        f"Hey {hbold(message.from_user.first_name)} !\n\n I am {hbold(bot_name)} simple quote generator bot made by @CodeForChrist. Use /generate_quote to get a random quote.",
        parse_mode=ParseMode.HTML,
    )

@router.message(F.text == "/generate_quote")
async def generate_quote_handler(message: Message) -> None:
    global current_quote_index
    current_quote_index = random.randint(0, len(quotes) - 1)
    message_text = await get_quote_message(current_quote_index)

    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➡️", callback_data="next"),
            ]
        ]
    )

    await message.answer(message_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)


# Handle callback queries from inline keyboard buttons
@router.callback_query()
async def callback_query_handler(query: types.CallbackQuery) -> None:
    global current_quote_index
    if query.data == "next":
        current_quote_index = (current_quote_index + 1) % len(quotes)
        # Now show both "Next" and "Previous" buttons
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="➡️", callback_data="next"),
                    InlineKeyboardButton(text="⬅️", callback_data="prev"),
                ]
            ]
        )
    elif query.data == "prev":
        current_quote_index = (current_quote_index - 1) % len(quotes)
        # Keep the same buttons (Next and Previous)
        keyboard = query.message.reply_markup
    message_text = await get_quote_message(current_quote_index)
    await query.message.edit_text(message_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await query.answer()


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())