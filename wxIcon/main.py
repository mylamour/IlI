import os
import math
import glob
import itchat
import urllib
import requests
import PIL.Image as Image

x = 0
y = 0
num = 0

itchat.auto_login(enableCmdQR=-1, hotReload=True)

friends = itchat.get_friends(update=True)[0:]
user = friends[0]["UserName"]

if not os.path.isdir(user):
    os.mkdir(user)

for friend in friends:
    img = itchat.get_head_img(userName=friend["UserName"])
    with open("{}/{}.jpg".format(user,friend["UserName"]), 'wb') as icon:
        icon.write(img)

pics = os.listdir(user)

eachsize = int(math.sqrt(float(640 * 640) / len(pics)))
numline = int(640 / eachsize)

toImage = Image.new('RGBA', (640, 640))

for i in pics:
    try:
        img = Image.open(user + "/" + i)
    except Exception as e:
        continue

    img = img.resize((eachsize, eachsize), Image.ANTIALIAS)
    toImage.paste(img, (x * eachsize, y * eachsize))

    x += 1
    if x == numline:
        x = 0
        y += 1

fimage = "{}.jpg".format(user)
toImage = toImage.convert("RGB")
toImage.save(fimage)

itchat.send_image(fimage, 'filehelper')
