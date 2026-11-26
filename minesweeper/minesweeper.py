
import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)

            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation of the board.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines neighboring a cell.
        """

        count = 0

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks whether all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game.

    A sentence consists of a set of cells and a count
    of how many of those cells are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns all cells known to be mines.
        """
        if len(self.cells) > 0 and self.count == len(self.cells):
            return set(self.cells)

        return set()

    def known_safes(self):
        """
        Returns all cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)

        return set()

    def mark_mine(self, cell):
        """
        Updates the sentence when a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates the sentence when a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player.
    """

    def __init__(self, height=8, width=8):

        self.height = height
        self.width = width

        # Keep track of moves already made
        self.moves_made = set()

        # Keep track of known mines and safe cells
        self.mines = set()
        self.safes = set()

        # Store logical knowledge
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine and updates all knowledge.
        """
        if cell in self.mines:
            return

        self.mines.add(cell)

        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe and updates all knowledge.
        """
        if cell in self.safes:
            return

        self.safes.add(cell)

        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Updates the AI's knowledge after a safe cell is revealed.
        """

        # 1. Record the move
        self.moves_made.add(cell)

        # 2. Mark the revealed cell as safe
        self.mark_safe(cell)

        # 3. Find neighboring cells that are still unknown
        neighbors = set()

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:

                    neighbor = (i, j)

                    if neighbor in self.mines:
                        count -= 1

                    elif neighbor not in self.safes:
                        neighbors.add(neighbor)

        # 4. Add the new logical sentence
        if neighbors:
            new_sentence = Sentence(neighbors, count)

            if new_sentence not in self.knowledge:
                self.knowledge.append(new_sentence)

        # 5. Keep making logical inferences until no new
        # information can be discovered.
        while True:

            new_mines = set()
            new_safes = set()

            # Discover known mines and safe cells
            for sentence in self.knowledge:

                new_mines.update(sentence.known_mines())
                new_safes.update(sentence.known_safes())

            # Remove facts already known
            new_mines -= self.mines
            new_safes -= self.safes

            # Update the knowledge base
            for mine in new_mines:
                self.mark_mine(mine)

            for safe in new_safes:
                self.mark_safe(safe)

            # Remove empty sentences
            self.knowledge = [
                sentence for sentence in self.knowledge
                if sentence.cells
            ]

            # 6. Infer new sentences using the subset method
            new_sentences = []

            for sentence1, sentence2 in itertools.combinations(
                self.knowledge, 2
            ):

                if sentence1.cells < sentence2.cells:

                    cells = sentence2.cells - sentence1.cells
                    count = sentence2.count - sentence1.count

                    if cells and 0 <= count <= len(cells):

                        new_sentence = Sentence(cells, count)

                        if (
                            new_sentence not in self.knowledge
                            and new_sentence not in new_sentences
                        ):
                            new_sentences.append(new_sentence)

                elif sentence2.cells < sentence1.cells:

                    cells = sentence1.cells - sentence2.cells
                    count = sentence1.count - sentence2.count

                    if cells and 0 <= count <= len(cells):

                        new_sentence = Sentence(cells, count)

                        if (
                            new_sentence not in self.knowledge
                            and new_sentence not in new_sentences
                        ):
                            new_sentences.append(new_sentence)

            # Stop when no new knowledge can be inferred
            if not new_mines and not new_safes and not new_sentences:
                break

            self.knowledge.extend(new_sentences)

    def make_safe_move(self):
        """
        Returns a known safe move that has not already been made.
        Returns None if no safe move is available.
        """

        available_moves = self.safes - self.moves_made

        if available_moves:
            return next(iter(available_moves))

        return None

    def make_random_move(self):
        """
        Returns a random move that has not already been made
        and is not known to be a mine.
        """

        available_moves = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made
            and (i, j) not in self.mines
        ]

        if available_moves:
            return random.choice(available_moves)

        return None
