from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.filters import CommandStart,  Command
import requests
from aiogram import F

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder

Bot_token = #########
VK_token = #########

bot = Bot(Bot_token)
dp = Dispatcher()

langs_API = {
    'english': 'en',
    'español': 'es',
    'português': 'pt',
    'русский': 'ru'
}
langs_emodji = {
    'ru': '🇷🇺',
    'en':  '🇬🇧',
    'es': '🇪🇸',
    'pt': '🇵🇹'
}

global from_lang
from_lang = ''

global to_lang
to_lang = ''

rev_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Поменять языки местами ↔', callback_data='реверс')
    ],
    [
        InlineKeyboardButton(text='Выбрать языки заново ↻', callback_data='заново')
    ]
])


@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(text=f'Здорова, чепушила: {message.from_user.username}')


@dp.message(Command('help'))
async def help_command(message: types.Message):
    await message.answer(text='''
Я не знаю, что делаю в этой жизни...
Ну а вообще я переводчик, правда знаю всего 4 языка))''')

@dp.message(Command('translate'))
async def transl_command(message: types.Message):
    Buttons = [
        [
            KeyboardButton(text='русский 🇷🇺'),
            KeyboardButton(text='english 🇬🇧')],
            [KeyboardButton(text='español 🇪🇸'),
            KeyboardButton(text='português 🇵🇹')
        ],
    ]
    langs = ReplyKeyboardMarkup(keyboard=Buttons, resize_keyboard=True, one_time_keyboard=True,  input_field_placeholder="Выберите язык")
    await message.answer(text='Окей, с какого языка будем переводить?', reply_markup=langs, )




@dp.message()
async def to_lang(message: types.Message):
    global from_lang
    global to_lang

    if message.text == 'русский 🇷🇺':
        from_lang = str(langs_API[message.text[:-3]])
        Buttons = [
            [
                KeyboardButton(text='english 🫖'),
                KeyboardButton(text='español 🦬'),
                KeyboardButton(text='português ⚽')
            ],
        ]
        langs = ReplyKeyboardMarkup(keyboard=Buttons, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выберите язык")
        await message.answer(text='На какой язык будем переводить?', reply_markup=langs, )

    elif message.text == 'english 🫖' or message.text == 'español 🦬' or message.text == 'português ⚽':
        to_lang = str(langs_API[message.text[:-2]])
        await message.answer(text='Хорошо, введи текст')

    elif message.text == 'english 🇬🇧' or message.text == 'español 🇪🇸' or message.text == 'português 🇵🇹':
        from_lang = str(langs_API[message.text[:-3]])
        to_lang = 'ru'
        await message.answer(text='Значит переводим на русский)\nХорошо, введи текст')

    else:
        try:
            response = requests.get('https://api.vk.com/method/translations.translate',
                                    params={
                                        'access_token': VK_token,
                                        'v': 5.154,
                                        'texts': message.text,
                                        'translation_language': str(from_lang + '-' + to_lang)
                                    }
                                    )

            data = response.json()
            output = str(', '.join(data['response']['texts']))
            output = output.replace('..', '')
            final_output = ''
            #форматируем финанльный output
            for i in range(len(output)):
                if output[i-2] == ',' or output[i-2] == '-':
                    final_output += output[i].lower()
                else:
                    final_output += output[i]


        #делаем кнопки реверса
            await message.answer(final_output, reply_markup=rev_markup)

        except KeyError:
            await message.answer('Подожди, превышен лимит переводов в минуту')


@dp.callback_query(F.data.in_(['реверс']))
async def process_buttons_press(callback: types.CallbackQuery):
    global from_lang
    global to_lang

    help = from_lang
    from_lang = to_lang
    to_lang = help


    await callback.answer(f'Вы поменяли язык\n{langs_emodji[from_lang]} - {langs_emodji[to_lang]}')

@dp.callback_query(F.data.in_(['заново']))
async def process_buttons_press(callback: types.CallbackQuery):
    await callback.answer('Выбрать языки заново')
    choose_again_lang = [
        [
            KeyboardButton(text='/translate')
        ]
    ]
    again_keyboard = ReplyKeyboardMarkup(keyboard=choose_again_lang, resize_keyboard=True, one_time_keyboard=True)
    await callback.message.answer(text='Нажмите на кнопку ⬇️', reply_markup=again_keyboard)





async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
