# TOC Final Project

## Project Name : Othello Game (黑白棋)

## About my LineBot

### Menu
Type "Rule" to see Rule and open Menu in your first entering room.
- See Rule : literraly
- 1 Player : Play With CPU (you use white discs)
- 2 Player : Can play with your friend.

### Game Rule
If you don't know what is 黑白棋, [See Here](https://zh.wikipedia.org/wiki/%E9%BB%91%E7%99%BD%E6%A3%8B).

### How to Play
In your turn, type a coordinate `(row, column)` to place your discs. If out of range or not following game rule. You will receive "Invalid Input" and need to retype a new coordinate.

If game end, LineBot will show who win and return to menu.

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
P1 type a coordinate to place white discs
If out of range or invalid input will keep the state
else go to `P2_play`
If type "menu" will back to `menu`, this round end.

- **`P2_play`**
P2 type a coordinate to place black discs
If out of range or invalid input will keep the state
else go to `P1_play`
If type "menu" will back to `menu`, this round end.

- **`P1_play_c`**
P1 type a coordinate to place white discs
If out of range or invalid input will keep the state
else go to `CPU_play`
If type "menu" will back to `menu`, this round end.

- **`CPU_play`**
CPU choose a coordinate to place black discs and go back `P1_play_c` immediatly.


:::info
In `P1_play`、`P1_play`、`P1_play_c`
If game end(any player win), go to menu.
In `CPU_play`, if game end(any player win), go to `P1_play`.
:::

## Specail Bonus
- Single user single state machine.
- Can Generate **Image** to show the board.
- Run on Heroku.

## FeedBack
1. Bonus 分數占好少(感覺Bonus應該在100分之外的加分才對)
2. 評分標準沒有很清楚(但如果給很鬆就沒差了ㄌ<3)
3. 基本上是查資料大賽...(且都是在 LineBot、Heroku 上)
4. Heroku 問題很難處裡(尤其是 pygraphviz 的問題)
5. 感覺可以早點Annouse早點
