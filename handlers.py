# -*- coding: utf-8 -*-
from telegram import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent, ChatAction
import uuid
import hashlib
import tempfile
from imgflip import IFApi
from PIL import Image, ImageDraw, ImageFont
import settings
from redis import Redis


redis = Redis()


api = IFApi(settings.IMGFLIP_USERNAME, settings.IMGFLIP_PASSWORD)


class States:
    NEW = 'new'
    ENTER_TEXT1 = 'enter_text1'
    ENTER_TEXT2 = 'enter_text2'


def help(bot, update):
    update.message.reply_text(u'''
Інструкція:
1. Пишеш в чаті: "@mememe_bot "
2. В списку знаходиш ID картинки, АЛЕ НЕ НАТИСКАЄШ НА НЕЇ
3. Дописуєш ID в повідомлення
4. Через крапку з комою дописуєш верхній і нижній текст, наприклад, "@mememe_bot 100947;що, як я скажу тобі;що ти - шоха"
5. Вибираємо фінальну картинку
6. ???
7. PROFIT!
'''.strip())


def inline(bot, update):
    q = update.inline_query.query
    try:
        offset = int(update.inline_query.offset)
    except:
        offset = 0

    q = q.split(';')

    start = offset
    end = start + 50
    next_offset = (start + 50) if offset < 200 else ''

    # if len(q) <= 1:
    #     update.inline_query.answer([
    #         InlineQueryResultArticle(
    #             id=uuid.uuid4(),
    #             title='Manual',
    #             input_message_content=InputTextMessageContent('1. Find ID of image in this list.\n2. Type query: ID;top text line;bottom text liine')
    #         )
    #     ])
    # el
    if len(q) != 3:
        response = api.get_memes()
        print response['data']['memes'][0]['url']
        results = []
        for meme in response['data']['memes']:
            results.append(
                InlineQueryResultPhoto(
                    id=uuid.uuid4(),
                    photo_url='https://dummyimage.com/600x400/000000/ffffff&text=+++{}+++:'.format(meme['id']),
                    thumb_url='https://dummyimage.com/600x400/000000/ffffff&text=+++{}+++:'.format(meme['id'])
                )
            )
            results.append(
                InlineQueryResultPhoto(
                    # id=hashlib.md5(meme['id']).hexdigest(),
                    id=uuid.uuid4(),
                    photo_url=meme['url'],
                    thumb_url=meme['url'],
                    title=u'{id}: {name}'.format(
                        id=meme['id'],
                        name=meme['name']
                    ),
                    caption=u'{id}: {name}'.format(
                        id=meme['id'],
                        name=meme['name']
                    )
                )
            )
        update.inline_query.answer(results[start:end], next_offset=next_offset)
        # update.inline_query.answer([
        #     InlineQueryResultArticle(
        #         id=uuid.uuid4(),
        #         title='Need 3 arguments.',
        #         input_message_content=InputTextMessageContent('E.g.: 100952;foo;bar')
        #     )
        # ])
    else:
        template_id, text0, text1 = q
        response = api.caption_image(int(template_id), text0, text1)
        update.inline_query.answer([
            InlineQueryResultPhoto(
                id=uuid.uuid4(),
                photo_url=response['data']['url'],
                thumb_url=response['data']['url']
            )
        ])


def start(bot, update):
    uid = update.message.from_user.id
    if uid <= 0:
        # Don't do anything in group chats
        return

    update.message.reply_text(u'Введи новий запит пошуку картинки.')


def message(bot, update):
    uid = update.message.from_user.id
    if uid <= 0:
        # Don't do anything in group chats
        return
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
        update.message.reply_photo(photo=str(response['data']['url']))
        update.message.reply_text(u'Готово! Якщо хочеш згенерувати ще, просто введи новий запит пошуку картинки.')
        redis.delete(user_key)


def reset(bot, update):
    uid = update.message.from_user.id
    if uid <= 0:
        # Don't do anything in group chats
        return

    user_key = 'mememe:user:{}'.format(uid)

    redis.delete(user_key)

    update.message.reply_text(u'О`кей, почнімо спочатку. Введи новий запит пошуку картинки.')
