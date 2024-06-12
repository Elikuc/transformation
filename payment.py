import yookassa
from yookassa import Payment
from config import ACCOUNT_ID, SECRET_KEY
import logging
from requests.exceptions import HTTPError

yookassa.Configuration.account_id = ACCOUNT_ID
yookassa.Configuration.secret_key = SECRET_KEY

logging.basicConfig(level=logging.INFO)

def create(amount, chat_id):
    try:
        logging.info("Creating payment...")
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/transformationpayment_bot"
            },
            'capture': True,
            'metadata': {
                'chat_id': chat_id
            },
            'description': 'Описание товара...',
            'receipt': {
                'items': [
                    {
                        'description': 'Название товара 1',
                        'quantity': '1.00',
                        'amount': {
                            'value': str(amount),
                            'currency': 'RUB'
                        },
                        'vat_code': '1',
                        'payment_subject': 'commodity',
                        'payment_mode': 'full_payment'
                    }
                ],
                'email': 'example@example.com'
            }
        })
        logging.info(f"Payment created: {payment.id}")
        return payment.confirmation.confirmation_url, payment.id
    except HTTPError as e:
        logging.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        raise

def check(payment_id):
    try:
        logging.info(f"Checking payment status for {payment_id}")
        payment = Payment.find_one(payment_id)
        logging.info(f"Payment status: {payment.status}")
        if payment.status == 'succeeded':
            logging.info("Payment succeeded")
            return payment.metadata
        else:
            logging.info("Payment not succeeded")
            return False
    except HTTPError as e:
        logging.error(f"HTTP Error while checking payment: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        raise
