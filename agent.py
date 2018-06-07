import numpy as np
import matplotlib.pyplot as plt
import utils


class MonteCarlo:

  NUM_ACTIONS = 9
  NUM_SPEEDS = 5
  ACTION_TO_ACCELERATION = np.array([[1, 1], [0, 1], [1, 0], [0, 0], [-1, 0], [0, -1], [1, -1], [-1, 1], [-1, -1]])

  def __init__(self, env, epsilon):
    """
    Initialize a Monte Carlo agent for the Racetrack environment.
    Each state is visited only once in a single episode, so the first-visit / every-visit distinction does not apply.
    :param env:         An instance of the racetrack environment.
    :param epsilon:     Constant for an epsilon-greedy policy.
    """

    self.env = env
    self.epsilon = epsilon

    self.action_values = None
    self.action_counts = None
    self.policy = None
    self.reset()

  def play_episode(self, explore=True, learn=True):
    """
    Play an episode.
    :param explore:     Use exploration policy.
    :param learn:       Update action counts and values.
    :return:            Total return of the episode.
    """

    sequence = []

    while not self.env.done:

      state = self.env.get_state()

      if explore:
        action = self.explore(self.policy[state])
      else:
        action = self.policy[state]

      reward = self.env.act(*self.action_to_acceleration(action))

      sequence.append((state, action, reward))

    returns = np.zeros(len(sequence))

    for i in reversed(range(len(sequence))):
      for j in range(i + 1):
        returns[j] += sequence[i][2]

    if learn:
      for i in range(len(sequence)):

        state = sequence[i][0]
        action = sequence[i][1]
        state_action = state + (action,)
        ret = returns[i]

        self.action_values[state_action] += utils.update_mean(ret, self.action_values[state_action],
                                                              self.action_counts[state_action])
        self.action_counts[state_action] += 1

    return returns[0]

  def reset(self):
    """
    Reset agent.
    :return:    None.
    """

    self.action_values = \
      np.zeros((self.env.racetrack.shape[0], self.env.racetrack.shape[1], self.NUM_SPEEDS, self.NUM_SPEEDS,
                self.NUM_ACTIONS), dtype=np.float32)
    self.action_counts = \
      np.zeros((self.env.racetrack.shape[0], self.env.racetrack.shape[1], self.NUM_SPEEDS, self.NUM_SPEEDS,
                self.NUM_ACTIONS), dtype=np.int32)
    self.policy = np.zeros((self.env.racetrack.shape[0], self.env.racetrack.shape[1], self.NUM_SPEEDS, self.NUM_SPEEDS),
                           dtype=np.int32)

  def update_policy(self):
    """
    Update epsilon-greedy policy using current action values.
    :return:    None.
    """

    # play action with maximum action value
    self.policy = np.argmax(self.action_values, axis=-1)

  def action_to_acceleration(self, action):
    """
    Translate action index into acceleration in x and y axes.
    :param action:    Action index.
    :return:          Acceleration in x and y axes.
    """

    return self.ACTION_TO_ACCELERATION[action]

  def explore(self, action):

    if np.random.uniform(0, 1) < self.epsilon:
      return np.random.randint(0, self.NUM_ACTIONS)
    else:
      return action

  def show_policy(self):

    for i in range(self.NUM_SPEEDS):
      for j in range(self.NUM_SPEEDS):
        plt.imshow(self.policy[:, :, i, i])
        plt.colorbar()
        plt.show()