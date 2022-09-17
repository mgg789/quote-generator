from bs4 import BeautifulSoup as bs
from PIL import Image, ImageFont, ImageDraw
import requests
import urllib
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.upload import VkUpload
import json
from io import BytesIO


def add_text(text, name):
    font = ImageFont.truetype("NotoSerif-Bold.ttf", 60)
    title_font = ImageFont.truetype("NotoSerif-Bold.ttf", 110)
    name_font = ImageFont.truetype("NotoSerif-Regular.ttf", 45)
    array_text = text.split()
    re = ""
    cur = 0
    for i in array_text:
        # print(cur, i)
        cur += len(i) + 1
        re += i + " "
        if cur >= 30:
            re += "\n"
            cur = 0
    # print(re)
    text = re
    # for i in text:
    #
    editable.text((230, 130), "Великие цитаты пумовцев", fill=(255, 255, 255), font=title_font) #title = const
    editable.text((650, 400), text, fill=(255, 255, 255), font=font) # quote
    editable.text((145, 905), name, fill=(255, 255, 255), font=name_font)


def add_image(ph):
    global new_quote

    if "sun" in ph:
        response = requests.get(ph)
        im = Image.open(BytesIO(response.content))
    else:
        # print("here")
        im = Image.open("noava.jpg")
    im = im.convert("RGB")
    im = im.resize((520, 520))
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    # print(im.mode)
    im.save("new_ava.png")

    img = Image.open("new_ava.png")
    new_quote = new_quote.convert("RGBA")
    img = img.convert("RGBA")
    new_quote.paste(img, (75, 375), img)


def upload_photo(upload, photo):
    response = upload.photo_messages(photo)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


def send_photo(vk, peer_id, owner_id, photo_id, access_key):
    # print(peer_id)
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    # print(attachment)
    session.get_api().messages.send(
        random_id=0,
        peer_id=peer_id,
        message="Вот твоя цитата! Кидай в предложку, если хотел бы выложить её в группе!",
        attachment=attachment)


app = "vk1.a.gskMOJQIPmk3hm2Koe8cChpQl-_r51n_8CYK5VxMb5ogmjZFVCyR4MztvYAsWsWSMppuxBEzADyQKnheROpqQwuVwStAsOAUj1mmUeRZ_q0M0oEuZ6woBUcSq9swiu-vnhgJpPEOsMjUfjOuPnV_E73GJPvJHB7UyHdxuLz_akwJ8jxAkuJt--sBalW96FIP" # через токен приложения upload
token = "vk1.a.yrLesQ_QLTPvKtytKkM45j2rouJvOZT7zCJBHttBKUNCW2eo-Lv_8TJU-O-CPgREQFbITMMSaI1E2Chcdb8a8WnQLaN-SFK1W0NYqYxP1GV2MSODkBdWMWKZ1BjI-jjZ4wsZwCsSx0jqTeu1mIU0Gwd9bEZV_b7y_rplgB17t1a6rsJsrY1IUSeWCgoBO9Sp"
session = vk_api.VkApi(token=token)
lp = VkLongPoll(session)
for event in lp.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            try:
                # print(event.user_id)
                final = event.message.split("\n")
                # print(final)
                # print(event.message)
                if len(final) < 2 or "@" not in event.message:
                    session.get_api().messages.send(
                        random_id=0,
                        peer_id=event.peer_id,
                        message="Кажется вами не был соблюдён формат цитаты. Следите за оформлением, пригодится при сдаче ЕГЭ)")
                    raise OverflowError
                quote = final[0]
                user_id = final[1][3:final[1].find("|")]
                re = requests.get("https://api.vk.com/method/users.get", params={
                    "access_token": token,
                    "user_ids": user_id,
                    "fields": "photo_max_orig",
                    "v": 5.131
                })
                data = json.loads(re.text)
                # print(f"Creating quote sent by {event.user_id}", end = " ")
                # print(data)
                if not len(data["response"]):
                    continue
                container = data["response"][0]
                name = f"{container['first_name']} {container['last_name']}"
                photo = container["photo_max_orig"]
                # print(photo)
                new_quote = Image.open("back.png")
                new_quote = new_quote.resize((2048, 1152))
                new_quote = new_quote.convert("RGB")
                editable = ImageDraw.Draw(new_quote)

                add_text(quote, name)
                add_image(photo)
                new_quote.save("quote.png")

                session_app = vk_api.VkApi(token=app)
                upload = VkUpload(session_app.get_api())
                send_photo(session_app.get_api(), event.user_id, *upload_photo(upload, 'quote.png'))
                # print("d", end=" ")
            except OverflowError:
                pass
            except:
                print(f"\nError with a quote from {event.user_id}. Fix ASAP.")
                session.get_api().messages.send(
                        random_id=0,
                        peer_id=event.peer_id,
                        message="При генерации цитаты возникла непредвиденная ошибка или вами не был соблюдён формат цитаты. В скором времени мы решим проблему. Спасибо, что помогаете нам улучшать генератор, пока он находится в режиме тестирования!")
