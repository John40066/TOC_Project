
from transitions.extensions import GraphMachine
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
machine = GraphMachine(
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
            "P1_play", "P2_play", "P1_play_C"], "dest": "menu", "conditions": "is_going_to_menu"},  # Go Back Menu
        {"trigger": "go_back", "source": [
            "P1_play", "P2_play", "P1_play_C", "Rule"], "dest": "menu"},  # Game End and Go Back Menu
    ],
    initial="menu",
    auto_transitions=False,
    show_conditions=True,
)

machine.get_graph().draw("./images/fsm.png", prog="dot", format="png")
