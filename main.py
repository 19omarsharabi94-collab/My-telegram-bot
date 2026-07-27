import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import fitz  # PyMuPDF

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 1233989658  # استبدل هذا الرقم بمعرفك الصحيح
user_data = {}

# قاموس يربط كل مرحلة باسم ملف الـ PDF الخاص بها في المستودع
GRADE_FILES = {
    "سادس ابتدائي": "primary_6.pdf",
    "اول متوسط": "middle_1.pdf",
    "ثاني متوسط": "middle_2.pdf",
    "ثالث متوسط": "middle_3.pdf",
    "رابع اعدادي": "high_4.pdf",
    "خامس اعدادي": "high_5.pdf",
    "سادس اعدادي": "high_6.pdf"
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    markup = InlineKeyboardMarkup(row_width=1)
    for grade_name in GRADE_FILES.keys():
        markup.add(InlineKeyboardButton(f"📚 {grade_name}", callback_data=f"grade_{grade_name}"))
        
    markup.add(InlineKeyboardButton("📢 قناة الاستاذ عمر الفارس", url="https://t.me/your_channel"))
    
    welcome_text = f"أهلاً بك عزيزي {user_name} 🌹\nيرجى اختيار المرحلة الدراسية:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("grade_"))
def grade_selected(call):
    grade = call.data.replace("grade_", "")
    user_data[call.from_user.id] = {"grade": grade, "step": "waiting_for_card"}
    
    bot.answer_callback_query(call.id, f"تم اختيار: {grade}")
    
    # تحديد السعر بناءً على المرحلة الدراسية
    if grade == "سادس اعدادي":
        price = "10,000 دينار"
    else:
        price = "5,000 دينار"
    
    sales_text = (
        f"📘 ملزمة (مساعد الطالب في اللغة الانكليزية) للصف ({grade})\n"
        "الملزمة شاملة ومترجمة بالكامل، وتغنيك عن المدرس الخصوصي\n\n"
        f"💰 سعر النسخة: {price}.\n"
        "طريقة الدفع:\n"
        "🔹 إرسال كارت رصيد (اسيا)\n\n"
        "📝 بعد التحويل، يرجى تزويدنا بـ:\n"
        "1️⃣ الاسم الرباعي للطالب\n"
        "2️⃣ رقم الهاتف\n"
        "3️⃣ اسم المدرسة\n"
        "سيتم طباعة هذه المعلومات على الملزمة\n\n"
        "📌 ملاحظة: الملزمة (PDF) يتم إرسالها مباشرة بعد تأكيد الدفع.\n"
        "مع تمنياتنا بالتوفيق 🌹\n\n"
        "👉 **الرجاء الآن إرسال صورة كارت الرصيد (أسيا)**:"
    )
    bot.send_message(call.message.chat.id, sales_text)

@bot.message_handler(content_types=['photo'])
def handle_card_photo(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get("step") == "waiting_for_card":
        user_data[user_id]["card_photo"] = message.photo[-1].file_id
        user_data[user_id]["step"] = "waiting_for_info"
        bot.reply_to(message, "✅ تم استلام صورة الكارت بنجاح.\n\nالرجاء الآن إرسال معلوماتك بثلاثة أسطر أو برسالة واحدة:\n(الاسم الرباعي، رقم الهاتف، اسم المدرسة)")
    else:
        bot.reply_to(message, "الرجاء الضغط على /start أولاً لاختيار المرحلة.")

@bot.message_handler(func=lambda message: True)
def handle_text_info(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get("step") == "waiting_for_info":
        info_text = message.text
        user_data[user_id]["info"] = info_text
        user_data[user_id]["step"] = "completed"
        
        grade = user_data[user_id]["grade"]
        
        bot.reply_to(message, "⏳ تم إرسال طلبك ومعلوماتك إلى الأستاذ عمر الفارس للمراجعة وسيتم إرسال الملزمة فور التأكيد 🌹")
        
        admin_notification = (
            f"🔔 طلب شراء جديد!\n\n"
            f"👤 الطالب: {message.from_user.first_name} (ID: {user_id})\n"
            f"📚 الصف: {grade}\n"
            f"📝 المعلومات:\n{info_text}"
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ موافقة وإرسال الملزمة", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")
        )
        
        bot.send_photo(ADMIN_ID, user_data[user_id]["card_photo"], caption=admin_notification, reply_markup=markup)

def add_watermark_to_pdf(input_pdf_path, output_pdf_path, watermark_text):
    doc = fitz.open(input_pdf_path)
    for page in doc:
        rect = page.rect
        point = fitz.Point(rect.width - 200, rect.height - 30)
        page.insert_text(point, watermark_text, fontsize=10, color=(0, 0, 1), fill_opacity=0.12)
    doc.save(output_pdf_path)
    doc.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def admin_decision(call):
    data_parts = call.data.split("_")
    action = data_parts[0]
    target_user_id = int(data_parts[1])
    
    if action == "approve":
        bot.answer_callback_query(call.id, "تمت الموافقة.")
        bot.send_message(target_user_id, "🎉 تم تأكيد الدفع والموافقة على طلبك!\nجاري إعداد نسختك الخاصة من الملزمة...")
        
        user_info = user_data.get(target_user_id, {})
        grade = user_info.get("grade")
        student_info = user_info.get("info", "معلومات الطالب")
        
        original_pdf = GRADE_FILES.get(grade)
        output_pdf = f"personalized_{target_user_id}.pdf"
        
        if original_pdf and os.path.exists(original_pdf):
            add_watermark_to_pdf(original_pdf, output_pdf, student_info)
            
            with open(output_pdf, "rb") as pdf_file:
                bot.send_document(target_user_id, pdf_file, caption=f"📘 إليك نسختك الخاصة من ملزمة ({grade}) مع معلوماتك الشخصية. شكراً لثقتك بنا 🌹")
            
            os.remove(output_pdf)
        else:
            bot.send_message(target_user_id, "عذراً، حدث خطأ في ملف الملزمة المطلوبة، يرجى مراجعة الإدارة.")
            bot.send_message(ADMIN_ID, f"⚠️ تنبيه: ملف الـ PDF الخاص بـ ({grade}) غير موجود في المستودع!")

        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n✅ **[تمت الموافقة وإرسال الملزمة آلياً]**")
        
    elif action == "reject":
        bot.answer_callback_query(call.id, "تم رفض الطلب.")
        bot.send_message(target_user_id, "عذراً، لم يتم التأكد من كارت الرصيد أو المعلومات المرسلة، يرجى التأكد والمحاولة لاحقاً.")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n❌ **[تم رفض الطلب]**")

print("Bot is running perfectly...")
bot.infinity_polling()
