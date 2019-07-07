import telebot
from telebot.types import Message
from telebot import types
import requests
import random
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import re

# Tokens
DROPBOX_TOKEN = 'pJ2iewDilZAAAAAAAAAADCRMJ7QQV6Z7U7R7TZwxC8-KkxSwVJvExcYuCGKKFq8C'
BOT_TOKEN = '878439822:AAEsyy-5dd4PJJG3zleTPSsr5GO3YbY8Ne8'


# Initializing bots
dbx = dropbox.Dropbox(DROPBOX_TOKEN)
bot = telebot.TeleBot(BOT_TOKEN)


# variables
BOT_BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/'
ADMIN_ID = 467167935

local_data_path = 'data.txt'
dbx_data_path = '/data/data.txt'

items_in_DB_item = 3
index_of_id_in_DB = 0
index_of_username_in_DB = 1
index_of_dorm_in_DB = 2

dormitories = {
	'knu16': 'Общежитие №16 КНУ имени Тараса Шевченка',
	'kpi11': 'Общежитие №11 КПИ имени Игоря Сикорского'
}
with open(local_data_path, 'r') as f:
	content = f.read()
BDLines = content.split(';')


# Returns True if user is new
# Returns False if user already exists
def is_user_new(message):
	with open(local_data_path, 'r') as f:
		content = f.read()
	BDLines = content.split(';')
	NewUser = True

	for x in BDLines[:-1]:
		BDItem = x.split()
		if BDItem[index_of_id_in_DB] == str(message.chat.id):
			NewUser = False

	return NewUser

# Returns dormitory of user
def get_dormotory(message):
	if is_user_new(message):
		sent = bot.send_message(message.chat.id, "Для начала выбери в какой общаге ты хочешь печатать🖨\n\n*Список доступных общаг:*\n/knu16\n/kpi11", parse_mode="Markdown", reply_markup=markup)
		bot.register_next_step_handler(sent, set_user)
	else:
		with open(local_data_path, 'r') as f:
			content = f.read()
		BDLines = content.split(';')

		for x in BDLines[:-1]:
			BDItem = x.split()
			if BDItem[index_of_id_in_DB] == str(message.chat.id):
				return BDItem[index_of_dorm_in_DB]
	bot.send_message(ADMIN_ID, '⚠️⚠️⚠️ПРОБЛЕМА С БД! НЕ УДАЕТСЯ НАЙТИ ОБЩАГУ СУЩЕСТВУЮЩЕГО ПОЛЬЗОВАТЕЛЯ⚠️⚠️⚠️')


# Upload DB to dropbox
def backup_DB():
    with open(local_data_path, 'rb') as f:
        try:
            dbx.files_upload(f.read(), dbx_data_path, mode=WriteMode('overwrite'))
        except ApiError as err:
            bot.send_message(ADMIN_ID, '⚠️⚠️⚠️ПРОБЛЕМА С ЗАГРУЗКОЙ БД В ОБЛАКО⚠️⚠️⚠️')

# Add data to DB
# @param new_content is a string
def add_to_DB(new_content):
    with open(local_data_path, 'a+') as f:
        f.write(str(new_content)+';')
    backup_DB()

# Buttons
markup = types.ReplyKeyboardMarkup()
markup.resize_keyboard = True
btnGetFile = types.KeyboardButton('Напечатать файл🖨')
btnGetPhoto = types.KeyboardButton('Напечатать фотографию🖼')
btnSetDorm = types.KeyboardButton('Выбрать общагу🏣')
markup.row(btnGetFile, btnGetPhoto)
markup.row(btnSetDorm)

# Handles command /start
@bot.message_handler(commands=['start'])
def handle_start(message: Message):
	bot.reply_to(message, 'Привет✋\nЯ бот, который может напечатать твои файлы весом до 20 Мб')

	if is_user_new(message):
		sent = bot.send_message(message.chat.id, "Для начала выбери в какой общаге ты хочешь печатать🖨\n\n*Список доступных общаг:*\n/knu16\n/kpi11", parse_mode="Markdown", reply_markup=markup)
		bot.register_next_step_handler(sent, set_user)
	else:
		sent = bot.send_message(message.chat.id, "Выбери в какой общаге ты хочешь печатать🖨\n\n*Список доступных общаг:*\n/knu16\n/kpi11", parse_mode="Markdown", reply_markup=markup)
		bot.register_next_step_handler(sent, set_dormitory)

