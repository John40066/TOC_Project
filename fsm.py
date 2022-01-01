from transitions.extensions import GraphMachine
import os
import sys
import random
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
import cv2
import numpy as np

blank_grid = cv2.imread('./images/grid.png', cv2.IMREAD_GRAYSCALE)
white = cv2.imread('./images/white.png', cv2.IMREAD_GRAYSCALE)
black = cv2.imread('./images/black.png', cv2.IMREAD_GRAYSCALE)

# web_url = "https://toc-final.herokuapp.com"
web_url = "https://2710-218-164-32-143.ngrok.io"

load_dotenv()

channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable. in fsm")
    sys.exit(1)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable. in fsm")
    sys.exit(1)


line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

H_Prio = [(0, 0), (0, 5), (5, 0), (5, 5)]
M_Prio = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5),
          (3, 0), (3, 1), (3, 4), (3, 5), (4, 2), (4, 3), (5, 2), (5, 3)]
L_Prio = [(0, 1), (1, 0), (1, 1), (0, 4), (1, 4), (1, 5),
          (5, 4), (4, 5), (4, 4), (4, 1), (4, 0), (5, 1)]
grid = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 2, 0, 0],
    [0, 0, 2, 1, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0]]


def judge_endgame():
    Blank_count = 0
    P1_count = 0
    P2_count = 0
    for i in range(6):
        for j in range(6):
            if grid[i][j] == 0:
                Blank_count += 1
            elif grid[i][j] == 1:
                P1_count += 1
            elif grid[i][j] == 2:
                P2_count += 1
    if Blank_count == 0:
        return P1_count < P2_count
    elif P1_count == 0:
        return True
    elif P2_count == 0:
        return False
    return None


def clean_grid():
    for i in range(6):
        for j in range(6):
            grid[i][j] = 0
            if i == 2 and j == 2:
                grid[i][j] = 1
            elif i == 3 and j == 3:
                grid[i][j] = 1
            elif i == 2 and j == 3:
                grid[i][j] = 2
            elif i == 3 and j == 2:
                grid[i][j] = 2


def add_pic(result, chess_type, x, y):
    m, n = chess_type.shape
    for i in range(m):
        for j in range(n):
            result[x+i][y+j] = chess_type[i][j]
    return result


def Grid_Image(Result_count):
    Result_count += 1
    result = blank_grid.copy()
    for i in range(6):
        for j in range(6):
            x = 29*i + 26
            y = 29*j + 26
            if grid[i][j] == 1:
                result = add_pic(result, white, x, y)
            elif grid[i][j] == 2:
                result = add_pic(result, black, x, y)
    cv2.imwrite("./images/result" + str(Result_count) + ".png", result)
    return Result_count


def CPU_decision():
    for i in range(4):
        if(place(H_Prio[i][0], H_Prio[i][1], 2)):
            return H_Prio[i][0], H_Prio[i][1]
    random.shuffle(M_Prio)
    for i in range(16):
        if(place(M_Prio[i][0], M_Prio[i][1], 2)):
            return M_Prio[i][0], M_Prio[i][1]
    random.shuffle(L_Prio)
    for i in range(12):
        if(place(L_Prio[i][0], L_Prio[i][1], 2)):
            return L_Prio[i][0], L_Prio[i][1]
    return


