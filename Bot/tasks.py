import time

import requests
import telebot
from django.utils.timezone import now

from Bot.models import Site, Client
from TheWatcher.celery import app


@app.task
def pool(i):
    item = Site.objects.get(pk=i)
    try:
        connect_timeout, read_timeout = 5.0, 30.0
        s = requests.session()
        s.verify = False
        site_ping = s.head(item.url, timeout=(connect_timeout, read_timeout))
        if site_ping.status_code < 400:
            state = True
        else:
            state = False
    except Exception:
        state = False

    time.sleep(1)
    if state != item.state:
        item.checking = True
        item.last_check = now()
        item.save(force_update=True)
        check_stage_1.delay(item)


def url_check(url):
    try:
        connect_timeout, read_timeout = 5.0, 30.0
        site_ping = requests.head(url, timeout=(connect_timeout, read_timeout))
        if site_ping.status_code < 400:
            return True
        else:
            return False
    except Exception:
        return False


@app.task
def check_stage_1(item):
    if url_check(item.url) != item.state:
        print('Checking', item.url)
        check_stage_2.delay(item)


@app.task
def check_stage_2(item):
    user_list = Client.objects.filter(url=item).only('chat_id', 'counter')
    bot = telebot.TeleBot('1266535504:AAFrmvuiGMrIowTsCeswknLfASwpHHLnDL0')
    while user_list.count() != 0:
        check = url_check(item.url)

        if check != item.state:
            for user in user_list:

                if (now() - item.last_check).total_seconds() > user.counter or check:
                    bot.send_message(user.chat_id,
                                     '' + str(item.url) + ' available ' + str(check))
                    user_list = user_list.exclude(chat_id=user.chat_id)

    item.state = url_check(item.url)
    item.checking = False
    item.save()
