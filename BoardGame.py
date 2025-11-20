# BoardGame.py
# Wizard Duel
#Pierce Limbo

#Instructions
# Player1 starts at tile 1 and moves right.
# Player2 starts at tile 10 and moves left.
# Some tiles are worth 1 point.
# First player to reach tile 5 wins.
# If both reach tile 5, higher score wins.

import os
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
GAME_FILE = "events.txt"
BOARD_SIZE = 10
CENTER_TILE = 5

def default_state():
    return {
        "turn": "Player1",
        "positions": {"Player1": 1, "Player2": BOARD_SIZE},
        "scores": {"Player1": 0, "Player2": 0},
        "runes": {
            3: "Fire",
            7: "Ice"
        },
        "last_message": ""
    }
state = default_state()

def load_game():
    global state
    if not os.path.exists(GAME_FILE):
        return
    new_state = default_state()
    runes = {}
    with open(GAME_FILE) as f:
        for raw in f:
            line = raw.strip()
            if ":" not in line:
                continue
            key, val = [x.strip() for x in line.split(":", 1)]

            if key == "Turn":
                new_state["turn"] = val
            elif key == "P1":
                new_state["positions"]["Player1"] = int(val)
            elif key == "P2":
                new_state["positions"]["Player2"] = int(val)
            elif key == "Score1":
                new_state["scores"]["Player1"] = int(val)
            elif key == "Score2":
                new_state["scores"]["Player2"] = int(val)
            elif key.isdigit():
                runes[int(key)] = val
    if runes:
        new_state["runes"] = runes
    state = new_state

def save_game():
    with open(GAME_FILE, "w") as f:
        f.write(f"Turn: {state['turn']}\n")
        f.write(f"P1: {state['positions']['Player1']}\n")
        f.write(f"P2: {state['positions']['Player2']}\n")
        f.write(f"Score1: {state['scores']['Player1']}\n")
        f.write(f"Score2: {state['scores']['Player2']}\n\n")

        for pos, rune in state["runes"].items():
            f.write(f"{pos}: {rune}\n")
def switch_turn():
    state["turn"] = "Player2" if state["turn"] == "Player1" else "Player1"
@app.route("/")
def index():
    return render_template(
        "board.html",
        board_size=BOARD_SIZE,
        turn=state["turn"],
        positions=state["positions"],
        scores=state["scores"],
        runes=state["runes"],
        last_message=state["last_message"]
    )
@app.route("/move")
def move():
    player = state["turn"]
    old_pos = state["positions"][player]
    if player == "Player1":
        new_pos = old_pos + 1
    else:
        new_pos = old_pos - 1
    state["positions"][player] = new_pos
    msg = f"{player} moved from {old_pos} to {new_pos}"
    if new_pos in state["runes"]:
        state["scores"][player] += 1
        rune = state["runes"].pop(new_pos)
        msg += f" and collected a {rune} rune (+1 point)"
    if new_pos == CENTER_TILE:
        state["last_message"] = msg + f". {player} reached the center and WINS!"
        save_game()
        return redirect(url_for("index"))
    state["last_message"] = msg + "."
    switch_turn()
    save_game()
    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    global state
    state = default_state()
    save_game()
    return redirect(url_for("index"))

if __name__ == "__main__":
    load_game()
    save_game()
    app.run(debug=True)