def place(x, y, player):
    if(grid[x][y] == 0):
        grid[x][y] = player
        can = False
        p = x+1
        while p <= 5:
            if grid[p][y] == player and p != x+1:
                can = True
                p -= 1
                while grid[p][y] != player:
                    grid[p][y] = player
                    p -= 1
                break
            elif grid[p][y] == 0:
                break
            p += 1
        p = x-1
        while p >= 0:
            if grid[p][y] == player and p != x-1:
                can = True
                p += 1
                while grid[p][y] != player:
                    grid[p][y] = player
                    p += 1
                break
            elif grid[p][y] == 0:
                break
            p -= 1
        p = y+1
        while p <= 5:
            if grid[x][p] == player and p != y+1:
                can = True
                p -= 1
                while grid[x][p] != player:
                    grid[x][p] = player
                    p -= 1
                break
            elif grid[x][p] == 0:
                break
            p += 1
        p = y-1
        while p >= 0:
            if grid[x][p] == player and p != y-1:
                can = True
                p += 1
                while grid[x][p] != player:
                    grid[x][p] = player
                    p += 1
                break
            elif grid[x][p] == 0:
                break
            p -= 1
        p, q = x+1, y+1
        while p <= 5 and q <= 5:
            if grid[p][q] == player and p != x+1:
                can = True
                p, q = p-1, q-1
                while grid[p][q] != player:
                    grid[p][q] = player
                    p, q = p-1, q-1
                break
            elif grid[p][q] == 0:
                break
            p, q = p+1, q+1
        p, q = x+1, y-1
        while p <= 5 and q >= 0:
            if grid[p][q] == player and p != x+1:
                can = True
                p, q = p-1, q+1
                while grid[p][q] != player:
                    grid[p][q] = player
                    p, q = p-1, q+1
                break
            elif grid[p][q] == 0:
                break
            p, q = p+1, q-1
        p, q = x-1, y-1
        while p >= 0 and q >= 0:
            if grid[p][q] == player and p != x-1:
                can = True
                p, q = p+1, q+1
                while grid[p][q] != player:
                    grid[p][q] = player
                    p, q = p+1, q+1
                break
            elif grid[p][q] == 0:
                break
            p, q = p-1, q-1
        p, q = x-1, y+1
        while p >= 0 and q <= 5:
            if grid[p][q] == player and p != x-1:
                can = True
                p, q = p+1, q-1
                while grid[p][q] != player:
                    grid[p][q] = player
                    p, q = p+1, q-1
                break
            elif grid[p][q] == 0:
                break
            p, q = p-1, q+1
        if not can:
            grid[x][y] = 0
        return can
    return False


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.Result_count = 0
        self.precount = 0
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_Rule(self, event):
        text = event.message.text
        return text.lower() == "rule"

    def on_enter_menu(self, event):
        clean_grid()
        for i in range(self.precount, self.Result_count):
            os.remove("./images/result" + str(i+1) + ".png")
        self.precount = self.Result_count
        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='Menu',
                text="Welcome~ Let's Play Othello!",
                actions=[
                    MessageAction(
                        label='See Rule',
                        text='Rule'
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
        userID = event.source.user_id
        line_bot_api.push_message(userID, buttons_template_message)

    def on_enter_Rule(self, event):
        send_text_message(
            event.reply_token, "Rule : \n1. Enter 2 number and split by a space.\n2. You can exist game at any time by typing 'Menu'.")
        self.go_back(event)

    def is_going_to_2P(self, event):
        clean_grid()
        text = event.message.text
        condition = (text.lower() == "2 player")
        return condition

    def is_going_to_CPU(self, event):
        clean_grid()
        text = event.message.text
        condition = text.lower() == "1 player"
        return condition

    def is_going_to_menu(self, event):
        text = event.message.text
        return text.lower() == "menu"

    def is_going_to_P2turn(self, event):
        text = event.message.text
        slist = text.split(' ')
        userID = event.source.user_id
        try:
            x = int(slist[0])
            y = int(slist[1])
        except:
            return False
        if (0 <= x and x <= 5 and 0 <= y and y <= 5):
            if place(x, y, 1):
                send_text_message(
                    event.reply_token, "Player 1 place at : (" + str(x) + ", " + str(y) + ")")
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
        userID = event.source.user_id
        try:
            x = int(slist[0])
            y = int(slist[1])
        except:
            return False
        if (0 <= x and x <= 5 and 0 <= y and y <= 5):
            if place(x, y, 2):
                send_text_message(
                    event.reply_token, "Player 2 place at : (" + str(x) + ", " + str(y) + ")")
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
        userID = event.source.user_id
        try:
            x = int(slist[0])
            y = int(slist[1])
        except:
            return False
        if (0 <= x and x <= 5 and 0 <= y and y <= 5):
            if place(x, y, 1):
                send_text_message(
                    event.reply_token, "You place at : (" + str(x) + ", " + str(y) + ")")
                return True
            else:
                line_bot_api.push_message(
                    userID, TextSendMessage(text="Can not place here!"))
        else:
            line_bot_api.push_message(
                userID, TextSendMessage(text="Out of board range!"))
        return False

    def on_enter_P1_play_C(self, event):
        status = judge_endgame()
        userID = event.source.user_id
        if(status == None):
            self.Result_count = Grid_Image(self.Result_count)
            line_bot_api.push_message(
                userID, TextSendMessage(text="Your Turn."))
            img_url = web_url + "/images/result" + \
                str(self.Result_count) + ".png"
            image_message = ImageSendMessage(
                original_content_url=img_url, preview_image_url=img_url)
            line_bot_api.push_message(userID, image_message)
            print(grid_str())
        elif(status):
            line_bot_api.push_message(
                userID, TextSendMessage(text="CPU Win ! Game End"))
            self.go_back(event)
        else:
            line_bot_api.push_message(
                userID, TextSendMessage(text="You Win ! Game End"))
            self.go_back(event)

    def on_enter_P2_play(self, event):
        status = judge_endgame()
        userID = event.source.user_id
        if(status == None):
            self.Result_count = Grid_Image(self.Result_count)
            line_bot_api.push_message(userID, TextSendMessage(text="P2 Turn."))
            img_url = web_url + "/images/result" + \
                str(self.Result_count) + ".png"
            image_message = ImageSendMessage(
                original_content_url=img_url, preview_image_url=img_url)
            line_bot_api.push_message(userID, image_message)
            print(grid_str())
        elif(status):
            line_bot_api.push_message(
                userID, TextSendMessage(text="Player 2 Win ! Game End"))
            self.go_back(event)
        else:
            line_bot_api.push_message(
                userID, TextSendMessage(text="Player 1 Win ! Game End"))
            self.go_back(event)

    def on_enter_P1_play(self, event):
        userID = event.source.user_id
        status = judge_endgame()
        if(status == None):
            self.Result_count = Grid_Image(self.Result_count)
            line_bot_api.push_message(
                userID, TextSendMessage(text="P1 Turn."))
            img_url = web_url + "/images/result" + \
                str(self.Result_count) + ".png"
            image_message = ImageSendMessage(
                original_content_url=img_url, preview_image_url=img_url)
            line_bot_api.push_message(userID, image_message)
            print(grid_str())
        elif(status):
            line_bot_api.push_message(
                userID, TextSendMessage(text="Player 2 Win ! Game End"))
            self.go_back(event)
        else:
            line_bot_api.push_message(
                userID, TextSendMessage(text="Player 1 Win ! Game End"))
            self.go_back(event)

    def on_enter_CPU_play(self, event):
        status = judge_endgame()
        userID = event.source.user_id
        if(status == None):
            x, y = CPU_decision()
            line_bot_api.push_message(userID, TextSendMessage(
                text="CPU Turn. CPU place at : (" + str(x) + ", " + str(y) + ")"))
        self.go_back(event)
