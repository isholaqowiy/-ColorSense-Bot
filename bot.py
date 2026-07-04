import os
import logging
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

import database
import color_extractor
import palette_generator
import utils

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation context boundaries states
MENU_CHOICE, AWAITING_IMAGE = range(2)

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🎨 Extract Color Palette", callback_data="menu_extract")],
        [InlineKeyboardButton("📋 Color Code Details", callback_data="menu_details")],
        [InlineKeyboardButton("⚙ Settings", callback_data="menu_settings"),
         InlineKeyboardButton("❓ Help", callback_data="menu_help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utils.ensure_temp_directory()
    await database.init_db()
    welcome = (
        "👋 Welcome to *ColorSense Bot*!\n"
        "Discover the beautiful colors hidden inside your images.\n\n"
        "🎨 *Extract striking color palettes*\n"
        "🌈 *Identify exact dominant color coverage*\n"
        "📋 *Get HEX, RGB, HSL, HSV, and CMYK listings*\n"
        "💾 *Export code layouts for CSS/Tailwind workflows*\n\n"
        "Tap a button below or upload an image to begin."
    )
    if update.message:
        await update.message.reply_text(welcome, reply_markup=get_main_menu(), parse_mode="Markdown")
    return MENU_CHOICE

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "❓ *ColorSense Manual Guide*\n\n"
        "1. Tap *Extract Color Palette* and upload your image (up to 20MB).\n"
        "2. The bot runs an advanced mathematical clustering model over pixel array layers.\n"
        "3. You'll receive a beautiful image preview card and detailed developer code snippets instantly."
    )
    if update.message: await update.message.reply_text(msg)
    elif update.callback_query: await update.callback_query.message.reply_text(msg)

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    
    if query.data == "menu_extract" or query.data == "menu_details":
        await query.message.reply_text("🖼 Send or upload the image you want me to analyze (PNG, JPG, WEBP, BMP):")
        return AWAITING_IMAGE
        
    elif query.data == "menu_settings":
        kb = [
            [InlineKeyboardButton("Size: 5 Colors", callback_data="set_size_5"),
             InlineKeyboardButton("Size: 10 Colors", callback_data="set_size_10")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="go_home")]
        ]
        await query.edit_message_text("⚙ *Configure Default Palette Size Settings:*", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        
    elif query.data.startswith("set_"):
        _, param, val = query.data.split("_")
        await database.update_setting(uid, "palette_size", int(val))
        await query.message.reply_text(f"✅ Default palette export size saved as: `{val}` colors.", parse_mode="Markdown")
        
    elif query.data == "go_home":
        await query.edit_message_text("Select an option below to begin exploring colors:", reply_markup=get_main_menu())
        
    elif query.data == "menu_help":
        await help_cmd(update, context)
        
    return MENU_CHOICE

async def handle_image_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    photo = update.message.photo[-1] if update.message.photo else (update.message.document if update.message.document and update.message.document.mime_type.startswith("image/") else None)
    
    if not photo:
        await update.message.reply_text("❌ Unsupported asset type. Please upload a valid image file.")
        return MENU_CHOICE
        
    status = await update.message.reply_text("⏳ Running K-Means pixel clustering profiles across the canvas layers...")
    
    tg_file = await context.bot.get_file(photo.file_id)
    input_path = os.path.join(utils.TEMP_DIR, f"user_{uid}_src.png")
    await tg_file.download_to_drive(input_path)
    
    settings = await database.get_settings(uid)
    palette = color_extractor.extract_palette(input_path, num_colors=settings['palette_size'])
    
    if palette:
        preview_path = os.path.join(utils.TEMP_DIR, f"user_{uid}_card.png")
        if palette_generator.draw_palette_preview(palette, preview_path):
            # Compile text log
            report_lines = ["🎨 *Extracted Dominant Color Palette Details:*", ""]
            for idx, c in enumerate(palette):
                report_lines.append(
                    f"*{idx+1}. Color {c['hex']}*\n"
                    f"└ RGB: `{c['rgb']}` | Coverage: `{c['coverage']}%`\n"
                    f"└ CMYK: `{c['cmyk']}` | HSL: `{c['hsl']}`"
                )
                
            css_snippet = palette_generator.generate_export_format(palette, "css")
            report_lines.append(f"\n📋 *CSS Code Variables Asset:*\n```css\n{css_snippet}\n```")
            
            with open(preview_path, 'rb') as f:
                await update.message.reply_photo(photo=f, caption="\n".join(report_lines), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Failed to compile the color swatch preview card.")
    else:
        await update.message.reply_text("❌ Analysis execution error. Image structure cannot be processed.")
        
    utils.clear_user_cache(uid)
    await status.delete()
    return MENU_CHOICE

def main():
    if not TOKEN:
        print("Fatal error: Missing BOT_TOKEN environment key data mapping config profile.")
        return
        
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(menu_router, pattern="^menu_")
        ],
        states={
            MENU_CHOICE: [CallbackQueryHandler(menu_router, pattern="^(menu_|go_home|set_)")],
            AWAITING_IMAGE: [MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image_analysis)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    application.add_handler(conv_handler)
    print("ColorSense Bot operational threads polling...")
    application.run_polling()

if __name__ == '__main__':
    main()

