
import random
from regenwormen_ai.constants import N_DICE

class RegenwormenEngine():
    def __init__(self, verbose:bool = False, seed=None):
        self.verbose = verbose
        self.players = []
        self.open_tiles = list(range(21, 37))
        self.current_player_idx = 0
        if seed is not None:
            random.seed(seed)
    
    def add_player(self, player):
        self.players.append(player)

    def finalize_turn(self, outcome:int):
        if outcome == -1:
            if len(self.current_player.tiles) > 0:
                popped_tile = self.current_player.tiles.pop()
                self.open_tiles.append(popped_tile)
                self.open_tiles.sort()
            self.open_tiles.pop()
            return
        
        # player wants to take a tile
        if not self.can_take_tile:
            raise ValueError("Player wants to take tile, but can't")
        
        tile = self.tile_to_take()

        if tile in self.open_tiles:
            self.open_tiles.remove(tile)
        else:
            for player in [p for p in self.players if p is not self.current_player]:
                if player.tiles[-1] == tile:
                    player.tiles.pop()
                    break
        
        self.current_player.tiles.append(tile)
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        
    def take_die(self, die_to_take:int):
        if die_to_take not in self.thrown_dice:
            raise ValueError(f"Die {die_to_take} is not in the thrown dice")
        if die_to_take in self.current_player.selected_dice:
            raise ValueError(f"Die {die_to_take} is already selected")
        
        self.current_player.selected_dice.extend([x for x in self.thrown_dice if x == die_to_take])
        self.thrown_dice = []

    def reset(self, seed=None):
        self.players = [player.reset_game() for player in self.players]
        self.open_tiles = list(range(21, 37))
        self.current_player_idx = 0
        self.thrown_dice = []
        if seed is not None:
            random.seed(seed)
    
    @property
    def current_player(self):
        return self.players[self.current_player_idx]
    
    @property
    def turn_failed_after_throw(self):
        if all([die in self.current_player.selected_dice for die in self.thrown_dice]):
            return True
        return False

    @property
    def turn_failed_after_die_select(self):
        if self.can_take_tile:
            return False
        if (
            len(self.current_player.selected_dice) - N_DICE == 0 or
            all([x in self.current_player.selected_dice for x in range(1, 7)])
        ):
            return True
        
        return False

    @property
    def is_game_over(self):
        return len(self.open_tiles) == 0
    
    @property
    def winner(self):
        if not self.is_game_over:
            raise ValueError("Game is not over yet")
        
        return sorted(
            self.players, key=lambda x: x.wurm_count, reverse=True
        )

    def get_open_and_stealable_tiles(self):
        open_tiles = self.open_tiles
        stealable_tiles = []
        for player in [p for p in self.players if p is not self.current_player]:
            if player.open_tile != -1:
                stealable_tiles.append(player.open_tile) 
        return sorted(open_tiles + stealable_tiles)

    def tile_to_take(self):
        if not 6 in self.current_player.selected_dice:
            return None
        tiles = self.get_open_and_stealable_tiles()
        tiles_to_take = [x for x in tiles if x <= self.current_player.dice_points]
        if len(tiles_to_take) == 0:
            return None
        return max(tiles_to_take)


    @property
    def can_take_tile(self):
        if self.tile_to_take() is None:
            return False
        return True

    def throw_dice(self):
        self.thrown_dice = [random.randint(1, 6) for _ in range(N_DICE - len(self.current_player.selected_dice))]
    



