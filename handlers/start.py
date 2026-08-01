from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database.db import add_user, get_bot_status
from keyboards.markups import main_menu_keyboard

START_TEXT = (
    "سلام رفیق 😎👋\n\n"
    "🎟 به بات تیکت امن kingk-configs خوش اومدی 🫴😑\n\n"
    "💨 اینجا میتونی خیلی امن و راحت تیکت ثبت کنی و ادمین از داخل همینجا بهت پاسخ بده 🤌🗿\n\n"
    "🫷🫪 ولی اگر برای خرید کانفیگ یا دریافت کانفیگ رایگان اومدی، لطفاً مستقیم به پشتیبانی پیام بده:\n\n"
    "@mr1kk1rn0 🚀"
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await add_user(user.id, user.full_name, user.username)
    
    bot_status = await get_bot_status()
    is_admin = (user.id == ADMIN_ID)
    is_active = (bot_status == 'active')

    if update.message:
        await update.message.reply_text(START_TEXT, reply_markup=main_menu_keyboard(is_admin, is_active))
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(START_TEXT, reply_markup=main_menu_keyboard(is_admin, is_active))

async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    bot_status = await get_bot_status()
    is_admin = (user.id == ADMIN_ID)
    is_active = (bot_status == 'active')
    
    await query.edit_message_text(START_TEXT, reply_markup=main_menu_keyboard(is_admin, is_active))