# Append user to data base
def set_user(message: Message):
	if str(message.content_type) == 'text':
		match = re.fullmatch(r'\/\w+\d+', message.text) 
		if match:
			success = False
			for key, value in dormitories.items():
				if (key == message.text[1:]):
					with open(local_data_path, 'r') as f:
						content = f.read()
					BDLines = content.split(';')
					with open(local_data_path, "w") as f:
						for line in BDLines[:-1]:
							if line.split()[0] != str(message.chat.id):
								f.write(str(line)+';')
					add_to_DB(str(message.chat.id) + " " + str(message.from_user.username) + " " + str(message.text[1:]))
					bot.reply_to(message, "Юху🙃\nЯ успешно все записал🙂\nТвоя текущая общага: " + value + "\n\nP.S. Ты всегда можешь поменять общагу для печати нажав на соответсвующую кнопку🏣")
					success = True
			if success == False:
				bot.reply_to(message, 'Выбери доступную общагу😡\nДля этого нажми на соответсвующую кнопку🏣')
		else:
			bot.reply_to(message, 'Выбери доступную общагу😡\nДля этого нажми на соответсвующую кнопку🏣')
	else:
		bot.reply_to(message, 'Выбери доступную общагу😡\nДля этого нажми на соответсвующую кнопку🏣')

# Update user's dormitory
def set_dormitory(message: Message):
	if str(message.content_type) == 'text':
		if is_user_new(message):
			sent = bot.send_message(message.chat.id, "Выбери в какой общаге ты хочешь печатать🖨\n\n*Список доступных общаг:*\n/knu16\n/kpi11", parse_mode="Markdown", reply_markup=markup)
			bot.register_next_step_handler(sent, set_user)
		else:
			success = False
			match = re.fullmatch(r'\/\w+\d+', message.text) 
			if match:
				for key, value in dormitories.items():
					if (key == message.text[1:]):
						with open(local_data_path, 'r') as f:
							content = f.read()
						BDLines = content.split(';')
						with open(local_data_path, "w") as f:
						    for line in BDLines[:-1]:
						        if line.split()[0] != str(message.chat.id):
						            f.write(str(line)+';')
						add_to_DB(str(message.chat.id) + " " + str(message.from_user.username) + " " + str(message.text[1:]))
						bot.reply_to(message, "Юху🙃\nЯ успешно все записал🙂\nТвоя текущая общага: " + value + "\n\nP.S. Ты всегда можешь поменять общагу для печати нажав на соответсвующую кнопку🏣")
						success = True
				if success == False:
					bot.reply_to(message, 'Выбери доступную общагу😡\nДля этого нажми на соответсвующую кнопку🏣')
			else:
				bot.reply_to(message, 'Выбери доступную общагу😡\nДля этого нажми на соответсвующую кнопку🏣')
	else:
		bot.reply_to(message, 'Выбери доступную общагу😡\nДля этого нажми на соответсвующую кнопку🏣')
		
# Handles command /developer
@bot.message_handler(commands=['developer'])
def handle_developer(message: Message):
	bot.reply_to(message, 'По всем вопросам и предложениям писать @Fleshgod', reply_markup=markup)

# Handles command /getchatid
@bot.message_handler(commands=['getchatid'])
def handle_getchatid(message: Message):
	bot.reply_to(message, 'ID вашего чата: ```' + str(message.chat.id) + '```' + '\n\n_*ID можно легко скопировать_', parse_mode="Markdown", reply_markup=markup)

