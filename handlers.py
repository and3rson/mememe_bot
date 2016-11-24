# -*- coding: utf-8 -*-
from telegram import ChatAction
from imgflip import IFApi
import settings
from redis import Redis


redis = Redis()
api = IFApi(settings.IMGFLIP_USERNAME, settings.IMGFLIP_PASSWORD)


class States:
    NEW = 'new'
    ENTER_TEXT1 = 'enter_text1'
    ENTER_TEXT2 = 'enter_text2'


def start(bot, update):
    if update.message.chat_id <= 0:
        # Don't do anything in group chats
        return

    update.message.reply_text(u'Введи новий запит пошуку картинки.')


def message(bot, update):
    if update.message.chat_id <= 0:
        # Don't do anything in group chats
        return

    uid = update.message.from_user.id
    q = update.message.text

    user_key = 'mememe:user:{}'.format(uid)

    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    if not redis.exists(user_key):
        redis.hmset(user_key, dict(
            state=States.NEW
        ))
        state = States.NEW
    else:
        state = redis.hget(user_key, 'state')

    if state == States.NEW:
        if q.strip() == '!':
            if not redis.hget(user_key, 'template_id'):
                update.message.reply_text('Введи новий запит пошуку картинки.')
            else:
                redis.hset(user_key, 'state', States.ENTER_TEXT1)
                update.message.reply_text('Введи верхній текст для картинки. Щоб пропустити його, надішли "-" (дефіс.)')
        else:
            result = api.search_templates(q)
            if not result:
                update.message.reply_text(u'Нічого не знайдено :v')
            else:
                title, href, template_id, image_url = result
                redis.hset(user_key, 'template_id', template_id)
                update.message.reply_photo(
                    photo=str(image_url),
                    caption=u'"{}"\nЦе та картинка, яку ти хочеш?\n\nНадішли "!" (знак оклику), щоб вибрати цю картинку.\nЯкщо не підходить - введи новий запит пошуку картинки.'.format(title)
                )
    elif state == States.ENTER_TEXT1:
        if q.strip() == '-':
            redis.hset(user_key, 'text1', '')
        else:
            redis.hset(user_key, 'text1', q.strip())
        redis.hset(user_key, 'state', States.ENTER_TEXT2)
        update.message.reply_text(u'Добре. Тепер введи нижній текст для картинки. Щоб пропустити його, надішли "-" (дефіс.)')
    elif state == States.ENTER_TEXT2:
        if q.strip() == '-':
            text2 = ''
        else:
            text2 = q.strip()
        redis.hset(user_key, 'state', States.NEW)
        template_id, text1, text2 = redis.hget(user_key, 'template_id'), redis.hget(user_key, 'text1'), text2
        # TODO: Caption image
        bot.sendChatAction(update.message.chat_id, ChatAction.UPLOAD_PHOTO)
        response = api.caption_image(int(template_id), text1, text2)
        if response['success']:
            update.message.reply_photo(photo=str(response['data']['url']))
        else:
            update.message.reply_text(u'Сталася помилка: {}'.format(response['error_message']))
        update.message.reply_text(u'Якщо хочеш згенерувати нову картинку, просто введи новий запит пошуку картинки.')
        redis.delete(user_key)


def reset(bot, update):
    if update.message.chat_id <= 0:
        # Don't do anything in group chats
        return

    uid = update.message.from_user.id

    user_key = 'mememe:user:{}'.format(uid)

    redis.delete(user_key)

    update.message.reply_text(u'О`кей, почнімо спочатку. Введи новий запит пошуку картинки.')
