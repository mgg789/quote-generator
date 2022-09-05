from bs4 import BeautifulSoup as bs
from PIL import Image, ImageFont, ImageDraw
import requests
import urllib
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.upload import VkUpload
import json
from io import BytesIO
from tokens import token, app


def add_text(text, name):
    font = ImageFont.truetype("NotoSerif-Bold.ttf", 50)
    title_font = ImageFont.truetype("NotoSerif-Bold.ttf", 110)
    name_font = ImageFont.truetype("NotoSerif-Regular.ttf", 45)
    array_text = text.split()
    re = ""
    cur = 0
    for i in array_text:
        # print(cur, i)
        cur += len(i) + 1
        re += i + " "
        if cur >= 35:
            re += "\n"
            cur = 0
    print(re)
    text = re
    # for i in text:
    #
    editable.text((230, 130), "Великие цитаты пумовцев", (255, 255, 255), font=title_font) #title = const
    editable.text((650, 400), text, (255, 255, 255), font=font) # quote
    editable.text((145, 905), name, (255, 255, 255), font=name_font)


def add_image(ph):
    global new_quote

    response = requests.get(ph)
    im = Image.open(BytesIO(response.content))
    im = im.resize((520, 520))
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
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
    print(peer_id)
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    session.get_api().messages.send(
        random_id=0,
        peer_id=peer_id,
        message="Вот твоя цитата! Кидай в предложку, если хотел бы выложить её в группе!",
        attachment=attachment)


session = vk_api.VkApi(token=token)
lp = VkLongPoll(session)
for event in lp.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            print(event.user_id)
            final = event.message.split("\n")
            quote = final[0]
            user_id = final[1][3:final[1].find("|")]
            re = requests.get("https://api.vk.com/method/users.get", params={
                "access_token": token,
                "user_ids": user_id,
                "fields": "photo_max_orig",
                "v": 5.131
            })
            data = json.loads(re.text)
            print(quote, user_id)
            container = data["response"][0]
            name = f"{container['first_name']} {container['last_name']}"
            photo = container["photo_max_orig"]

            new_quote = Image.open("back.png")
            new_quote = new_quote.resize((2048, 1152))
            editable = ImageDraw.Draw(new_quote)

            add_text(quote, name)
            add_image(photo)
            new_quote.save("quote.png")

            session_app = vk_api.VkApi(token=app)
            upload = VkUpload(session_app.get_api())
            send_photo(session_app.get_api(), event.user_id, *upload_photo(upload, 'quote.png'))

