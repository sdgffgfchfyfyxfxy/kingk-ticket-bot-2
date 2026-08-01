from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database.db import (
    get_stats, get_bot_status, set_bot_status, get_all_tickets, 
    count_tickets, get_ticket, get_ticket_messages, update_ticket_status, add_message
)
from keyboards.markups import (
    admin_panel_keyboard, admin_settings_keyboard, pagination_keyboard, 
    admin_ticket_manage_keyboard, back_to_main_keyboard
)

async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if update.effective_user.id != ADMIN_ID:
        await query.answer("❌ شما دسترسی ادمین ندارید!", show_alert=True)
        return

    users, open_t, closed_t, msgs = await get_stats()
    text = (
        f"🛠 **پنل مدیریت ادمین**\n\n"
        f"👥 تعداد کاربران: {users}\n"
        f"🟢 تیکت‌های باز: {open_t}\n"
        f"🔴 تیکت‌های بسته: {closed_t}\n"
        f"💬 کل پیام‌ها: {msgs}\n"
    )
    await query.edit_message_text(text, reply_markup=admin_panel_keyboard(), parse_mode="Markdown")

async def admin_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bot_status = await get_bot_status()
    await query.edit_message_text("⚙️ تنظیمات ربات:", reply_markup=admin_settings_keyboard(bot_status == 'active'))

async def set_bot_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "set_bot_on":
        await set_bot_status("active")
    else:
        await set_bot_status("inactive")
        
    bot_status = await get_bot_status()
    await query.edit_message_text("⚙️ تنظیمات ربات بروز شد:", reply_markup=admin_settings_keyboard(bot_status == 'active'))

async def admin_list_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split("_")
    # format: admin_{status}_tickets_{page} or admin_all_tickets_{page}
    if "all" in query.data:
        status = None
        prefix = "admin_all_tickets"
    elif "open" in query.data:
        status = "Open"
        prefix = "admin_open_tickets"
    else:
        status = "Closed"
        prefix = "admin_closed_tickets"
        
    page = int(data_parts[-1])
    limit = 5
    offset = page * limit
    
    tickets = await get_all_tickets(status=status, limit=limit, offset=offset)
    total = await count_tickets(status=status)
    total_pages = (total + limit - 1) // limit
    
    if not tickets:
        await query.edit_message_text("📭 هیچ تیکتی یافت نشد.", reply_markup=admin_panel_keyboard())
        return

    keyboard = []
    for t in tickets:
        status_emoji = "🟢" if t['status'] == 'Open' else "🔴"
        keyboard.append([InlineKeyboardButton(f"🎟 #{t['ticket_id']} | {t['title'][:15]} | {status_emoji} {t['status']}", callback_data=f"adm_view_{t['ticket_id']}")])
        
    # Add pagination
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ صفحه قبل", callback_data=f"{prefix}_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("صفحه بعد ➡️", callback_data=f"{prefix}_{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
        
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به پنل مدیریت", callback_data="admin_panel")])
    await query.edit_message_text(f"📋 لیست تیکت‌ها (صفحه {page + 1} از {total_pages or 1}):", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_view_ticket_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    ticket_id = int(query.data.split("_")[-1])
    ticket = await get_ticket(ticket_id)
    messages = await get_ticket_messages(ticket_id)
    
    if not ticket:
        await query.edit_message_text("⚠️ تیکت یافت نشد.", reply_markup=admin_panel_keyboard())
        return

    text = f"🎟 تیکت شماره #{ticket['ticket_id']}\n👤 کاربر: {ticket['user_id']}\n📌 عنوان: {ticket['title']}\n📌 وضعیت: {ticket['status']}\n🕒 تاریخ: {ticket['created_at']}\n━━━━━━━━━━━━━━━\n\n"
    for msg in messages:
        sender = "👤 کاربر" if msg['sender_id'] == ticket['user_id'] else "🛠 ادمین"
        content = msg['caption'] or f"[{msg['message_type']}]"
        text += f"{sender}: {content}\n"

    await query.edit_message_text(text, reply_markup=admin_ticket_manage_keyboard(ticket_id, ticket['status']))

async def admin_toggle_ticket_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split("_")
    action = data_parts[1] # close or open
    ticket_id = int(data_parts[2])
    
    new_status = 'Closed' if action == 'close' else 'Open'
    await update_ticket_status(ticket_id, new_status)
    
    if new_status == 'Closed':
        try:
            ticket = await get_ticket(ticket_id)
            await context.bot.send_message(chat_id=ticket['user_id'], text=f"✅ تیکت شماره #{ticket_id} شما بسته شد.")
        except Exception:
            pass

    # Refresh detail view
    ticket = await get_ticket(ticket_id)
    messages = await get_ticket_messages(ticket_id)
    text = f"🎟 تیکت شماره #{ticket['ticket_id']}\n👤 کاربر: {ticket['user_id']}\n📌 عنوان: {ticket['title']}\n📌 وضعیت: {ticket['status']}\n🕒 تاریخ: {ticket['created_at']}\n━━━━━━━━━━━━━━━\n\n"
    for msg in messages:
        sender = "👤 کاربر" if msg['sender_id'] == ticket['user_id'] else "🛠 ادمین"
        content = msg['caption'] or f"[{msg['message_type']}]"
        text += f"{sender}: {content}\n"

    await query.edit_message_text(text, reply_markup=admin_ticket_manage_keyboard(ticket_id, ticket['status']))

async def admin_reply_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ticket_id = int(query.data.split("_")[-1])
    
    context.user_data['admin_replying_to'] = ticket_id
    await query.edit_message_text(
        f"💬 لطفاً پاسخ خود را برای تیکت #{ticket_id} (متن، عکس، فایل و...) ارسال کنید:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 انصراف", callback_data=f"adm_view_{ticket_id}")]])
    )

async def handle_admin_reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ticket_id = context.user_data.get('admin_replying_to')
    if not ticket_id:
        return
        
    ticket = await get_ticket(ticket_id)
    if not ticket:
        await update.message.reply_text("⚠️ تیکت یافت نشد.")
        return

    message = update.message
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

    await add_message(ticket_id, ADMIN_ID, msg_type, file_id, caption)

    # Send to user
    try:
        await context.bot.send_message(chat_id=ticket['user_id'], text=f"💬 پاسخ جدید از ادمین برای تیکت #{ticket_id}:")
        if msg_type == 'photo':
            await context.bot.send_photo(chat_id=ticket['user_id'], photo=file_id, caption=caption)
        elif msg_type == 'video':
            await context.bot.send_video(chat_id=ticket['user_id'], video=file_id, caption=caption)
        elif msg_type == 'voice':
            await context.bot.send_voice(chat_id=ticket['user_id'], voice=file_id, caption=caption)
        elif msg_type == 'document':
            await context.bot.send_document(chat_id=ticket['user_id'], document=file_id, caption=caption)
        else:
            await context.bot.send_message(chat_id=ticket['user_id'], text=caption)
            
        await message.reply_text(f"✅ پاسخ با موفقیت برای کاربر ارسال شد.", reply_markup=back_to_main_keyboard())
    except Exception as e:
        await message.reply_text(f"❌ خطا در ارسال پیام به کاربر: {e}")

    context.user_data.pop('admin_replying_to', None)