# Handles command /donate
@bot.message_handler(commands=['donate'])
def handle_donate(message: Message):
	bot.reply_to(message, 'Привет✋\nХочешь помочь разработчику с улучшением этого проекта и ускорить появление такого же принтера в своей общаге?🏣\nМожешь пожертвовать свои кровно заработанные на эти карты:\nПриват: ' + '```4149499109769909```' + '\nМоно:' + '```5375414108279679```' + '\nВ комментарии к платежу напиши свои пожелания или номер общежития в котором ты бы хотел тоже запустить чудо-принтер.🖨\nБудем благодарны тебе за любой вклад в наш проект.💵', parse_mode="Markdown", reply_markup=markup)

# Handles button print file
@bot.message_handler(func=lambda message: (str(message.text).upper() == 'НАПЕЧАТАТЬ ФАЙЛ🖨') | (str(message.text).upper() == 'ФАЙЛ') | (str(message.text).upper() == 'НАПЕЧАТАТЬ ФАЙЛ') | (str(message.text) == '🖨'), content_types=['text'])
def handle_text_doc(message):
	if is_user_new(message):
		sent = bot.send_message(message.chat.id, "Для начала работы с ботом выбери в какой общаге ты хочешь печатать🖨\n\n*Список доступных общаг:*\n/knu16\n/kpi11", parse_mode="Markdown", reply_markup=markup)
		bot.register_next_step_handler(sent, set_user)
	else:
		bot.reply_to(message, 'Отлично!\nПросто отправь мне файл размером до 20 Мб и я отправлю его на печать☺️', reply_markup=markup)
		if(random.randint(1, 10) > 5):
			bot.send_message(message.chat.id, '⚠_️Но не забывай про одно строгое правило:_⚠️\n_курсачи и дипломы обязательно скидывать в защитных контейнерах - попадание воды в принтер может ему навредить!_😂', parse_mode="Markdown", reply_markup=markup)

# Handles button print photo
@bot.message_handler(func=lambda message: (str(message.text).upper() == 'НАПЕЧАТАТЬ ФОТОГРАФИЮ🖼') | (str(message.text).upper() == 'ФОТОГРАФИЮ') | (str(message.text).upper() == 'ФОТОГРАФИЯ') | (str(message.text).upper() == 'НАПЕЧАТАТЬ ФОТОГРАФИЮ') | (str(message.text) == '🖼') | (str(message.text).upper() == 'ФОТО'), content_types=['text'])
def handle_text_photo(message):
	if is_user_new(message):
		sent = bot.send_message(message.chat.id, "Для начала работы с ботом выбери в какой общаге ты хочешь печатать🖨\n\n*Список доступных общаг:*\n/knu16\n/kpi11", parse_mode="Markdown", reply_markup=markup)
		bot.register_next_step_handler(sent, set_user)
	else:
		bot.reply_to(message, 'Понял-принял!\nОтправь мне фотографию файлом или картинкой и я отправлю ее на печать☺️', reply_markup=markup)


# Handles button set dormitory
@bot.message_handler(func=lambda message: (str(message.text).upper() == 'ВЫБРАТЬ ОБЩАГУ🏣') | (str(message.text).upper() == 'ОБЩАГУ') | (str(message.text).upper() == 'ОБЩАГА') | (str(message.text).upper() == 'ВЫБРАТЬ ОБЩАГУ') | (str(message.text) == '🏣') | (str(message.text).upper() == 'DORM'), content_types=['text'])
def handle_text_dorm(message):
	sent = bot.reply_to(message, "Выбери в какой общаге ты хочешь печатать🖨\n\n*Список доступных общаг:*\n/knu16\n/kpi11", parse_mode="Markdown", reply_markup=markup)
	if is_user_new(message):
		bot.register_next_step_handler(sent, set_user)
	else:
		bot.register_next_step_handler(sent, set_dormitory)

