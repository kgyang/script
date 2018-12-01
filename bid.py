#!/usr/bin/python
# used to paibai, just for fun 

import time
import pyautogui
from PIL import Image
import pytesseract
import pyscreeze

#get time
def get_time():
    #pyscreeze.screenshot(region=(477, 436, 58, 14), imageFilename='time.png')
    #text = pytesseract.image_to_string(Image.open('time.png'), config='--psm 7')
    im = pyscreeze.screenshot(region=(477, 436, 58, 14))
    text = pytesseract.image_to_string(im, config='--psm 7')
    try:
        return [int(time) for time in text.split(':')]
    except:
        return [0, 0, 0]

def get_price():
    im = pyscreeze.screenshot(region=(504, 453, 45, 14))
    text = pytesseract.image_to_string(im, config='--psm 7')
    try:
        price = int(text)
    except:
        price = 0
    return price

#input price
def input_price(price):
    pyautogui.click(x=986, y=463)
    pyautogui.typewrite(str(price))
    pyautogui.click(x=1143, y=460)
    time.sleep(0.2)
    pyautogui.click(x=1085, y=464)

#submit
def submit():
    pyautogui.click(x=901, y=542)

if __name__ == "__main__":
    while True:
        hour, minute, second = get_time()
        if not hour: continue
        print(str(hour)+":"+str(minute)+":"+str(second))
        price = get_price()
        if not price: continue
        print(str(price))
        if second >= 45:
            input_price(price+300)
            break
        time.sleep(0.1)
    while True:
        hour, minute, second = get_time()
        if not hour: continue
        print(str(hour)+":"+str(minute)+":"+str(second))
        if second >= 55:
            submit()
            break
        time.sleep(0.1)
