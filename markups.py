from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard(is_admin: bool = False, bot_active: bool = True):
    keyboard = []
    if bot_active:
        keyboard.append([InlineKeyboardButton("🎫 ساخت تیکت جدید 📬", callback_data="create_ticket")])
        keyboard.append([InlineKeyboardButton("✨️ تیکت های ایجاد شده 🏅", callback_data="my_tickets")])
    
    keyboard.append([InlineKeyboardButton("🪄 ورود به ربات اصلی خرید/کانفیگ رایگان ⚜️", url="https://t.me/kingconfi8sbot")])
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("🛠 پنل مدیریت ادمین", callback_data="admin_panel")])
        
    return InlineKeyboardMarkup(keyboard)

def ticket_confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton("📭 ویرایش ♻️", callback_data="edit_ticket")],
        [InlineKeyboardButton("✔️ ارسال 🚀", callback_data="send_ticket")],
        [InlineKeyboardButton("❄️ لغو ❌", callback_data="cancel_ticket")]
    ]
    return InlineKeyboardMarkup(keyboard)

def ticket_edit_keyboard(messages_count: int):
    keyboard = [
        [InlineKeyboardButton("ویرایش عنوان", callback_data="edit_title")]
    ]
    if messages_count >= 1:
        keyboard.append([InlineKeyboardButton("ویرایش پیام اول", callback_data="edit_msg_1")])
    if messages_count >= 2:
        keyboard.append([InlineKeyboardButton("ویرایش پیام دوم", callback_data="edit_msg_2")])
    if messages_count >= 3:
        keyboard.append([InlineKeyboardButton("ویرایش پیام سوم", callback_data="edit_msg_3")])
        
    keyboard.append([InlineKeyboardButton("اتمام ویرایش", callback_data="finish_edit")])
    return InlineKeyboardMarkup(keyboard)

def admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎟 مشاهده تمام تیکت‌ها", callback_data="admin_all_tickets_0")],
        [InlineKeyboardButton("🟢 تیکت‌های باز", callback_data="admin_open_tickets_0")],
        [InlineKeyboardButton("🔴 تیکت‌های بسته", callback_data="admin_closed_tickets_0")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_settings_keyboard(bot_active: bool):
    status_on = "✅ ON" if bot_active else "ON"
    status_off = "OFF" if bot_active else "❌ OFF"
    
    # Visual indicator highlighting current status
    if bot_active:
        status_on = "✅ ON [فعال]"
        status_off = "❌ OFF"
    else:
        status_on = "✅ ON"
        status_off = "❌ OFF [غیرفعال]"

    keyboard = [
        [InlineKeyboardButton(status_on, callback_data="set_bot_on"),
         InlineKeyboardButton(status_off, callback_data="set_bot_off")],
        [InlineKeyboardButton("🔙 بازگشت به پنل مدیریت", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def pagination_keyboard(page: int, total_pages: int, prefix: str):
    keyboard = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ صفحه قبل", callback_data=f"{prefix}_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("صفحه بعد ➡️", callback_data=f"{prefix}_{page + 1}"))
        
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به پنل مدیریت", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)

def admin_ticket_manage_keyboard(ticket_id: int, status: str):
    status_btn = InlineKeyboardButton("🔒 بستن تیکت", callback_data=f"adm_close_{ticket_id}") if status == 'Open' else InlineKeyboardButton("🔓 باز کردن دوباره تیکت", callback_data=f"adm_open_{ticket_id}")
    keyboard = [
        [status_btn, InlineKeyboardButton("💬 پاسخ به تیکت", callback_data=f"adm_reply_{ticket_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def user_ticket_detail_keyboard(ticket_id: int, status: str):
    keyboard = []
    if status == 'Open':
        keyboard.append([InlineKeyboardButton("💬 ارسال پیام جدید", callback_data=f"usr_reply_{ticket_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="my_tickets")])
    return InlineKeyboardMarkup(keyboard)

def back_to_main_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]])