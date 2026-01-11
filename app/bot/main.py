from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from uuid import uuid4

from app.utils.config import settings
from app.utils.logging import setup_logging
from app.db.database import (
    init_db,
    create_job,
    list_jobs,
    set_cancel,
    count_active_jobs,
    update_job,
    get_job,
)
import json
from app.core.cleanup import delete_outputs
from app.utils.telegram import send_results
from app.workers.tasks import enqueue_job

logger = setup_logging("bot")

MENU = [
    [InlineKeyboardButton("🎬 Buat Shorts Baru", callback_data="menu:new")],
    [InlineKeyboardButton("⚙️ Pengaturan Default", callback_data="menu:settings")],
    [InlineKeyboardButton("📦 Preset", callback_data="menu:presets")],
    [InlineKeyboardButton("🧾 Riwayat Job", callback_data="menu:history")],
    [InlineKeyboardButton("❓ Bantuan", callback_data="menu:help")],
]

DEFAULT_OPTIONS = {
    "clip_count": 2,
    "duration": "18-35",
    "captions": True,
    "caption_style": "boxed",
    "smart_crop": True,
    "hook_mode": "balanced",
    "language": "auto",
    "watermark": "",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Selamat datang! Pilih menu:",
        reply_markup=InlineKeyboardMarkup(MENU),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Gunakan tombol menu untuk mulai. /status <job_id>")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Gunakan /status <job_id>")
        return
    await update.message.reply_text(f"Cek status job: {context.args[0]}")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Gunakan /cancel <job_id>")
        return
    set_cancel(context.args[0])
    await update.message.reply_text("Job dibatalkan.")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    jobs = list_jobs(str(update.effective_user.id))
    if not jobs:
        await update.message.reply_text("Belum ada riwayat.")
        return
    text = "\n".join(f"{job['id']} - {job['status']}" for job in jobs)
    await update.message.reply_text(text)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Pengaturan default via menu tombol.")


def _config_keyboard(options: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Jumlah clip: 1", callback_data="set:clip_count:1"),
                InlineKeyboardButton("2", callback_data="set:clip_count:2"),
                InlineKeyboardButton("3", callback_data="set:clip_count:3"),
                InlineKeyboardButton("4", callback_data="set:clip_count:4"),
                InlineKeyboardButton("5", callback_data="set:clip_count:5"),
            ],
            [
                InlineKeyboardButton("Durasi 12–25s", callback_data="set:duration:12-25"),
                InlineKeyboardButton("18–35s", callback_data="set:duration:18-35"),
                InlineKeyboardButton("25–45s", callback_data="set:duration:25-45"),
            ],
            [
                InlineKeyboardButton("Captions ON", callback_data="set:captions:1"),
                InlineKeyboardButton("Captions OFF", callback_data="set:captions:0"),
            ],
            [
                InlineKeyboardButton("BOXED", callback_data="set:caption_style:boxed"),
                InlineKeyboardButton("MINIMAL", callback_data="set:caption_style:minimal"),
                InlineKeyboardButton("TIKTOK", callback_data="set:caption_style:tiktok"),
            ],
            [
                InlineKeyboardButton("Smart Crop ON", callback_data="set:smart_crop:1"),
                InlineKeyboardButton("Smart Crop OFF", callback_data="set:smart_crop:0"),
            ],
            [
                InlineKeyboardButton("Hook AGGRESSIVE", callback_data="set:hook_mode:aggressive"),
                InlineKeyboardButton("BALANCED", callback_data="set:hook_mode:balanced"),
                InlineKeyboardButton("SAFE", callback_data="set:hook_mode:safe"),
            ],
            [
                InlineKeyboardButton("Lang AUTO", callback_data="set:language:auto"),
                InlineKeyboardButton("ID", callback_data="set:language:id"),
                InlineKeyboardButton("EN", callback_data="set:language:en"),
            ],
            [
                InlineKeyboardButton("Watermark Set", callback_data="step:watermark"),
                InlineKeyboardButton("Watermark Clear", callback_data="set:watermark:"),
            ],
            [
                InlineKeyboardButton("▶️ Lanjut", callback_data="step:preview"),
                InlineKeyboardButton("↩️ Kembali", callback_data="menu:start"),
                InlineKeyboardButton("❌ Batal", callback_data="menu:cancel"),
            ],
        ]
    )


