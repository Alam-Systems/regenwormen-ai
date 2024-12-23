from typing import Optional
import gymnasium as gym
import numpy as np


class InvalidAction(Exception):
    pass


MIN_TILE_VALUE = 21
MAX_POINTS = 40


class RegenwormenEnv(gym.Env):
    def __init__(self):
        self.engine = RegenwormenEngine()
        self.player = self.engine.players[0]

        self.action_space = gym.spaces.Discrete(8)
        self.observation_space = gym.spaces.Box(0, 1, shape=(2,))

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed, options=options)
        self.engine.reset(seed=seed)
        return self._get_current_obs(), {}

    def step(self, action):
        prev_worm_count = self.player.state["worm_count"]

        try:
            if action == 0:
                self.engine.throw_dice()
                if self.engine.turn_failed_after_throw:
                    self.engine.finalize_turn(outcome=-1)
                    self._let_other_players_take_turn()

            elif action == 1:
                self.engine.finalize_turn(outcome=1)
                self._let_other_players_take_turn()

            elif action > 1:
                self.player.take_die(die_number=action)
                if self.engine.turn_failed_after_die_select:
                    self.engine.finalize_turn(outcome=-1)
                    self._let_other_players_take_turn()

        except InvalidAction:
            return (
                self._get_current_obs(),
                -1000,
                True,
                False,
                {},
            )

        reward = self.player.state["worm_count"] - prev_worm_count
        if self.engine.is_game_over:
            if self.engine.winner == self.player:
                reward = 100

        return (
            self._get_current_obs(),
            reward,
            self.engine.is_game_over,
            False,
            {},
        )

    def render(self, mode="human"):
        print(f"""
Player:
  Upper tile: {self.player.open_tile}
  Worm count: {self.player.worm_count}
  Dice: {self.player.state["dice"]}

Opponents:
  {[f"Upper tile: {player.open_tile}\n  Worm count: {player.worm_count}\n\n" for player in self.engine.players if player is not self.player]}

Open tiles: {self.engine.open_tiles}
""")

    def _let_other_players_take_turn(self):
        next_player = self.engine.current_player
        while next_player is not self.player:
            next_player.take_turn()
            next_player = self.engine.current_player

    def _get_current_obs(self) -> np.ndarray:
        observation = self._encode_dice_values(self.engine.dice_values)
        observation.extend(self._encode_tiles(self.engine.open_tiles))
        for player in self.engine.players:
            observation.extend(self._encode_player_state(player))

        observation.extend(self._encode_dice_values(self.player.state["dice"]))

        return np.array(observation, dtype=np.float32)

    def _encode_tiles(self, tiles: list[int]) -> list[float]:
        encoded_tiles = [0.0] * 16
        for tile in tiles:
            encoded_tiles[tile - MIN_TILE_VALUE] = 1.0

        return encoded_tiles

    def _encode_dice_values(self, dice_values: list[int]) -> list[float]:
        encoded_dice_values = [0.0] * 6
        for dice in dice_values:
            encoded_dice_values[dice - 1] += 1 / 6

        return encoded_dice_values

    def _encode_player_state(self, player) -> list[float]:
        state = self._encode_tiles([])
        if player.open_tile != -1:
            state[player.open_tile - MIN_TILE_VALUE] = 1.0

        state.append(player.worm_count / MAX_POINTS)
        return state
