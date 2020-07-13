import re
import threading
import time
import requests
import telebot

from django.db import IntegrityError
from Bot.models import Client, Site

bot = telebot.TeleBot('1266535504:AAFrmvuiGMrIowTsCeswknLfASwpHHLnDL0')

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Try again', 'Cancel')


def url_check(url):
    try:
        site_ping = requests.head(url)
        if site_ping.status_code < 400:
            return True
        else:
            return False
    except Exception:
        return False


@bot.message_handler(content_types=['text'])
def start(message):
    x = threading.Thread(target=site_check)
    x.start()

    try:
        Client.objects.create(chat_id=message.from_user.id, chat_name=message.from_user.first_name,
                              username=message.from_user.username, lastname=message.from_user.last_name)
    except IntegrityError:
        pass

    if message.text == '/check':
        bot.send_message(message.from_user.id,
                         'What link do you want to check?\nFull link please (http:// or https://)')
        bot.register_next_step_handler(message, link_validation)

    elif message.text == '/add':
        bot.send_message(message.from_user.id,
                         'What link do you want to add to check list?\nFull link please (http:// or https://)')
        bot.register_next_step_handler(message, add_link)

    elif message.text == '/remove':
        bot.send_message(message.from_user.id,
                         'Write link to remove from check list?\nFull link please (http:// or https://)')
        bot.register_next_step_handler(message, remove)

    elif message.text == '/list':
        bot.send_message(message.from_user.id,
                         'Site`s your tracking:')
        user = Client.objects.get(chat_id=message.from_user.id)

        for e in user.url.all():
            bot.send_message(message.from_user.id, e.url)

    elif message.text == '/commands':
        bot.send_message(message.from_user.id,
                         'Available commands:'
                         '\n/commands - View all list of commands.'
                         '\n/check - Check a site now.'
                         '\n/add - Add a site to your check list.'
                         '\n/remove - Remove a site from your check list.'
                         '\n/list - Show check list.')

    else:
        bot.send_message(message.from_user.id, 'For list of commands type /commands')


def link_validation(message):
    link = message.text

    if re.match(regex, link):
        bot.send_message(message.from_user.id, 'Let`s take a look', reply_markup=keyboard1)

        if url_check(link):
            bot.send_message(message.from_user.id, 'Website working')
        else:
            bot.send_message(message.from_user.id, 'Website offline')

        bot.register_next_step_handler(message, retry)
    else:
        bot.send_message(message.from_user.id, 'Not a valid URL!', reply_markup=keyboard1)
        bot.register_next_step_handler(message, retry)


def retry(message):
    if message.text == 'Try again':
        bot.send_message(message.from_user.id, 'Ok let`s try again.')
        bot.register_next_step_handler(message, link_validation)
    else:
        bot.register_next_step_handler(message, start)


def add_link(message):
    if re.match(regex, message.text):

        try:
            user = Client.objects.get(chat_id=message.from_user.id)
            url = Site.objects.create(url=message.text, state=url_check(message.text))
            user.url.add(url)
            bot.send_message(message.from_user.id, 'Added to list!')
        except IntegrityError:
            bot.send_message(message.from_user.id, 'Already exists!')


def remove(message):
    if re.match(regex, message.text):

        try:
            user = Client.objects.get(chat_id=message.from_user.id)
            url = Site.objects.get(url=message.text)
            user.url.remove(url)
            bot.send_message(message.from_user.id, 'Deleted from list!')
        except IntegrityError:
            bot.send_message(message.from_user.id, 'Already deleted!')


def site_check():
    while True:

        for item in Site.objects.all():

            if url_check(item.url) != item.state:
                user_list = Client.objects.filter(url=item)
                item.state = url_check(item.url)
                item.save()

                if item.state:

                    for user in user_list:
                        bot.send_message(user.chat_id, '' + item.url + ' become available')
                else:

                    for user in user_list:
                        bot.send_message(user.chat_id, '' + item.url + ' unavailable')

        time.sleep(5)


bot.polling(none_stop=True, interval=2)
