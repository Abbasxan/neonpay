"""
Прямое сравнение: ваш текущий код vs NEONPAY
"""

# ========== ВАША ТЕКУЩАЯ РЕАЛИЗАЦИЯ ==========
"""
@router.pre_checkout_query() 
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery): 
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.successful_payment) 
async def successful_payment_handler(message: Message): 
    try: 
        payload_data = json.loads(message.successful_payment.invoice_payload) 
        payment_type = payload_data.get("type") 
        user_id = payload_data.get("user_id", message.from_user.id) 
        amount = payload_data.get("amount", 0) 
        
        if payment_type == "verification": 
            await process_verification_payment(user_id, message, lang_code) 
        elif payment_type == "topup": 
            await process_topup_payment(user_id, amount, currency, lang_code, message)
    except Exception as e: 
        logging.error(f"Error: {e}")

async def process_verification_payment(user_id, message, lang_code):
    # 30+ строк кода для обработки верификации
    
async def process_topup_payment(user_id, amount, currency, lang_code, message): 
    # 40+ строк кода для обработки пополнения
"""

# ========== С NEONPAY API ==========

from neonpay import NeonPay

# Инициализация
neonpay = NeonPay.create_for_aiogram(bot)

# Отправка инвойса (1 строка вместо создания сложного payload)
stage = neonpay.create_payment_stage("Верификация", "Получить доступ", 50, {"type": "verification"})
await neonpay.send_invoice(chat_id, stage)

# Обработка платежей (автоматически обрабатывает pre_checkout и successful_payment)
@neonpay.on_successful_payment
async def handle_payment(result):
    if result.payload["type"] == "verification":
        await update_user_verification_status(result.user_id, verified=True)
    elif result.payload["type"] == "topup":
        await update_user_balance(result.user_id, result.amount)

# ВСЁ! Больше никакого кода не нужно!
