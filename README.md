# TOC Final Project

## Project Name : Othello Game (黑白棋)

## State Machine

### Graph
![](https://i.imgur.com/FQTOorl.png)

### Concept

- **`menu`**
start from menu(new user type 'menu' to open menu)
push botton "Rule" to see game rule
push botton "1 Player" to play with CPU
push botton "2 Player" to play with your friend

- **`Rule`**
send rule message and go back `menu` immediatly.

- **`P1_play`**
P1 type a coordinate to place white chess
If out of range or invalid input will keep the state
else go to `P2_play`
If type "menu" will back to `menu`, this round end.

- **`P2_play`**
P2 type a coordinate to place black chess
If out of range or invalid input will keep the state
else go to `P1_play`
If type "menu" will back to `menu`, this round end.

- **`P1_play_c`**
P1 type a coordinate to place white chess
If out of range or invalid input will keep the state
else go to `CPU_play`
If type "menu" will back to `menu`, this round end.

- **`CPU_play`**
CPU choose a coordinate to place black chess and go back `P1_play_c` immediatly.


:::info
In `P1_play`、`P1_play`、`P1_play_c`
If game end(any player win), go to menu.
In `CPU_play`, if game end(any player win), go to `P1_play`.
:::


## Specail Bonus
- Can Generate Image to show the chess.