# Sent file to print
@bot.message_handler(content_types=['document'])
def handle_doc(message: Message):
	if is_user_new(message):
		sent = bot.send_message(message.chat.id, "Для начала работы с ботом выбери в какой общаге ты хочешь печатать🖨\n\n*Список доступных общаг:*\n/knu16\n/kpi11", parse_mode="Markdown", reply_markup=markup)
		bot.register_next_step_handler(sent, set_user)
	else:
		if(message.document.file_size > 20971520):
			bot.reply_to(message, 'Не, брат, это слишком много. На вот, попробуй, авось поможет', reply_markup=markup)
			largeFilePhoto = open('large_file.jpg', 'rb')
			bot.send_photo(message.chat.id, largeFilePhoto, reply_markup=markup)
		else:
			path = '/PrintQueue/' + get_dormotory(message) + '/' + message.document.file_id + '___' + message.from_user.first_name + '___' + message.document.file_name 
			file_info = bot.get_file(message.document.file_id)
			downloaded_file = bot.download_file(file_info.file_path)
			dbx.files_upload(downloaded_file, path)
			bot.reply_to(message, "Файл успешно отправлен на печать👍\nID вашего заказа: " + "```" + str(message.document.file_id) + "```" + "\n\n_*ID можно легко скопировать_", parse_mode="Markdown", reply_markup=markup)

# Sent photo to print
@bot.message_handler(content_types=['photo'])
def handle_photo(message: Message):
	if is_user_new(message):
		sent = bot.send_message(message.chat.id, "Для начала работы с ботом выбери в какой общаге ты хочешь печатать🖨\n\n*Список доступных общаг:*\n/knu16\n/kpi11", parse_mode="Markdown", reply_markup=markup)
		bot.register_next_step_handler(sent, set_user)
	else:
		file_id = message.photo[-1].file_id
		file_info = bot.get_file(file_id)
		fileName = str(file_info.file_path).find('/')
		path = '/PrintQueue/' + get_dormotory(message) + '/' + file_id + '___' + message.from_user.first_name + '___' + file_info.file_path[fileName+1:]
		downloaded_file = bot.download_file(file_info.file_path)
		dbx.files_upload(downloaded_file, path)
		bot.reply_to(message, "Фото успешно отправлено на печать👍\nID вашего заказа: " + "```" + str(file_id) + "```" + "\n\n_*ID можно легко скопировать_", parse_mode="Markdown", reply_markup=markup)

# Handles all sent video files
@bot.message_handler(content_types=['video', 'video_note'])
def handle_video(message: Message):
	bot.reply_to(message, "Прости, дружище, занят - потом обязательно гляну.\nP.S. Если есть что распечатать - обращайся)", reply_markup=markup)
	bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

# Handles all sent audio files
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message: Message):
	bot.reply_to(message, "Прости, дружище, занят - потом обязательно послушаю.\nP.S. Если есть что распечатать - обращайся)", reply_markup=markup)
	bot.send_message(ADMIN_ID, 'От: ' + message.from_user.first_name)
	bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

# Handles all sent contacts
@bot.message_handler(content_types=['contact'])
def handle_contact(message: Message):
	bot.reply_to(message, "Это контактик какой-то красавицы?🤔\nЕсли да, то я обязательно передам его своему хозяину🙃\nP.S. Если есть что распечатать - обращайся)", reply_markup=markup)
	bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

# Handles all sent locations
@bot.message_handler(content_types=['location'])
def handle_location(message: Message):
	bot.reply_to(message, "Вау! Это что, локация где сегодня пройдет самая жаркая туса?🔥🔥🔥\nЯ передал хозяину) Он с Вами скоро свяжется😉\nP.S. Если есть что распечатать - обращайся)", reply_markup=markup)
	bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

# Handles all sent stickers
@bot.message_handler(content_types=['sticker'])
def handle_sticker(message: Message):
	bot.reply_to(message, "Аахахахах😂\nЧеткий стикер - будь я человеком, то слал бы его каждому)\nP.S. Если есть что распечатать - обращайся)", reply_markup=markup)
	bot.send_message(ADMIN_ID, 'От: ' + message.from_user.first_name)
	bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

# Handles text messages and everything other
@bot.message_handler(func=lambda message: True)
def send_default(message: Message):
	bot.reply_to(message, 'Не, дружище, ты не понял. У меня нет искуственного интелекта и поговорить со мной не получится😔\nНо распечатать твои файлы я могу😉\nДля начала работы введи /start', reply_markup=markup)

bot.polling()
