from gymnasium.envs.registration import register

register(
    id='Pygame-v0',
    entry_point='exchange_env.envs:CustomEnv',
    max_episode_steps=2000,
)
