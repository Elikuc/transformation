import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TOKEN
from payment import create, check

logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Ссылки для каждого тарифа
TARIFF_LINKS = {
    'try': "https://t.me/+q3hQOd6UmfNlMDgy",
    'basic': "https://t.me/+cDkzwHwOBPtkYmUy",
    'vip': "https://t.me/+d8X2G0TSxHY0ZWNi"
}


@router.message(Command(commands=['start']))
async def start_handler(message: Message):
    logging.info(f"Received /start command from user {message.from_user.id}")
    try:
        await message.answer(
            'Привет🩷 Я рада тебя видеть здесь, на пути к Превращению!) '
            'Чтобы стать лучшей версией себя и научиться красиво танцевать, я предлагаю тебе ниже выбрать тариф по которому ты хочешь заниматься✨ '
            'До встречи на 💖«ПРЕВРАЩЕНИИ»!💖',
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(text="Тариф «Я попробую»", callback_data="choose_try"),
                        types.InlineKeyboardButton(text="Тариф «Базовый»", callback_data="choose_basic"),
                        types.InlineKeyboardButton(text="Тариф «VIP»", callback_data="choose_vip")
                    ]
                ]
            )
        )
    except Exception as e:
        logging.error(f"Error in start_handler: {e}")


@router.callback_query(lambda c: c.data.startswith('choose_'))
async def choose_tariff_handler(callback: types.CallbackQuery):
    logging.info(f"Received tariff choice: {callback.data} from user {callback.from_user.id}")
    try:
        tariff_mapping = {
            'choose_try': ('try', 1),
            'choose_basic': ('basic', 5990),
            'choose_vip': ('vip', 7990)
        }
        tariff_key, tariff_price = tariff_mapping.get(callback.data, (None, None))
        if tariff_key is None:
            logging.error(f"Invalid tariff key: {callback.data}")
            return

        payment_url, payment_id = create(tariff_price, callback.message.chat.id)

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text='Оплатить',
            url=payment_url
        ))
        builder.add(types.InlineKeyboardButton(
            text='Проверить оплату',
            callback_data=f'check_{payment_id}_{tariff_key}'
        ))

        await callback.message.answer(
            f"Счет сформирован! Стоимость выбранного тарифа: {tariff_price} ₽",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logging.error(f"Error in choose_tariff_handler: {e}")
        await callback.message.answer(f"Произошла ошибка при создании платежа: {str(e)}")
    finally:
        await callback.answer()


@router.callback_query(lambda c: 'check' in c.data)
async def check_handler(callback: types.CallbackQuery):
    logging.info(f"Received check payment request: {callback.data} from user {callback.from_user.id}")
    payment_id, tariff_key = callback.data.split('_')[1:]
    result = check(payment_id)
    if result:
        await callback.message.answer(f'Оплата прошла успешно! Вот ваша ссылка: {TARIFF_LINKS[tariff_key]}')
    else:
        await callback.message.answer('Оплата пока не прошла или возникла ошибка')
    await callback.answer()


async def main():
    logging.info("Starting bot polling...")
    await dp.start_polling(bot, skip_updates=False)


if __name__ == '__main__':
    asyncio.run(main())
