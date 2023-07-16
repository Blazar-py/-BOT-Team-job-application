from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

bot = Bot(token="TOKEN")          # token бота

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

admin_id = 123    # id админа

class UserState(StatesGroup):
    id_tg = State()
    nick = State()
    opit_worka = State()
    traffik = State()
    info = State()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Отправить заявку 🖊")
    button2 = types.KeyboardButton(text='Поддержка 👤')
    keyboard.add(button, button2)
    await message.answer('Бот написан @BlazarPython. Для взаимодействия с ботом - работайте с клавиатурой кнопок.', reply_markup=keyboard)

@dp.message_handler(content_types=['text'])
async def message(message):
    global id_tg
    id_tg = message.from_user.id
    all_id = open("all_id.txt", "r", encoding="utf-8")
    if message.text == 'Отправить заявку 🖊':
        if str(id_tg) not in all_id.read():
            await message.answer("Напишите как с вами можно связаться?\nНик телеграмма / ссылка на профиль lolza...", reply_markup=types.ReplyKeyboardRemove())
            all_id = open("all_id.txt", "a", encoding="utf-8")
            all_id.write(str(f"{id_tg}\n"))
            all_id.close()
            await UserState.nick.set()
        else:
            await message.answer('Вы уже подавали заявку! Ожидайте вердикта от админа')
    elif message.text == 'Поддержка 👤':
        await message.answer("Поддержка: @BlazarPython")

@dp.message_handler(state=UserState.nick)
async def get_nick(message: types.Message, state: FSMContext):
    await state.update_data(nick=message.text)
    await message.answer("Напишите свой опыт работы.")
    await UserState.opit_worka.set()

@dp.message_handler(state=UserState.opit_worka)
async def get_nick(message: types.Message, state: FSMContext):
    await state.update_data(opit_worka=message.text)
    await message.answer("Напишите источник траффика.")
    await UserState.traffik.set()

@dp.message_handler(state=UserState.traffik)
async def get_nick(message: types.Message, state: FSMContext):
    await state.update_data(traffik=message.text)
    await message.answer("Напишите доп. информацию по желанию.")
    await UserState.info.set()

@dp.message_handler(state=UserState.info)
async def get_info(message: types.Message, state: FSMContext):
    if message.text == 'Поддержка 👤':
        await message.answer("Поддержка: @BlazarPython")
    elif message.text == 'Отправить заявку 🖊':
        await message.answer('Вы уже подавали заявку! Ожидайте вердикта от админа')
    else:
        global nick_name
        await state.update_data(info=message.text)
        await state.update_data(id_tg=message.from_user.id)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton(text="Отправить заявку 🖊")
        button2 = types.KeyboardButton(text='Поддержка 👤')
        keyboard.add(button, button2)
        await message.answer("Ваша заявка была отправлена администраторам на проверку.\nОжидайте вынесения вердикта 🕣", reply_markup=keyboard)
        data = await state.get_data()
        nick_name = data['nick']
        inlinekeyboard = types.InlineKeyboardMarkup()
        inlinekeyboard.add(types.InlineKeyboardButton(text="Принять ☑", callback_data="accept"), types.InlineKeyboardButton(text="Отклонить ❌", callback_data="deny"))
        await bot.send_message(admin_id, f"❗ Пришла новая заявка от {data['nick']}. "
                                         f"\n\nОпыт работы кандидата: {data['opit_worka']}"
                                         f"\nИсточник траффика: {data['traffik']}"
                                         f"\nДоп. информация от кандидата: {data['info']}", reply_markup=inlinekeyboard)
        await state.finish()

@dp.callback_query_handler(text="accept")
async def callback_inline(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Заявка была принята!\nСвязаться с кандидатом: {nick_name}')
    await call.bot.send_message(id_tg, 'Заявка была принята!')
    await call.answer()

@dp.callback_query_handler(text="deny")
async def send_all(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Заявка была отклонена!')
    await call.bot.send_message(id_tg, 'Заявка была принята!')
    await call.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)