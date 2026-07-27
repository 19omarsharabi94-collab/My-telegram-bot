import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# تفعيل التسجيل حتى نعرف إذا صار خطأ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# هذه الدالة تشتغل كل ما شخص يدز رسالة للبوت
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    # الرد اللي راح يجاوب بيه البوت
    await update.message.reply_text(f"أهلاً بك عيني {user_name}! تم إطلاق البوت بنجاح. قريباً راح نرفع الملازم هنا.")

if __name__ == '__main__':
    # هنا تحط التوكن مالتك اللي حصلناه قبل شوية
    TOKEN = "8659119267:AAEmmroAO8ikC9kYNuSpQlw2bMHfYMRxe-w"
    
    app = ApplicationBuilder().token(TOKEN).build()

    # ربط الرسائل بالدالة
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_message))

    print("البوت يعمل الآن...")
    app.run_polling()
