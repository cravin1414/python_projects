from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from random import randint
import time

def dice_game():
    put_markdown("# 🎲 Dice Rolling Game")
    put_text("Welcome to the Dice Rolling Game! Click the button below to roll the die.")
    
    score = 0
    high_score = 0
    
    while True:
        action = actions(buttons=['Roll Dice', 'View Stats', 'Exit Game'])
        
        if action == 'Exit Game':
            toast("Thanks for playing!")
            break
            
        if action == 'View Stats':
            put_markdown("## Game Statistics")
            put_table([
                ['Current Score', score],
                ['High Score', max(score, high_score)]
            ])
            continue
            
        if action == 'Roll Dice':
            # Clear previous output
            clear('roll_result')
            
            # Animation for rolling
            with use_scope('roll_result', clear=True):
                put_text("Rolling...")
                for _ in range(3):
                    put_text("⚂")
                    time.sleep(0.3)
                    clear('roll_result')
                
                # Get random dice value (1-6)
                dice_value = randint(1, 6)
                score += dice_value
                
                # Display result with appropriate dice emoji
                dice_emojis = {
                    1: '⚀',
                    2: '⚁',
                    3: '⚂',
                    4: '⚃',
                    5: '⚄',
                    6: '⚅'
                }
                
                put_markdown(f"## You rolled: {dice_value} {dice_emojis[dice_value]}")
                put_text(f"Your current score: {score}")
                
                # Update high score if needed
                if score > high_score:
                    high_score = score
                    put_text("🎉 New high score! 🎉")

if __name__ == '__main__':
    start_server(dice_game, port=8080, debug=True)