from treys import Card, Evaluator, Deck
from table_information import print_game_stage, active_player # Import the print_game_stage function




def calculate_hand_strength_and_equity_treys(hole_cards, community_cards=None, num_opponents=5, num_simulations=3000, player_actions=None, player_names=None):
    if not hole_cards:
        return None, None

    if community_cards is None:
        community_cards = []

    game_stage = print_game_stage(community_cards)

    if game_stage == "Pre-flop":
        num_simulations = 10000

    evaluator = Evaluator()
    hole_cards_converted = [Card.new(card) for card in hole_cards]
    community_cards_converted = [Card.new(card) for card in community_cards]

    if player_actions and player_names:
        active_status = active_player(player_actions, player_names)
        num_active_opponents = active_status.count('Y')
        num_opponents = num_active_opponents

    wins = 0
    total = 0

    for _ in range(num_simulations):
        deck = Deck()
        for card in hole_cards_converted + community_cards_converted:
            deck.cards.remove(card)

        if game_stage == "Pre-flop":
            remaining_community_cards = deck.draw(5)
        elif game_stage == "Flop":
            remaining_community_cards = community_cards_converted + deck.draw(2)
        elif game_stage == "Turn":
            remaining_community_cards = community_cards_converted + deck.draw(1)
        elif game_stage == "River":
            remaining_community_cards = community_cards_converted
        else:
            raise ValueError("Invalid game stage provided.")

        hand_strength = evaluator.evaluate(hole_cards_converted, remaining_community_cards)

        all_opponents_beaten = True
        for _ in range(num_opponents):
            opponent_hole_cards = deck.draw(2)
            opponent_hand_strength = evaluator.evaluate(opponent_hole_cards, remaining_community_cards)

            if hand_strength >= opponent_hand_strength:
                all_opponents_beaten = False
                break

        if all_opponents_beaten:
            wins += 1

        total += 1

    hand_equity = wins / total

    return hand_strength, hand_equity






def convert_card_notation(card):
    if not card:
        return None
    suit_conversion = {'S': 's', 'H': 'h', 'D': 'd', 'C': 'c'}
    rank, suit = card[:-1], card[-1]
    return rank + suit_conversion[suit]





if __name__ == "__main__":
    # Input hole cards and community cards manually
    hole_cards_input = ["8S", "5H"]  # Aces of Spades and Hearts
    community_cards_input = ["AS", "4D", "6S", "8H"]  # Flop example

    # Convert cards to the format used in the calculate_hand_strength_and_equity_treys function
    hole_cards = [convert_card_notation(card) for card in hole_cards_input]
    community_cards = [convert_card_notation(card) for card in community_cards_input]

    # Calculate hand strength and equity
    hand_strength, hand_equity = calculate_hand_strength_and_equity_treys(hole_cards, community_cards)

    print("Hole Cards:", hole_cards_input)
    print("Community Cards:", community_cards_input)
    print("Hand Strength:", hand_strength)
    print("Hand Equity:", hand_equity)
