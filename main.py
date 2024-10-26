import random

def get_computer_choice():
    """Generate random choice for computer"""
    choices = ['rock', 'paper', 'scissors']
    return random.choice(choices)

def determine_winner(player_choice, computer_choice):
    """Determine the game result based on player and computer choice"""
    if player_choice == computer_choice:
        return "It's a Tie!"
    elif (
            (player_choice == 'rock' and computer_choice == 'scissors') or
            (player_choice == 'scissors' and computer_choice == 'paper') or
            (player_choice == 'paper' and computer_choice == 'rock')
    ): return 'You Win!'
    else:
        return 'You Lose :('