import telebot
from telebot.types import Message
from telebot import types
import requests
import random
import dropbox

DROPBOX_TOKEN = 'pJ2iewDilZAAAAAAAAAADCRMJ7QQV6Z7U7R7TZwxC8-KkxSwVJvExcYuCGKKFq8C'
BOT_TOKEN = '878439822:AAEsyy-5dd4PJJG3zleTPSsr5GO3YbY8Ne8'
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/'

dbx = dropbox.Dropbox(DROPBOX_TOKEN)
bot = telebot.TeleBot(BOT_TOKEN)

# Ответ на команду /start
@bot.message_handler(commands=['start'])
def handle_start_help(message: Message):
	bot.reply_to(message, 'Привет✋\nЯ бот, который может напечатать твои файлы весом до 20 Мб\n')
	markup = types.ReplyKeyboardMarkup()
	markup.resize_keyboard = True
	btnGetFile = types.KeyboardButton('Напечатать файл🖨')
	btnGetPhoto = types.KeyboardButton('Напечатать фотографию🖼')
	markup.row(btnGetFile, btnGetPhoto)
	bot.send_message(message.chat.id, "Что Вам угодно, сударь?", reply_markup=markup)

# Ответ на команду /developer
@bot.message_handler(commands=['developer'])
def handle_developer(message: Message):
	bot.reply_to(message, 'По всем вопросам и предложениям писать @Fleshgod')

# Ответ на нажатие кнопки напечатать файл
@bot.message_handler(func=lambda message: (str(message.text).upper() == 'НАПЕЧАТАТЬ ФАЙЛ🖨') | (str(message.text).upper() == 'ФАЙЛ') | (str(message.text).upper() == 'НАПЕЧАТАТЬ ФАЙЛ') | (str(message.text) == '🖨'), content_types=['text'])
def handle_text_doc(message):
	bot.reply_to(message, 'Отлично!\nПросто отправь мне файл размером до 20 Мб и я отправлю его на печать☺️')
	if(random.randint(1, 10) > 5):
		bot.send_message(message.chat.id, '⚠_️Но не забывай про одно строгое правило:_⚠️\n_курсачи и дипломы обязательно скидывать в защитных контейнерах - попадание воды в принтер может ему навредить!_😂', parse_mode="Markdown")

# Ответ на нажатие кнопки напечатать фото
@bot.message_handler(func=lambda message: (str(message.text).upper() == 'НАПЕЧАТАТЬ ФОТОГРАФИЮ🖼') | (str(message.text).upper() == 'ФОТОГРАФИЮ') | (str(message.text).upper() == 'ФОТОГРАФИЯ') | (str(message.text).upper() == 'НАПЕЧАТАТЬ ФОТОГРАФИЮ') | (str(message.text) == '🖼') | (str(message.text).upper() == 'ФОТО'), content_types=['text'])
def handle_text_photo(message):
	bot.reply_to(message, 'Понял-принял!\nОтправь мне фотографию файлом или картинкой и я отправлю ее на печать☺️')


# Отправка документа на печать
@bot.message_handler(content_types=['document'])
def handle_doc(message: Message):
	if(message.document.file_size > 20971520):
		bot.reply_to(message, 'Не, брат, это слишком много. На вот, попробуй, авось поможет')
		largeFilePhoto = open('large_file.jpg', 'rb')
		bot.send_photo(message.chat.id, largeFilePhoto)
	else:
		path = '/PrintQueue/' + message.document.file_id + '___' + message.from_user.first_name + '___' + message.document.file_name 
		file_info = bot.get_file(message.document.file_id)
		downloaded_file = bot.download_file(file_info.file_path)
		with open(path,'wb') as new_file:
			dbx.files_upload(downloaded_file, path)
		bot.reply_to(message, "Файл успешно отправлен на печать👍\nID вашего заказа: " + "```" + str(message.document.file_id) + "```" + "\n\n_*ID можно легко скопировать_", parse_mode="Markdown")

# Отправка фото на печать
@bot.message_handler(content_types=['photo'])
def handle_photo(message: Message):
	file_id = message.photo[-1].file_id
	file_info = bot.get_file(file_id)
	fileName = str(file_info.file_path).find('/')
	path = '/PrintQueue/' + file_id + '___' + message.from_user.first_name + file_info.file_path[fileName+1:]
	downloaded_file = bot.download_file(file_info.file_path)
	with open(path,'wb') as new_file:
		dbx.files_upload(downloaded_file, path)
	bot.reply_to(message, "Фото успешно отправлено на печать👍\nID вашего заказа: " + "```" + str(message.photo[-1].file_id) + "```" + "\n\n_*ID можно легко скопировать_", parse_mode="Markdown")

# Handles all sent video files
@bot.message_handler(content_types=['video', 'video_note'])
def handle_video(message: Message):
	bot.reply_to(message, "Прости, дружище, занят - потом обязательно гляну.\nP.S. Если есть что распечатать - обращайся)")
	bot.forward_message(467167935, message.chat.id, message.message_id)

# Handles all sent audio files
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message: Message):
	bot.reply_to(message, "Прости, дружище, занят - потом обязательно послушаю.\nP.S. Если есть что распечатать - обращайся)")
	bot.send_message(467167935, 'От: ' + message.from_user.first_name)
	bot.forward_message(467167935, message.chat.id, message.message_id)

# Handles all sent contacts
@bot.message_handler(content_types=['contact'])
def handle_contact(message: Message):
	bot.reply_to(message, "Это контактик какой-то красавицы?🤔\nЕсли да, то я обязательно передам его своему хозяину🙃\nP.S. Если есть что распечатать - обращайся)")
	bot.forward_message(467167935, message.chat.id, message.message_id)

# Handles all sent locations
@bot.message_handler(content_types=['location'])
def handle_location(message: Message):
	bot.reply_to(message, "Вау! Это что, локация где сегодня пройдет самая жаркая туса?🔥🔥🔥\nЯ передал хозяину) Он с Вами скоро свяжется😉\nP.S. Если есть что распечатать - обращайся)")
	bot.forward_message(467167935, message.chat.id, message.message_id)

# Handles all sent stickers
@bot.message_handler(content_types=['sticker'])
def handle_sticker(message: Message):
	bot.reply_to(message, "Аахахахах😂\nЧеткий стикер - будь я человеком, то слал бы его каждому)\nP.S. Если есть что распечатать - обращайся)")
	bot.send_message(467167935, 'От: ' + message.from_user.first_name)
	bot.forward_message(467167935, message.chat.id, message.message_id)

# Запасная функция, которая срабатывает при ошибке
@bot.message_handler(func=lambda message: True)
def send_default(message: Message):
	bot.reply_to(message, 'Не, дружище, ты не понял. У меня нет искуственного интелекта и поговорить со мной не получится😔\nНо распечатать твои файлы я могу😉\nДля начала работы введи /start')

bot.polling()
