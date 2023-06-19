from treys import Evaluator, Card

def get_hand_strength(hole, community):
    evaluator = Evaluator()

    # Ensure hole and community cards are not empty
    if not hole or not community:
        raise ValueError("Hole cards and community cards cannot be empty")

    # Convert hole cards and community cards to the internal representation
    hole_cards = [Card.new(card) for card in hole]
    community_cards = [Card.new(card) for card in community]

    # Get the rank of the hand
    rank = evaluator.evaluate(hole_cards, community_cards)

    # Get the class of the hand (Flush, Straight, etc.)
    hand_class = evaluator.get_rank_class(rank)

    # Get a string representation of the hand
    hand_string = evaluator.class_to_string(hand_class)

    # Get the hand strength (0 is the best hand possible, 7462 is the worst hand)
    hand_strength = 1.0 - (rank / 7462)

    return rank, hand_string, hand_strength
