import argparse
import gymnasium as gym

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

gym.register(
    id="Regenwormen-v0",
    entry_point="regenwormen.env:RegenwormenEnv",
)


def main(manual):
    env = gym.make("Regenwormen-v0")
    model = PPO("MlpPolicy", env)
    model.learn(total_timesteps=25000)

    done = False
    obs = env.reset()
    while True:
        if manual:
            action = int(input("Enter action: "))
        else:
            action, _states = model.predict(obs)

        obs, rewards, dones, info = env.step(action)
        env.render()

    # env = gym.make("Regenwormen-v0")
    # import pdb

    # pdb.set_trace()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", action="store_true")

    args = parser.parse_args()
    main(args.manual)
