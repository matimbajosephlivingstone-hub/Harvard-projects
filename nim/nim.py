
import math
import random
import time


class Nim():

    def __init__(self, initial=[1, 3, 5, 7]):
        """
        Initialize game board.
        Each game board has
            - `piles`: a list of how many elements remain in each pile
            - `player`: 0 or 1 to indicate which player's turn
            - `winner`: None, 0, or 1 to indicate who the winner is
        """
        self.piles = initial.copy()
        self.player = 0
        self.winner = None

    @classmethod
    def available_actions(cls, piles):
        """
        Return all available actions in a state.
        """
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions

    @classmethod
    def other_player(cls, player):
        """
        Return the other player.
        """
        return 0 if player == 1 else 1

    def switch_player(self):
        """
        Switch the current player.
        """
        self.player = Nim.other_player(self.player)

    def move(self, action):
        """
        Make a move for the current player.
        """
        pile, count = action

        if self.winner is not None:
            raise Exception("Game already won")
        elif pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile")
        elif count < 1 or count > self.piles[pile]:
            raise Exception("Invalid number of objects")

        self.piles[pile] -= count
        self.switch_player()

        if all(pile == 0 for pile in self.piles):
            self.winner = self.player


class NimAI():

    def __init__(self, alpha=0.5, epsilon=0.1):
        """
        Initialize AI with an empty Q-learning dictionary.
        """
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        """
        Update Q-values using Q-learning.
        """
        old = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(
            old_state, action, old, reward, best_future
        )

    def get_q_value(self, state, action):
        """
        Return the Q-value for a state/action pair.
        Return 0 if the pair does not exist.
        """
        state = tuple(state)
        return self.q.get((state, action), 0)

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update the Q-value using the Q-learning formula.
        """
        new_value = reward + future_rewards

        updated_q = old_q + self.alpha * (new_value - old_q)

        self.q[(tuple(state), action)] = updated_q

    def best_future_reward(self, state):
        """
        Return the highest Q-value for any available action.
        """
        actions = Nim.available_actions(state)

        if not actions:
            return 0

        return max(
            self.get_q_value(state, action)
            for action in actions
        )

    def choose_action(self, state, epsilon=True):
        """
        Choose an action using epsilon-greedy strategy.
        """
        actions = list(Nim.available_actions(state))

        if not actions:
            return None

        # Explore: choose a random action
        if epsilon and random.random() < self.epsilon:
            return random.choice(actions)

        # Exploit: choose the action with the highest Q-value
        best_value = max(
            self.get_q_value(state, action)
            for action in actions
        )

        best_actions = [
            action for action in actions
            if self.get_q_value(state, action) == best_value
        ]

        return random.choice(best_actions)


def train(n):
    """
    Train an AI by playing n games against itself.
    """

    player = NimAI()

    for i in range(n):
        print(f"Playing training game {i + 1}")
        game = Nim()

        last = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        while True:

            state = game.piles.copy()
            action = player.choose_action(game.piles)

            last[game.player]["state"] = state
            last[game.player]["action"] = action

            game.move(action)
            new_state = game.piles.copy()

            if game.winner is not None:
                player.update(state, action, new_state, -1)

                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    1
                )
                break

            elif last[game.player]["state"] is not None:
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    0
                )

    print("Done training")

    return player


def play(ai, human_player=None):
    """
    Play a human game against the AI.
    """

    if human_player is None:
        human_player = random.randint(0, 1)

    game = Nim()

    while True:

        print()
        print("Piles:")

        for i, pile in enumerate(game.piles):
            print(f"Pile {i}: {pile}")

        print()

        available_actions = Nim.available_actions(game.piles)
        time.sleep(1)

        if game.player == human_player:
            print("Your Turn")

            while True:
                try:
                    pile = int(input("Choose Pile: "))
                    count = int(input("Choose Count: "))

                    if (pile, count) in available_actions:
                        break

                    print("Invalid move, try again.")

                except ValueError:
                    print("Please enter valid numbers.")

        else:
            print("AI's Turn")
            pile, count = ai.choose_action(
                game.piles, epsilon=False
            )
            print(f"AI chose to take {count} from pile {pile}.")

        game.move((pile, count))

        if game.winner is not None:
            print()
            print("GAME OVER")

            winner = "Human" if game.winner == human_player else "AI"

            print(f"Winner is {winner}")
            return
