#!/usr/bin/env python
# the region is dertermined by executing pyautogui.position() while the mouse
# being pointed to the target region

#get time
def get_time():
    pyscreeze.screenshot(region=(269, 294, 76, 17), imageFilename='time.png') #125%
    text = pytesseract.image_to_string(Image.open('time.png'), config='--psm 7')
    try:
        return [int(time) for time in text.split(':')]
    except:
        return [0, 0, 0]

def get_price():
    pyscreeze.screenshot(region=(302, 314, 50, 16), imageFilename='price.png') #125%
    text = pytesseract.image_to_string(Image.open('price.png'), config='--psm 7')
    try:
        price = int(text)
    except:
        price = 0
    return price

def get_second_price():
    while True:
        hour, minute, second = get_time()
        if not hour: continue
        print(str(hour)+":"+str(minute)+":"+str(second))
        price = get_price()
        if not price: continue
        print(str(price))
        return (second, price)

#input price
def input_price(price):
    pyautogui.click(clicks=2, x=914, y=332)#125%
    pyautogui.typewrite(str(price))
    pyautogui.click(x=1095, y=332)#125%

#withdraw
def withdraw():
    pyautogui.click(x=1038, y=433)#125%

#submit
def submit():
    pyautogui.click(x=793, y=434)#125%

def bid():
    submit_price = 0
    while True:
        second, price = get_second_price()
        if second >= 45 and second <= 48:
            submit_price = price + 1000
            input_price(submit_price)
            break
        time.sleep(0.1)

    while True:
        second, price = get_second_price()
        if second >= 50 and second <= 55:
            price += 800
            if abs(submit_price - price) >= 200:
                withdraw()
                submit_price = price
                input_price(submit_price)
            break
        time.sleep(0.1)

    while True:
        hour, minute, second = get_time()
        if second >= 55:
            submit()
            break
        time.sleep(0.1)


def usage():
    sys.stderr.write('automatic bid for shanghai license (for fun)\n')
    sys.exit(1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "-h": usage()
    import time
    import pyautogui
    from PIL import Image
    import pytesseract
    import pyscreeze

    bid()


