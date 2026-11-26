
import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S

NP -> Nominal | Det Nominal | NP PP

Nominal -> N | Adj Nominal

VP -> V | V NP | Adv VP | VP Adv | VP PP | VP Conj VP

PP -> P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()
    else:
        s = input("Sentence: ")

    s = preprocess(s)

    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return

    if not trees:
        print("Could not parse sentence.")
        return

    for tree in trees:
        tree.pretty_print()
        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    words = nltk.word_tokenize(sentence)
    return [
        word.lower()
        for word in words
        if any(character.isalpha() for character in word)
    ]


def np_chunk(tree):
    chunks = []

    for subtree in tree.subtrees():
        if subtree.label() == "NP":
            nested_nps = [
                child
                for child in subtree.subtrees()
                if child.label() == "NP" and child is not subtree
            ]

            if not nested_nps:
                chunks.append(subtree)

    return chunks


if __name__ == "__main__":
    main()
