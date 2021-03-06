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
    MessageTemplateAction
)
from fsm import TocMachine
from utils import send_text_message

load_dotenv()

user_list = []

# machine = TocMachine(
#     states=["menu", "Rule", "P1_play", "P2_play",
#             "P1_play_C", "CPU_play"],
#     transitions=[
#         {"trigger": "advance", "source": "menu",
#             "dest": "Rule", "conditions": "is_going_to_Rule"},  # Rule
#         {"trigger": "advance", "source": "menu",
#             "dest": "P1_play", "conditions": "is_going_to_2P"},  # 2 Player
#         {"trigger": "advance", "source": "menu",
#             "dest": "P1_play_C", "conditions": "is_going_to_CPU"},  # 1 Player
#         {"trigger": "advance", "source": "P1_play",
#             "dest": "P2_play", "conditions": "is_going_to_P2turn"},  # 1P to 2P
#         {"trigger": "advance", "source": "P2_play",
#             "dest": "P1_play", "conditions": "is_going_to_P1turn"},  # 2P to 1P
#         {"trigger": "advance", "source": "P1_play_C",
#             "dest": "CPU_play", "conditions": "is_going_to_CPUturn"},  # 1P to CPU
#         {"trigger": "go_back", "source": "CPU_play",
#             "dest": "P1_play_C"},  # CPU to 1P
#         {"trigger": "advance", "source": [
#             "P1_play", "P2_play", "P1_play_C", "Rule"], "dest": "menu", "conditions": "is_going_to_menu"},  # Go Back Menu
#         {"trigger": "go_back", "source": [
#             "P1_play", "P2_play", "P1_play_C", "Rule"], "dest": "menu"},  # Game End and Go Back Menu
#         {"trigger": "go_back", "source": "Rule", "dest": "menu"},  # Go Back Menu
#     ],
#     initial="menu",
#     auto_transitions=False,
# )


def new_Machine(userid):
    return TocMachine(
        userid=userid,
        states=["menu", "Rule", "P1_play", "P2_play",
                "P1_play_C", "CPU_play"],
        transitions=[
            {"trigger": "advance", "source": "menu",
             "dest": "Rule", "conditions": "is_going_to_Rule"},  # Rule
            {"trigger": "advance", "source": "menu",
             "dest": "P1_play", "conditions": "is_going_to_2P"},  # 2 Player
            {"trigger": "advance", "source": "menu",
             "dest": "P1_play_C", "conditions": "is_going_to_CPU"},  # 1 Player
            {"trigger": "advance", "source": "P1_play",
             "dest": "P2_play", "conditions": "is_going_to_P2turn"},  # 1P to 2P
            {"trigger": "advance", "source": "P2_play",
             "dest": "P1_play", "conditions": "is_going_to_P1turn"},  # 2P to 1P
            {"trigger": "advance", "source": "P1_play_C",
             "dest": "CPU_play", "conditions": "is_going_to_CPUturn"},  # 1P to CPU
            {"trigger": "go_back", "source": "CPU_play",
             "dest": "P1_play_C"},  # CPU to 1P
            {"trigger": "advance", "source": [
                "P1_play", "P2_play", "P1_play_C", "Rule"], "dest": "menu", "conditions": "is_going_to_menu"},  # Go Back Menu
            {"trigger": "go_back", "source": [
                "P1_play", "P2_play", "P1_play_C", "Rule"], "dest": "menu"},  # Game End and Go Back Menu
            {"trigger": "go_back", "source": "Rule",
                "dest": "menu"},  # Go Back Menu
        ],
        initial="menu",
        auto_transitions=False,
        # show_conditions=True
    )


app = Flask(__name__, static_url_path="/images", static_folder="./images/")


# get channel_secret and channel_access_token from your environment variable
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


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    pos = -1
    for i in range(len(user_list)):
        if user_list[i]['userID'] == events[0].source.user_id:
            pos = i
            break
    if pos == -1:
        pos = len(user_list)
        user_list.append(
            {"userID": events[0].source.user_id, "machine": new_Machine(events[0].source.user_id)})
    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {user_list[pos]['machine'].state}")
        print(f"REQUEST BODY: \n{body}")
        response = user_list[pos]['machine'].advance(event)
        if response == False:
            send_text_message(event.reply_token, "Invalid Command.")

    return "OK"


# @app.route("/show-fsm", methods=["GET"])
# def show_fsm():
#     machine.get_graph().draw("fsm.png", prog="dot", format="png")
#     return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
