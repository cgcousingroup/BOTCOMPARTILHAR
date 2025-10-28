import time
import threading
import urllib.parse
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🔑 Token do seu bot
TOKEN = "8464960674:AAHac8qmO06W0AgYA94EGudbt7pLs5wR-Q8"

# 🔗 Link VIP
VIP_LINK = "https://t.me/+QkDedq4Tuf85ZGIx"

# 📁 Caminho da imagem local (deve estar na mesma pasta que este script)
IMAGE_PATH = Path(__file__).parent / "vip.jpg"

# 📢 Texto e link que o usuário vai compartilhar
SHARE_TEXT = "🎁 Olha esse conteúdo VIP que eu descobri!"
SHARE_URL = "https://t.me/vipgratisproibido_bot"  # altere para o link do seu bot ou canal

# 🔒 Codificação do texto e link para uso no Telegram
encoded_text = urllib.parse.quote(SHARE_TEXT)
encoded_url = urllib.parse.quote(SHARE_URL)

# 🔗 Link de compartilhamento formatado corretamente
SHARE_LINK = f"https://t.me/share/url?url={encoded_url}&text={encoded_text}"

# 📊 Armazenamento de progresso e verificação
user_progress = {}
last_click_time = {}  # armazena o tempo em que o usuário clicou em “compartilhar”


# --------------------- /start ---------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = 0

    text = (
        "🎉 <b>Bem-vindo ao VIP Novinhas Proibidas!</b>\n\n"
        "Você está prestes a liberar um conteúdo exclusivo 👑\n\n"
        "Para liberar o link VIP, compartilhe esta mensagem com <b>5 amigos</b>.\n\n"
        "Clique abaixo para começar 👇"
    )

    keyboard = [
        [InlineKeyboardButton("📤 Compartilhar com amigos", callback_data="share_now")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 📸 Envia a imagem local
    with open(IMAGE_PATH, "rb") as img:
        await update.message.reply_photo(
            photo=img,
            caption=text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )


# --------------------- Quando clicar em “📤 Compartilhar com amigos” ---------------------
async def share_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Salva horário do clique
    last_click_time[user_id] = time.time()

    # Mensagem informando que ele deve sair pra compartilhar
    await query.edit_message_caption(
        caption="📤 Selecione amigos na lista abaixo e compartilhe o conteúdo.\n\n"
                "Assim que enviar, volte aqui! Vamos verificar automaticamente.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📱 Abrir lista de contatos", url=SHARE_LINK)]]
        )
    )

    # Após 5 segundos, mostrar botão “Já compartilhei”
    def show_confirm_button():
        time.sleep(5)
        try:
            keyboard = [[InlineKeyboardButton("✅ Já compartilhei", callback_data="shared")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.application.create_task(
                query.edit_message_caption(
                    caption="👍 Já compartilhou com um amigo? Clique abaixo para confirmar 👇",
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            )
        except Exception as e:
            print("Erro ao atualizar mensagem:", e)

    threading.Thread(target=show_confirm_button).start()


# --------------------- Quando clicar em “✅ Já compartilhei” ---------------------
async def shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    now = time.time()
    last_time = last_click_time.get(user_id, 0)
    time_diff = now - last_time

    # Se o usuário clicou muito rápido, não conta
    if time_diff < 5:
        await query.edit_message_caption(
            caption="⚠️ Parece que você não chegou a compartilhar.\n"
                    "Tente novamente e espere alguns segundos após enviar aos amigos.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📤 Compartilhar novamente", callback_data="share_now")]]
            )
        )
        return

    # Caso válido — aumenta progresso
    progress = user_progress.get(user_id, 0) + 1
    user_progress[user_id] = progress

    if progress < 5:
        keyboard = [[InlineKeyboardButton("📤 Compartilhar com amigos", callback_data="share_now")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_caption(
            caption=f"📢 Compartilhamentos confirmados: {progress}/5\n\n"
                    "Continue compartilhando para liberar o acesso VIP 👑",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_caption(
            caption=f"🎉 Parabéns! Você completou 5 compartilhamentos!\n\n"
                    f"Aqui está seu acesso VIP 👇\n{VIP_LINK}",
            parse_mode="HTML"
        )


# --------------------- Main ---------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(share_now, pattern="^share_now$"))
    app.add_handler(CallbackQueryHandler(shared, pattern="^shared$"))

    print("🤖 Bot rodando com imagem local e texto de compartilhamento limpo...")
    app.run_polling()


# --------------------- Execução ---------------------
if __name__ == "__main__":
    main()
