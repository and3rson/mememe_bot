# -*- coding: utf-8 -*-
from telegram import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
import uuid
import hashlib
import tempfile
from imgflip import IFApi
from PIL import Image, ImageDraw, ImageFont
import settings


api = IFApi(settings.IMGFLIP_USERNAME, settings.IMGFLIP_PASSWORD)


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
