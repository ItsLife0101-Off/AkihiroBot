from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberStatus
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Токен твоего бота
API_TOKEN = '7747777900:AAFGR9zocLqCHmGyXwOWimscqvZip3gNI04'

# Создаем объекты бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# Команда для жалобы на пользователя с указанием причины
@dp.message_handler(commands=['report'], commands_prefix='!')
async def report_command(message: types.Message):
    # Проверяем, есть ли сообщение, на которое жалуются
    if not message.reply_to_message:
        await message.reply("Команда должна быть ответом на сообщение пользователя, на которого жалуются.")
        return
    
    # Получаем текст после команды как причину
    reason = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not reason:
        await message.reply("Пожалуйста, укажите причину жалобы после команды.")
        return

    reported_user = message.reply_to_message.from_user

    # Отправляем жалобу администраторам группы
    admin_list = await bot.get_chat_administrators(message.chat.id)
    for admin in admin_list:
        # Отправляем сообщение только настоящим пользователям, исключая ботов
        if admin.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] and not admin.user.is_bot:
            await bot.send_message(admin.user.id, f"Жалоба на пользователя: {reported_user.full_name}\nПричина: {reason}")

    await message.reply("Жалоба отправлена администраторам.")

# Команда для администраторов, чтобы забанить пользователя с указанием причины
@dp.message_handler(commands=['ban'], commands_prefix='!')
async def ban_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Команда должна быть ответом на сообщение пользователя, которого хотите забанить.")
        return
    
    # Проверяем, является ли пользователь администратором
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply("У вас нет прав на использование команды бан.")
        return
    
    # Получаем текст после команды как причину бана
    reason = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not reason:
        await message.reply("Пожалуйста, укажите причину бана после команды.")
        return

    user_to_ban = message.reply_to_message.from_user

    # Забанить пользователя
    await bot.kick_chat_member(message.chat.id, user_to_ban.id)

    # Отправляем сообщение об успешном бане
    await message.reply(f"Пользователь {user_to_ban.full_name} был забанен.\nПричина: {reason}")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