def _preview_text(options: dict) -> str:
    return (
        "Preview konfigurasi:\n"
        f"Jumlah clip: {options['clip_count']}\n"
        f"Durasi: {options['duration']}\n"
        f"Captions: {'ON' if options['captions'] else 'OFF'} ({options['caption_style']})\n"
        f"Smart Crop: {'ON' if options['smart_crop'] else 'OFF'}\n"
        f"Hook mode: {options['hook_mode']}\n"
        f"Language: {options['language']}\n"
        f"Watermark: {options['watermark'] or '-'}"
    )


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "menu:new":
        context.user_data["wizard"] = {"state": "awaiting_url", "options": DEFAULT_OPTIONS.copy()}
        await query.edit_message_text(
            "Kirim URL YouTube.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="menu:cancel")]]),
        )
    elif data == "menu:settings":
        await query.edit_message_text("Pengaturan default (TODO)")
    elif data == "menu:presets":
        await query.edit_message_text("Preset contoh: Viral, Edukasi, Story")
    elif data == "menu:history":
        jobs = list_jobs(str(update.effective_user.id))
        if not jobs:
            await query.edit_message_text("Belum ada riwayat.")
            return
        text = "Riwayat job terakhir:"
        keyboard = []
        for job in jobs:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{job['id'][:6]} ({job['status']})",
                        callback_data=f"history:{job['id']}:details",
                    ),
                    InlineKeyboardButton("Resend", callback_data=f"history:{job['id']}:resend"),
                    InlineKeyboardButton("Delete", callback_data=f"history:{job['id']}:delete"),
                ]
            )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "menu:help":
        await query.edit_message_text("Gunakan tombol untuk membuat shorts.")
    elif data == "menu:cancel":
        context.user_data.pop("wizard", None)
        await query.edit_message_text("Dibatalkan.")
    elif data == "menu:start":
        await query.edit_message_text("Pilih menu:", reply_markup=InlineKeyboardMarkup(MENU))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    wizard = context.user_data.get("wizard")
    if data.startswith("cancel:"):
        job_id = data.split(":", 1)[1]
        set_cancel(job_id)
        await query.edit_message_text("Job dibatalkan.")
        return
    if data.startswith("history:"):
        _, job_id, action = data.split(":", 2)
        job = get_job(job_id)
        if not job:
            await query.edit_message_text("Job tidak ditemukan.")
            return
        if action == "details":
            await query.edit_message_text(f"Job {job_id} status: {job['status']}")
        elif action == "resend":
            result_json = job.get("result_json")
            if result_json:
                send_results(job_id, json.loads(result_json))
            await query.edit_message_text("Hasil dikirim ulang.")
        elif action == "delete":
            deleted = delete_outputs(job_id)
            await query.edit_message_text("Output dihapus." if deleted else "Output tidak ditemukan.")
        return
    if not wizard:
        return
    options = wizard["options"]
    if data.startswith("set:"):
        _, key, value = data.split(":", 2)
        if key in {"captions", "smart_crop"}:
            options[key] = value == "1"
        elif key in {"clip_count"}:
            options[key] = int(value)
        else:
            options[key] = value
        await query.edit_message_text("Konfigurasi diupdate.", reply_markup=_config_keyboard(options))
    elif data == "step:preview":
        await query.edit_message_text(
            _preview_text(options),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🚀 Proses Sekarang", callback_data="step:run")],
                    [InlineKeyboardButton("🧪 Test 1 Clip Dulu", callback_data="step:test")],
                    [InlineKeyboardButton("⚙️ Ubah Setting", callback_data="step:config")],
                    [InlineKeyboardButton("❌ Batal", callback_data="menu:cancel")],
                ]
            ),
        )
    elif data == "step:config":
        await query.edit_message_text("Konfigurasi:", reply_markup=_config_keyboard(options))
    elif data == "step:watermark":
        wizard["state"] = "awaiting_watermark"
        await query.edit_message_text("Kirim teks watermark.")
    elif data in {"step:run", "step:test"}:
        if count_active_jobs(str(update.effective_user.id)) >= settings.user_concurrency:
            await query.edit_message_text("Batas job aktif tercapai. Tunggu selesai.")
            return
        if data == "step:test":
            options = options | {"clip_count": 1}
        job_id = uuid4().hex
        options = options | {"url": wizard.get("url", "")}
        create_job(job_id, str(update.effective_user.id), options)
        enqueue_job(job_id)
        progress_message = await query.edit_message_text(
            f"Job {job_id} dibuat. Menunggu proses...",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⛔ Cancel Job", callback_data=f"cancel:{job_id}")]]),
        )
        options["telegram"] = {
            "chat_id": progress_message.chat_id,
            "message_id": progress_message.message_id,
        }
        update_job(job_id, options_json=json.dumps(options))
        context.user_data.pop("wizard", None)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wizard = context.user_data.get("wizard")
    if not wizard:
        return
    if wizard.get("state") == "awaiting_url":
        wizard["url"] = update.message.text.strip()
        wizard["state"] = "config"
        await update.message.reply_text("Konfigurasi:", reply_markup=_config_keyboard(wizard["options"]))
    elif wizard.get("state") == "awaiting_watermark":
        wizard["options"]["watermark"] = update.message.text.strip()
        wizard["state"] = "config"
        await update.message.reply_text("Watermark diset.", reply_markup=_config_keyboard(wizard["options"]))


def main() -> None:
    init_db()
    application = ApplicationBuilder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CallbackQueryHandler(handle_menu, pattern=r"^menu:"))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling()


if __name__ == "__main__":
    main()
