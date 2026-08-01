from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from states.states import TicketState
from database.db import (
    get_bot_status, get_user_open_tickets_count, create_ticket, 
    add_message, get_ticket, get_ticket_messages, update_ticket_status
)
from keyboards.markups import (
    ticket_confirm_keyboard, ticket_edit_keyboard, main_menu_keyboard, back_to_main_keyboard
)
from config import ADMIN_ID

async def start_create_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    bot_status = await get_bot_status()
    if bot_status != 'active':
        await query.edit_message_text(
            "✨️ درحال‌حاضر ربات غیرفعال میباشد !\n\nبعدا تلاش کنید یا مستقیم به پشتیبانی بگویید 🎁\n\n《@mr1kk1rn0》",
            reply_markup=back_to_main_keyboard()
        )
        return ConversationHandler.END

    user_id = update.effective_user.id
    open_count = await get_user_open_tickets_count(user_id)
    if open_count >= 3:
        await query.edit_message_text(
            "⚠️ شما حداکثر تعداد تیکت‌های باز (۳ عدد) را دارید. لطفاً منتظر پاسخ ادمین باشید یا تیکت‌های قبلی را ببندید.",
            reply_markup=back_to_main_keyboard()
        )
        return ConversationHandler.END

    context.user_data['ticket_title'] = ""
    context.user_data['ticket_messages'] = []

    await query.edit_message_text(
        "✔️ شما درحال ایجاد تیکت جدید هستید ⚠️\n\nیک نام برای تیکت خود ارسال کنید ♻️"
    )
    return TicketState.GET_TITLE

async def get_ticket_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text
    context.user_data['ticket_title'] = title
    
    await update.message.reply_text(
        "🎁 داش، حالا متن، عکس، ویدیو یا فایل تیکتت رو بفرست همینجا ✨️\n\n(می‌توانید تا ۳ پیام ارسال کنید و سپس دکمه تایید را بزنید)",
        reply_markup=ticket_confirm_keyboard() # Or temporary confirmation view
    )
    return TicketState.COLLECT_MESSAGES

async def collect_ticket_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    messages = context.user_data.get('ticket_messages', [])
    
    if len(messages) >= 3:
        await message.reply_text("⚠️ حداکثر ۳ پیام ارسال کرده‌اید. لطفاً دکمه تایید را بزنید.")
        return TicketState.COLLECT_MESSAGES

    msg_type = "text"
    file_id = None
    caption = message.text or message.caption or ""

    if message.photo:
        msg_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        msg_type = "video"
        file_id = message.video.file_id
    elif message.voice:
        msg_type = "voice"
        file_id = message.voice.file_id
    elif message.document:
        msg_type = "document"
        file_id = message.document.file_id

    messages.append({
        "type": msg_type,
        "file_id": file_id,
        "caption": caption
    })
    context.user_data['ticket_messages'] = messages

    # Bot sends no text response after each message as requested, but shows confirmation panel when requested or reminds user
    if len(messages) == 3:
        await message.reply_text(
            f"🪄 تعداد ۳ پیام شما ثبت شد. آیا مایل به ارسال این تیکت هستین؟ 🎟",
            reply_markup=ticket_confirm_keyboard()
        )
        return TicketState.CONFIRM_TICKET
    else:
        # Prompt confirmation panel on demand or let user continue sending up to 3 messages
        await message.reply_text(
            f"✅ پیام شماره {len(messages)} ثبت شد. پیام بعدی را بفرستید یا دکمه تایید زیر را بزنید:",
            reply_markup=ticket_confirm_keyboard()
        )
        return TicketState.COLLECT_MESSAGES

async def confirm_ticket_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    messages = context.user_data.get('ticket_messages', [])
    if not messages:
        await query.edit_message_text("⚠️ هیچ پیامی ارسال نکرده‌اید!", reply_markup=back_to_main_keyboard())
        return ConversationHandler.END

    await query.edit_message_text(
        "🪄 آیا مایل به ارسال این تیکت هستین؟ 🎟",
        reply_markup=ticket_confirm_keyboard()
    )
    return TicketState.CONFIRM_TICKET

async def final_send_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    title = context.user_data.get('ticket_title', 'بدون عنوان')
    messages = context.user_data.get('ticket_messages', [])
    
    ticket_id = await create_ticket(user.id, title)
    
    for msg in messages:
        await add_message(ticket_id, user.id, msg['type'], msg['file_id'], msg['caption'])
        
    await query.edit_message_text(
        f"✅ تیکت شما با موفقیت ثبت شد!\n\n🎟 شماره تیکت: #{ticket_id}",
        reply_markup=main_menu_keyboard(user.id == ADMIN_ID, True)
    )
    
    # Send to Admin
    admin_text = (
        f"📩 تیکت جدید دریافت شد!\n\n"
        f"🎟 شماره تیکت: #{ticket_id}\n"
        f"👤 نام: {user.full_name}\n"
        f"🆔 آیدی: {user.id}\n"
        f"🔗 Username: @{user.username if user.username else 'ندارد'}\n"
        f"📌 عنوان: {title}\n"
        f"━━━━━━━━━━━━━━━"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        for msg in messages:
            if msg['type'] == 'photo':
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=msg['file_id'], caption=msg['caption'])
            elif msg['type'] == 'video':
                await context.bot.send_video(chat_id=ADMIN_ID, video=msg['file_id'], caption=msg['caption'])
            elif msg['type'] == 'voice':
                await context.bot.send_voice(chat_id=ADMIN_ID, voice=msg['file_id'], caption=msg['caption'])
            elif msg['type'] == 'document':
                await context.bot.send_document(chat_id=ADMIN_ID, document=msg['file_id'], caption=msg['caption'])
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=msg['caption'])
    except Exception as e:
        print(f"Error sending ticket to admin: {e}")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel_ticket_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    
    user = update.effective_user
    bot_status = await get_bot_status()
    
    await query.edit_message_text(
        "❌ عملیات لغو شد.",
        reply_markup=main_menu_keyboard(user.id == ADMIN_ID, bot_status == 'active')
    )
    return ConversationHandler.END

async def edit_ticket_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    messages = context.user_data.get('ticket_messages', [])
    
    await query.edit_message_text(
        "🛠 بخش مورد نظر برای ویرایش را انتخاب کنید:",
        reply_markup=ticket_edit_keyboard(len(messages))
    )
    return TicketState.CONFIRM_TICKET # or editing flow state

# Specific Edit Handlers
async def edit_title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("عنوان جدید تیکت را ارسال کنید:")
    return TicketState.EDIT_TITLE

async def save_new_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ticket_title'] = update.message.text
    await update.message.reply_text(
        "🪄 عنوان ویرایش شد. آیا مایل به ارسال این تیکت هستین؟ 🎟",
        reply_markup=ticket_confirm_keyboard()
    )
    return TicketState.CONFIRM_TICKET
