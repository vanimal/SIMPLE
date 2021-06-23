from gym.envs.registration import register

register(
    id='CantStop-v0',
    entry_point='cantstop.envs:CantStopEnv',
)

