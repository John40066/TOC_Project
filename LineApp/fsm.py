from transitions.extensions import GraphMachine
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

# class MyMachine(object):
#     def __init__(self, **machine_configs):
#         self.machine = GraphMachine(model=self, **machine_configs)

#     def is_going_to_state1(self, event):
#         text = event.message.text
#         return text.lower() == "go to state1"

#     def is_going_to_state2(self, event):
#         text = event.message.text
#         return text.lower() == "go to state2"

#     def on_enter_state1(self, event):
#         print("I'm entering state1")

#         reply_token = event.reply_token
#         send_text_message(reply_token, "Trigger state1")
#         self.go_back()

#     def on_exit_state1(self):
#         print("Leaving state1")

#     def on_enter_state2(self, event):
#         print("I'm entering state2")

#         reply_token = event.reply_token
#         send_text_message(reply_token, "Trigger state2")
#         self.go_back()

#     def on_exit_state2(self):
#         print("Leaving state2")


# machine = TocMachine(
#     states=["user", "state1", "state2"],
#     transitions=[
#         {
#             "trigger": "advance",
#             "source": "user",
#             "dest": "state1",
#             "conditions": "is_going_to_state1",
#         },
#         {
#             "trigger": "advance",
#             "source": "user",
#             "dest": "state2",
#             "conditions": "is_going_to_state2",
#         },
#         {"trigger": "go_back", "source": ["state1", "state2"], "dest": "user"},
#     ],
#     initial="user",
#     auto_transitions=False,
#     show_conditions=True,
# )


class MyMachine(object):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_state1(self, event):
        text = event.message.text
        return text.lower() == "go to state1"

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == "go to state2"

    def on_enter_state1(self, event):
        print("I'm entering state1")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state1")
        self.go_back()

    def on_exit_state1(self):
        print("Leaving state1")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state2")
        self.go_back()

    def on_exit_state2(self):
        print("Leaving state2")


machine = MyMachine(
    states=["user", "state1", "state2"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state1",
            "conditions": "is_going_to_state1",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state2",
            "conditions": "is_going_to_state2",
        },
        {"trigger": "go_back", "source": ["state1", "state2"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

machine.get_graph().draw("fsm.png", prog="dot", format="png")
