from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from regenwormen_engine import RegenwormenEngine


class BaseStrategy(ABC):
    def __init__(self, name:str, game_engine:"RegenwormenEngine"):
        self.name = name 
        self.game_engine = game_engine
        self.tiles = []
        self.selected_dice = []
    
    def reset_game(self):
        self.tiles = []
        self.selected_dice = []
        return self
    
    def end_turn(self):
        self.selected_dice = []
    
    @abstractmethod
    def take_die(self, **kwargs) -> int | str:
        """Select a set of dice based on the selected dice and the rolled dice"""
        pass

    @abstractmethod
    def determine_to_take_tile(self, **kwargs) -> bool:
        """Function to determine whether to take a tile or to roll dice again"""
        pass

    @property
    def open_tile(self):
        if len(self.tiles) == 0:
            return -1
        return self.tiles[-1]

    @property
    def wurm_count(self):
        return sum([(x-17)//4 for x in self.tiles])

    @property
    def current_dice_score(self) -> int:
        """The current amount of points in the selected dice"""
        return sum(self.selected_dice) - self.selected_dice.count(6)
    
    @staticmethod
    def tile_to_worms(tile_points):
        """Number of worm for a given tile"""
        return min((tile_points - 17) // 4, 4)
    
    def take_turn(self) -> tuple[int | str | None, list[int|str]]:
        """Returns the type of action (dead, take tile or take dice)
        and the dice that were rolled."""
        
        while True:
            self.game_engine.throw_dice()
            if self.game_engine.turn_failed_after_throw:
                outcome = -1
                break
            
            die_to_take = self.take_die()
            if self.game_engine.turn_failed_after_die_select:
                outcome = -1
                break
            self.game_engine.take_die(die_to_take)

            if self.determine_to_take_tile():
                outcome = 1
                break
        
        self.game_engine.finalize_turn(outcome=outcome)
    
    @property
    def dice_points(self):
        return sum(self.selected_dice) - self.selected_dice.count(6)
