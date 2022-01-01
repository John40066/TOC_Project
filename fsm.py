from transitions.extensions import GraphMachine
import os
import sys
from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    TextMessage,
    MessageEvent,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageTemplateAction,
    MessageAction,
    ImageSendMessage
)
from utils import send_text_message

load_dotenv()

channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
userID = 'Ue2b28014d0bc94ec2c97d37e1534e468'

buttons_back_message = TemplateSendMessage(
    alt_text='Buttons template',
    template=ButtonsTemplate(
        title='[INFO]',
        text='Click me to return to menu',
        actions=[
            MessageAction(
                label='Go Back to Menu',
                text='Back'
            )
        ]
    )
)

gird = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 2, 0, 0, 0],
    [0, 0, 0, 2, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]]


def clean_grid():
    gird = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 2, 0, 0, 0],
        [0, 0, 0, 2, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]]


def grid_str():
    s = "+ 0 1 2 3 4 5 6 7\n"
    for i in range(8):
        s += (str(i))
        for j in range(8):
            if gird[i][j] == 0:
                s += "  "
            elif gird[i][j] == 1:
                s += " O"
            elif gird[i][j] == 2:
                s += " X"
        s += "\n"
    return s


def place(x, y, player):
    if(gird[x][y] == 0):
        gird[x][y] = player
        can = False
        p = x+1
        while p < 7:
            if gird[p][y] == player and p != x+1:
                can = True
                p -= 1
                while gird[p][y] != player:
                    gird[p][y] = player
                    p -= 1
                break
            elif gird[p][y] == 0:
                break
            p += 1
        p = x-1
        while p >= 0:
            if gird[p][y] == player and p != x-1:
                can = True
                p += 1
                while gird[p][y] != player:
                    gird[p][y] = player
                    p += 1
                break
            elif gird[p][y] == 0:
                break
            p -= 1
        p = y+1
        while p < 7:
            if gird[x][p] == player and p != y+1:
                can = True
                p -= 1
                while gird[x][p] != player:
                    gird[x][p] = player
                    p -= 1
                break
            elif gird[x][p] == 0:
                break
            p += 1
        p = y-1
        while p >= 0:
            if gird[x][p] == player and p != y-1:
                can = True
                p += 1
                while gird[x][p] != player:
                    gird[x][p] = player
                    p += 1
                break
            elif gird[x][p] == 0:
                break
            p -= 1
        p, q = x+1, y+1
        while p < 7 and q < 7:
            if gird[p][q] == player and p != x+1:
                can = True
                p, q = p-1, q-1
                while gird[p][q] != player:
                    gird[p][q] = player
                    p, q = p-1, q-1
                break
            elif gird[p][q] == 0:
                break
            p, q = p+1, q+1
        p, q = x+1, y-1
        while p < 7 and q >= 0:
            if gird[p][q] == player and p != x+1:
                can = True
                p, q = p-1, q+1
                while gird[p][q] != player:
                    gird[p][q] = player
                    p, q = p-1, q+1
                break
            elif gird[p][q] == 0:
                break
            p, q = p+1, q-1
        p, q = x-1, y-1
        while p >= 0 and q >= 0:
            if gird[p][q] == player and p != x-1:
                can = True
                p, q = p+1, q+1
                while gird[p][q] != player:
                    gird[p][q] = player
                    p, q = p+1, q+1
                break
            elif gird[p][q] == 0:
                break
            p, q = p-1, q-1
        p, q = x-1, y+1
        while p >= 0 and q < 7:
            if gird[p][q] == player and p != x-1:
                can = True
                p, q = p+1, q-1
                while gird[p][q] != player:
                    gird[p][q] = player
                    p, q = p+1, q-1
                break
            elif gird[p][q] == 0:
                break
            p, q = p-1, q+1
        if not can:
            gird[x][y] = 0
        return can
    return False


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_Rank(self, event):
        text = event.message.text
        return text.lower() == "rank"

    def on_enter_menu(self, event):
        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='Menu',
                text="Welcome~ Let's Play Othello!",
                actions=[
                    MessageAction(
                        label='See Rank',
                        text='Rank'
                    ),
                    MessageAction(
                        label='1 Player',
                        text='1 Player'
                    ),
                    MessageAction(
                        label='2 Player',
                        text='2 Player'
                    )
                ]
            )
        )
        line_bot_api.push_message(userID, buttons_template_message)

    def on_enter_Rank(self, event):
        print("In Rank List")
        line_bot_api.push_message(userID, TextSendMessage(text="====RANK===="))
        self.go_back(event)

    def is_going_to_2P(self, event):
        clean_grid()
        text = event.message.text
        condition = text.lower() == "2 player"
        if condition:
            line_bot_api.push_message(userID, TextSendMessage(
                text="You Choose 2 Player Mode"))
        return condition

    def is_going_to_CPU(self, event):
        clean_grid()
        text = event.message.text
        condition = text.lower() == "1 player"
        if condition:
            line_bot_api.push_message(userID, TextSendMessage(
                text="You Choose 1 Player Mode"))
        return condition

    def is_going_to_menu(self, event):
        text = event.message.text
        return text.lower() == "back"

    def is_going_to_P2turn(self, event):
        text = event.message.text
        slist = text.split(' ')
        try:
            x = int(slist[0])
            y = int(slist[1])
        except:
            return False
        if (0 <= x and x <= 7 and 0 <= y and y <= 7):
            if place(x, y, 1):
                line_bot_api.push_message(userID, TextSendMessage(
                    text="Player 1 place at : (" + str(x) + ", " + str(y) + ")"))
                return True
            else:
                line_bot_api.push_message(
                    userID, TextSendMessage(text="Can not place here!"))
        else:
            line_bot_api.push_message(
                userID, TextSendMessage(text="Out of board range!"))
        return False

    def is_going_to_P1turn(self, event):
        text = event.message.text
        slist = text.split(' ')
        try:
            x = int(slist[0])
            y = int(slist[1])
        except:
            return False
        if (0 <= x and x <= 7 and 0 <= y and y <= 7):
            if place(x, y, 2):
                line_bot_api.push_message(userID, TextSendMessage(
                    text="Player 2 place at : (" + str(x) + ", " + str(y) + ")"))
                return True
            else:
                line_bot_api.push_message(
                    userID, TextSendMessage(text="Can not place here!"))
        else:
            line_bot_api.push_message(
                userID, TextSendMessage(text="Out of board range!"))
        return False

    def is_going_to_CPUturn(self, event):
        text = event.message.text
        slist = text.split(' ')
        try:
            x = int(slist[0])
            y = int(slist[1])
        except:
            return False
        return 0 <= x and x <= 7 and 0 <= y and y <= 7

    def on_enter_P1_play_C(self, event):
        line_bot_api.push_message(
            userID, TextSendMessage(text="Your Turn. Type a coordinate."))
        line_bot_api.push_message(userID, buttons_back_message)

    def on_enter_P2_play(self, event):
        line_bot_api.push_message(userID, TextSendMessage(
            text="P2 Turn. Type a coordinate."))
        line_bot_api.push_message(userID, buttons_back_message)
        line_bot_api.push_message(userID, TextSendMessage(text=grid_str()))
        img_url = 'https://c356-223-139-137-56.ngrok.io/images/grid.png'
        image_message = ImageSendMessage(
            original_content_url=img_url, preview_image_url=img_url)
        line_bot_api.push_message(userID, image_message)

    def on_enter_P1_play(self, event):
        line_bot_api.push_message(userID, TextSendMessage(
            text="P1 Turn. Type a coordinate."))
        line_bot_api.push_message(userID, buttons_back_message)
        print(grid_str())
        line_bot_api.push_message(userID, TextSendMessage(text=grid_str()))

    def on_enter_CPU_play(self, event):
        print("CPU play")
        reply_token = event.reply_token
        send_text_message(reply_token, "==CPU Turn==")
        self.go_back()

    # def on_exit_state1(self):
    #     print("Leaving state1")

    # def on_exit_state2(self):
    #     print("Leaving state2")
