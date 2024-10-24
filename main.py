from flask import Flask, render_template, request
import random

app = Flask(__name__)

choices = ['rock', 'paper', 'scissors']

def determine_winner(player, computer):
    """
    Determine the winner based on player and computer choices
    returning win, lose or tie
    :param player:
    :param computer:
    :return:
    """
    if player == computer:
        return 'tie'
    elif (
        player == 'rock' and computer == 'scissors' or
        player == 'paper' and computer == 'rock' or
        player == 'scissor' and computer == 'paper'
    ): return 'win'
    else:
        return 'lose'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play', methods=['POST'])
def play():
    """
    Play single round and return result
    :return:
    """
    player_choice = request.form['choice']
    computer_choice = random.choice(choices)

    result = determine_winner(player_choice, computer_choice)

    return render_template('result.html', player_choice=player_choice,
                           computer_choice=computer_choice, result=result)

if __name__ == '__main__':
    app.run(debug=True)