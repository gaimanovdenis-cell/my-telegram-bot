import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

import os
TOKEN = os.environ.get("BOT_TOKEN")

# Инициализация бота с учетом обновлений aiogram 3.7+
# Теперь parse_mode передается через DefaultBotProperties
bot = Bot(
    token=TOKEN, 
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# Класс состояний для FSM
class FormStates(StatesGroup):
    waiting_for_command = State()
    waiting_for_reason = State()
    waiting_for_nicks = State()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    text = (
        "👋 <b>Привет! Я бот-помощник для администраторов.</b>\n"
        "Я автоматизирую создание форм для блокировок.\n\n"
        "Введите команду для наказания (например, /bot, /permban или /ban):"
    )
    await message.answer(text)
    await state.set_state(FormStates.waiting_for_command)

@dp.message(FormStates.waiting_for_command)
async def process_command(message: Message, state: FSMContext):
    """Обработчик ввода команды"""
    command = message.text.strip()
    await state.update_data(command=command)

    if command.lower() == "/bot":
        await message.answer("Введите никнеймы или ID аккаунтов через пробел:")
        await state.set_state(FormStates.waiting_for_nicks)
    else:
        await message.answer(f"Вы выбрали команду {command}. Теперь введите причину:")
        await state.set_state(FormStates.waiting_for_reason)

@dp.message(FormStates.waiting_for_reason)
async def process_reason(message: Message, state: FSMContext):
    """Обработчик ввода причины"""
    reason = message.text.strip()
    await state.update_data(reason=reason)
    await message.answer("Введите никнеймы или ID аккаунтов через пробел:")
    await state.set_state(FormStates.waiting_for_nicks)

@dp.message(FormStates.waiting_for_nicks)
async def process_nicks(message: Message, state: FSMContext):
    """Генерация финальных форм"""
    data = await state.get_data()
    command = data.get("command")
    reason = data.get("reason")
    nicks = message.text.split()
    
    if not nicks:
        await message.answer("Список пуст. Введите ники еще раз:")
        return

    forms = []
    if command.lower() == "/bot":
        for nick in nicks:
            forms.append(f"<code>{command} {nick}</code>")
        result = "\n".join(forms)
    else:
        for nick in nicks:
            # Сначала проверка имущества, потом само наказание
            block = f"<code>/get {nick}</code>\n<code>{command} {nick} {reason}</code>"
            forms.append(block)
        result = "\n\n".join(forms)

    try:
        await message.answer(result)
        await message.answer(
            f"✅ Сгенерировано форм: {len(nicks)}.\n"
            "Введите новую команду для следующей партии:"
        )
        await state.set_state(FormStates.waiting_for_command)
    except Exception as e:
        await message.answer("Ошибка: сообщение слишком длинное. Попробуйте ввести меньше ников за раз.")

async def main():
    print("Бот успешно запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
