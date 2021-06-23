import gym
import numpy as np

from stable_baselines import logger

from functools import reduce

from .classes import Game

class CantStopEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self, verbose = False, manual = False):
    super(CantStopEnv, self).__init__()

    self.name = 'cantstop'
    self.manual = manual
    self.verbose = verbose

    self.n_players = 2

    self.action_space = gym.spaces.Discrete(8)

    boardSpaces = 83
    self.observation_size = (self.n_players + 1) * boardSpaces + 24
    self.observation_space = gym.spaces.Box(0, 1, (self.observation_size + self.action_space.n,))

  @property
  def observation(self):
    obs = np.zeros(self.observation_size)

    spots = reduce(lambda p, c: p + c.content, self.game.board, [])

    for i, t in enumerate(list(range(self.n_players)) + ['T']):
      for j, s in enumerate(spots):
        if (s == t):
          obs[83 * i + j] = 1

    if (self.game.dice is not None):
      for i, d in enumerate(self.game.dice):
        obs[83 * (self.n_players + 1) + i * 6 + d - 1] = 1

    return np.append(obs, self.legal_actions)

  @property
  def legal_actions(self):
    actions = np.zeros(self.action_space.n)

    if self.game.dice is None:
      actions[0] = 1
      actions[1] = 1 if any([c for c in self.game.board if c.active]) else 0
    else:
      for i, v in enumerate(self.game.moveValid):
        if v:
          actions[i + 2] = 1

    return actions

  def step(self, action):
    self.steps += 1

    if (self.steps > 1000):
      return self.observation, [-1] * self.n_players, True, {}

    if action == 0:
        self.game.roll()
    elif action == 1:
        self.game.skip()
    else:
        self.game.apply(action - 2)

    self.current_player_num = self.game.currentPlayer

    done = self.game.winner is not None
    reward = [0] * self.n_players

    if done:
      reward = [1 if i == self.game.winner else -1 / (self.n_players - 1) for i in range(self.n_players)]

    return self.observation, reward, done, {}

  def reset(self):
    self.game = Game(self.n_players)
    self.steps = 0
    self.current_player_num = self.game.currentPlayer

  def render(self, mode='human', close=False):
    if close:
        return

    logger.debug(str(self.game))

    if (self.game.winner is not None):
      logger.debug(f'Player {self.game.winner} wins.')
    elif (self.game.dice is None):
      logger.debug('0: Roll, 1: Pass')
    else:
      logger.debug(', '.join([f'{i + 2}: {self.game._sums(move)}' for i, move in enumerate(self.game.moves) if self.game.moveValid[i]]))
