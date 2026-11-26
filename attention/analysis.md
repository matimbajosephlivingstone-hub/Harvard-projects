# Analysis

## Layer 3, Head 10

This attention head appears to capture direct object and verb-noun relationships, where transitive verbs attend strongly to the nouns that serve as their direct objects. When predicting a masked noun following an action verb, this head focuses heavily on the preceding verb to determine what kind of object makes semantic sense in that context.

Example Sentences:
- The chef carefully prepared the [MASK] for the guests.
- She opened the heavy [MASK] and walked into the room.

## Layer 4, Head 11

This attention head appears to track determiner-noun and adjective-noun modifier relationships, connecting articles (such as "the" or "a") and descriptive adjectives directly to the head noun they modify. In the attention diagrams, noun tokens show high attention weights toward their preceding determiners and adjectives, helping BERT identify noun phrase boundaries.

Example Sentences:
- A bright red [MASK] was parked outside the building.
- He picked up the old dusty [MASK] from the top shelf.

