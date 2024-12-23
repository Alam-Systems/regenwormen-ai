from regenwormen_ai.strategies.base_strategy import BaseStrategy
import random


class RandomStrategy(BaseStrategy):

    def take_die(self):
        die_options = [x for x in self.game_engine.thrown_dice if x not in self.selected_dice]
        choice = random.choice(die_options)
        return choice
    
    def determine_to_take_tile(self):
        if self.game_engine.can_take_tile:
            choice = random.choice([True, False])
            return choice
        return False
    


