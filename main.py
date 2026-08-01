import asyncio
import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ConversationHandler, filters
)
from config import BOT_TOKEN, ADMIN_ID
from database.db import init_db
from states.states import TicketState

# Handlers
from handlers.start import start_command, back_to_main_callback
from handlers.ticket import (
    start_create_ticket, get_ticket_title, collect_ticket_content,
    confirm_ticket_callback, final_send_ticket, cancel_ticket_callback,
    edit_ticket_callback, edit_title_handler, save_new_title
)
from handlers.user_tickets import list_user_tickets, view_user_ticket_detail
from handlers.admin import (
    admin_panel_handler, admin_settings_handler, set_bot_status_callback,
    admin_list_tickets, admin_view_ticket_detail, admin_toggle_ticket_status,
    admin_reply_prompt, handle_admin_reply_message
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation handler for ticket creation
    ticket_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_create_ticket, pattern="^create_ticket$")],
        states={
            TicketState.GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ticket_title)],
            TicketState.COLLECT_MESSAGES: [
                MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL) & ~filters.COMMAND, collect_ticket_content),
                CallbackQueryHandler(confirm_ticket_callback, pattern="^send_ticket$")
            ],
            TicketState.CONFIRM_TICKET: [
                CallbackQueryHandler(final_send_ticket, pattern="^send_ticket$"),
                CallbackQueryHandler(cancel_ticket_callback, pattern="^cancel_ticket$"),
                CallbackQueryHandler(edit_ticket_callback, pattern="^edit_ticket$")
            ],
            TicketState.EDIT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_new_title)]
        },
        fallbacks=[CallbackQueryHandler(cancel_ticket_callback, pattern="^cancel_ticket$")]
    )

    # Command & Callback Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(ticket_conv_handler)
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_main$"))
    application.add_handler(CallbackQueryHandler(list_user_tickets, pattern="^my_tickets$"))
    application.add_handler(CallbackQueryHandler(view_user_ticket_detail, pattern="^view_usr_ticket_\d+$"))

    # Admin Panel Handlers
    application.add_handler(CallbackQueryHandler(admin_panel_handler, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_settings_handler, pattern="^admin_settings$"))
    application.add_handler(CallbackQueryHandler(set_bot_status_callback, pattern="^set_bot_(on|off)$"))
    application.add_handler(CallbackQueryHandler(admin_list_tickets, pattern="^admin_(all|open|closed)_tickets_\d+$"))
    application.add_handler(CallbackQueryHandler(admin_view_ticket_detail, pattern="^adm_view_\d+$"))
    application.add_handler(CallbackQueryHandler(admin_toggle_ticket_status, pattern="^adm_(close|open)_\d+$"))
    application.add_handler(CallbackQueryHandler(admin_reply_prompt, pattern="^adm_reply_\d+$"))
    
    # Admin text/media reply handler
    application.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL) & ~filters.COMMAND & filters.User(user_id=ADMIN_ID),
        handle_admin_reply_message
    ))

    application.add_error_handler(error_handler)

    logger.info("🤖 Bot is starting and polling...")
    application.run_polling()

if __name__ == "__main__":
    main()