import random
from datetime import datetime

def roll_dice(dice_expression):
    try:
        num_dice, dice_modifier = dice_expression.split('d')
        num_dice = int(num_dice)

        if '+' in dice_modifier:
            sides, modifier = dice_modifier.split('+')
            modifier = int(modifier)
        elif '-' in dice_modifier:
            sides, modifier = dice_modifier.split('-')
            modifier = -int(modifier)
        else:
            sides = dice_modifier
            modifier = 0

        sides = int(sides)
        
        # Roll the dice
        total = sum(random.randint(1, sides) for _ in range(num_dice)) + modifier
        
        # Get the timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return total, timestamp

    except ValueError:
        return None, None
