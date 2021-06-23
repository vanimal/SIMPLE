import itertools
import secrets

class Game:
  def __init__(self, num_players):
    self.num_players = num_players
    self.currentPlayer = secrets.randbelow(num_players)
    self.board = [Column(13 - 2 * abs(7-r)) for r in range(2, 13)]
    self.dice = None
    self.winner = None

    halfMoves = list(itertools.combinations(range(4), 2))
    self.moves = list(zip(halfMoves, reversed(halfMoves)))

    self.moveValid = [False for _ in self.moves]

  def roll(self):
    self.dice = [secrets.randbelow(6) + 1 for _ in range(4)]

    open = self._hasOpenPositions()
    available = [c.available and (open or c.active) for c in self.board]
    sums = [self._sums(move) for move in self.moves]
    self.moveValid = [available[s - 2] or available[t - 2] for (s, t) in sums]

    if (not any(self.moveValid)):
      self._bust()

  def skip(self):
    for c in self.board:
      c.commit(self.currentPlayer)

    self.currentPlayer = (self.currentPlayer + 1) % self.num_players

  def apply(self, move):
    sums = self._sums(self.moves[move])

    for s in sums:
      self._apply(s)

    self.dice = None

    if (len([c for c in self.board if c.winner in (self.currentPlayer, 'T')]) == 3):
      self.winner = self.currentPlayer

  def _bust(self):
    for c in self.board:
      c.bust()

    self.currentPlayer = (self.currentPlayer + 1) % self.num_players
    self.dice = None

  def _apply(self, sum):
    open = self._hasOpenPositions()
    column = self.board[sum - 2]

    if (open or column.active):
      column.advance(self.currentPlayer)

  def _sums(self, move):
    ((i,j), (k,l)) = move

    return (self.dice[i] + self.dice[j], self.dice[k] + self.dice[l])

  def _hasOpenPositions(self):
    return len([c for c in self.board if c.active]) < 3

  def __str__(self):
    return '\n'.join([f'{i+2:2}: {str(c).center(13)}' for i, c in enumerate(self.board)])

class Column:
  def __init__(self, height):
    self.content = [None] * height
    self.available = True
    self.active = False

  def advance(self, player):
    if not self.available:
      return

    if self.active:
      start = self._find('T')
    else:
      start = self._find(player)

    next = start + 1

    while self.content[next] != None:
      next += 1

    if self.active:
      self.content[start] = None

    self.content[next] = 'T'
    self.active = True
    self.available = self.content[-1] == None

  def commit(self, player):
    if not self.active:
      return

    moved = False

    for index, value in reversed(list(enumerate(self.content))):
      if value == 'T':
        self.content[index] = player
        moved = True
      if moved and value == player:
        self.content[index] = None

    self.active = False
    self.available = self.content[-1] == None

  def bust(self):
    if not self.active:
      return

    for index, value in enumerate(self.content):
      if value == 'T':
        self.content[index] = None

    self.active = False
    self.available = self.content[-1] == None

  @property
  def winner(self):
    return self.content[-1]

  def _find(self, value):
    try:
      return self.content.index(value)
    except:
      return -1

  def __str__(self):
    return ''.join(['_' if c is None else str(c) for c in self.content])
