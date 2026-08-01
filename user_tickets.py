from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_user_tickets, get_ticket, get_ticket_messages, add_message
from keyboards.markups import user_ticket_detail_keyboard, back_to_main_keyboard
from config import ADMIN_ID

async def list_user_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    tickets = await get_user_tickets(user_id)
    if not tickets:
        await query.edit_message_text(
            "📭 شما هنوز هیچ تیکتی ثبت نکرده‌اید.",
            reply_markup=back_to_main_keyboard()
        )
        return

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = []
    for t in tickets:
        status_emoji = "🟢" if t['status'] == 'Open' else "🔴"
        keyboard.append([InlineKeyboardButton(f"🎟 #{t['ticket_id']} | {t['title']} | {status_emoji} {t['status']}", callback_data=f"view_usr_ticket_{t['ticket_id']}")])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])
    await query.edit_message_text("✨️ تیکت‌های ایجاد شده شما:", reply_markup=InlineKeyboardMarkup(keyboard))

async def view_user_ticket_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    ticket_id = int(query.data.split("_")[-1])
    ticket = await get_ticket(ticket_id)
    messages = await get_ticket_messages(ticket_id)
    
    if not ticket:
        await query.edit_message_text("⚠️ تیکت مورد نظر یافت نشد.", reply_markup=back_to_main_keyboard())
        return

    text = f"🎟 تیکت شماره #{ticket['ticket_id']}\n📌 عنوان: {ticket['title']}\n📌 وضعیت: {ticket['status']}\n🕒 تاریخ: {ticket['created_at']}\n━━━━━━━━━━━━━━━\n\n"
    for msg in messages:
        sender = "👤 شما" if msg['sender_id'] == ticket['user_id'] else "🛠 ادمین"
        content = msg['caption'] or f"[{msg['message_type']}]"
        text += f"{sender}: {content}\n"

    await query.edit_message_text(text, reply_markup=user_ticket_detail_keyboard(ticket_id, ticket['status']))