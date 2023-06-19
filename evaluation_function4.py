from treys import Card, Evaluator, Deck
from table_information import print_game_stage, active_player, convert_stack_size_to_float
from player_stats_detector import get_player_stats
import random

# Define hand ranges for each position
HAND_RANGES = {
    'Under the Gun': {
        'Fold': ['2S', '2H', '2D', '2C', '3S', '3H', '3D', '3C', '4S', '4H', '4D', '4C', '5S', '5H', '5D', '5C', '6S', '6H', '6D', '6C', '7S', '7H', '7D', '7C'],
        'Call': ['8S', '8H', '8D', '8C', '9S', '9H', '9D', '9C', 'TS', 'TH', 'TD', 'TC', 'JS', 'JH', 'JD', 'JC', 'QS', 'QH', 'QD', 'QC'],
        'Raise': ['KS', 'KH', 'KD', 'KC', 'AS', 'AH', 'AD', 'AC']
    },
    'Middle Position': {
        'Fold': ['2S', '2H', '2D', '2C', '3S', '3H', '3D', '3C', '4S', '4H', '4D', '4C'],
        'Call': ['5S', '5H', '5D', '5C', '6S', '6H', '6D', '6C', '7S', '7H', '7D', '7C', '8S', '8H', '8D', '8C', '9S', '9H', '9D', '9C'],
        'Raise': ['TS', 'TH', 'TD', 'TC', 'JS', 'JH', 'JD', 'JC', 'QS', 'QH', 'QD', 'QC', 'KS', 'KH', 'KD', 'KC', 'AS', 'AH', 'AD', 'AC']
    },
    'Cut Off': {
        'Fold': ['2S', '2H', '2D', '2C'],
        'Call': ['3S', '3H', '3D', '3C', '4S', '4H', '4D', '4C', '5S', '5H', '5D', '5C', '6S', '6H', '6D', '6C', '7S', '7H', '7D', '7C'],
        'Raise': ['8S', '8H', '8D', '8C', '9S', '9H', '9D', '9C', 'TS', 'TH', 'TD', 'TC', 'JS', 'JH', 'JD', 'JC', 'QS', 'QH', 'QD', 'QC', 'KS', 'KH', 'KD', 'KC', 'AS', 'AH', 'AD', 'AC']
    },
    'Button': {
        'Fold': [],
        'Call': ['2S', '2H', '2D', '2C', '3S', '3H', '3D', '3C', '4S', '4H', '4D', '4C', '5S', '5H', '5D', '5C', '6S', '6H', '6D', '6C'],
        'Raise': ['7S', '7H', '7D', '7C', '8S', '8H', '8D', '8C', '9S', '9H', '9D', '9C', 'TS', 'TH', 'TD', 'TC', 'JS', 'JH', 'JD', 'JC', 'QS', 'QH', 'QD', 'QC', 'KS', 'KH', 'KD', 'KC', 'AS', 'AH', 'AD', 'AC']
    },
    'Small Blind': {
        'Fold': ['2S', '2H', '2D', '2C', '3S', '3H', '3D', '3C'],
        'Call': ['4S', '4H', '4D', '4C', '5S', '5H', '5D', '5C', '6S', '6H', '6D', '6C', '7S', '7H', '7D', '7C', '8S', '8H', '8D', '8C'],
        'Raise': ['9S', '9H', '9D', '9C', 'TS', 'TH', 'TD', 'TC', 'JS', 'JH', 'JD', 'JC', 'QS', 'QH', 'QD', 'QC', 'KS', 'KH', 'KD', 'KC', 'AS', 'AH', 'AD', 'AC']
    },
    'Big Blind': {
        'Fold': ['2S', '2H', '2D', '2C'],
        'Call': ['3S', '3H', '3D', '3C', '4S', '4H', '4D', '4C', '5S', '5H', '5D', '5C', '6S', '6H', '6D', '6C', '7S', '7H', '7D', '7C', '8S', '8H', '8D', '8C'],
        'Raise': ['9S', '9H', '9D', '9C', 'TS', 'TH', 'TD', 'TC', 'JS', 'JH', 'JD', 'JC', 'QS', 'QH', 'QD', 'QC', 'KS', 'KH', 'KD', 'KC', 'AS', 'AH', 'AD', 'AC']
    },
    'Unknown': {
        'Fold': ['2S', '2H', '2D', '2C', '3S', '3H', '3D', '3C', '4S', '4H', '4D', '4C'],
        'Call': ['5S', '5H', '5D', '5C', '6S', '6H', '6D', '6C', '7S', '7H', '7D', '7C', '8S', '8H', '8D', '8C', '9S', '9H', '9D', '9C'],
        'Raise': ['TS', 'TH', 'TD', 'TC', 'JS', 'JH', 'JD', 'JC', 'QS', 'QH', 'QD', 'QC', 'KS', 'KH', 'KD', 'KC', 'AS', 'AH', 'AD', 'AC']
    }
}

def get_stack_size_category(stack_size, big_blind_size):
    stack_size_in_blinds = stack_size / big_blind_size
    if stack_size_in_blinds <= 10:
        return 'Small Stack'
    elif stack_size_in_blinds <= 50:
        return 'Medium Stack'
    else:
        return 'Large Stack'

def get_pot_size_category(pot_size, big_blind_size):
    pot_size_in_blinds = pot_size / big_blind_size
    if pot_size_in_blinds <= 10:
        return 'Small Pot'
    elif pot_size_in_blinds <= 50:
        return 'Medium Pot'
    else:
        return 'Large Pot'


def generate_opponent_hand_range(hole_cards, community_cards, num_opponents, player_positions, player_actions, player_stack_sizes, pot_size, big_blind_size):
    all_cards = [rank + suit for rank in '23456789TJQKA' for suit in 'shdc']
    known_cards = [convert_card_notation(card) for card in hole_cards + community_cards]
    all_cards = [card for card in all_cards if card not in known_cards]
    
    opponent_hand_ranges = []

    pot_size_category = get_pot_size_category(pot_size, big_blind_size)

    for i in range(num_opponents):
        position = player_positions[i]
        stack_size = player_stack_sizes[i]
        action = player_actions[i]
        stack_size_category = get_stack_size_category(stack_size, big_blind_size)

        possible_hands = [hand for hand in HAND_RANGES[position] if hand in all_cards]

        if possible_hands:
            if stack_size_category == 'Small Stack':
                possible_hands = [hand for hand in possible_hands if hand in HAND_RANGES['Tight']]
            elif stack_size_category == 'Deep Stack':
                possible_hands = [hand for hand in possible_hands if hand in HAND_RANGES['Loose']]
            if action in ['Bet', 'Raise']:
                if pot_size_category in ['Large Pot', 'Massive Pot']:
                    possible_hands = [hand for hand in possible_hands if hand in HAND_RANGES['Strong']]
                else:
                    possible_hands = [hand for hand in possible_hands if hand in HAND_RANGES['Semi-Strong']]
            elif action == 'Call':
                if pot_size_category in ['Large Pot', 'Massive Pot']:
                    possible_hands = [hand for hand in possible_hands if hand in HAND_RANGES['Medium']]
                else:
                    possible_hands = [hand for hand in possible_hands if hand in HAND_RANGES['Weak']]
            else:  # Check or Fold
                possible_hands = [hand for hand in possible_hands if hand in HAND_RANGES['Weak']]

            opponent_hole_cards = random.sample(possible_hands, 2)
            all_cards = [card for card in all_cards if card not in opponent_hole_cards]  # Remove chosen cards from the deck
        else:
            # If there are no possible hands for the current position, choose random cards
            opponent_hole_cards = random.sample(all_cards, 2)
            all_cards = [card for card in all_cards if card not in opponent_hole_cards]

        opponent_hand_ranges.append(opponent_hole_cards)

    return opponent_hand_ranges








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
    rank, suit = card[:-1], card[-1].upper()
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

    # Generate and print opponents' hand ranges
    num_opponents = 5
    player_positions = ['Button', 'Small Blind', 'Big Blind', 'Under the Gun', 'Middle Position', 'Cut Off']
    player_actions = ['Raise', 'Call', 'Check', 'Fold', 'Bet']
    player_names, player_stack_sizes, pot_size = get_player_stats(r"C:\Users\matus\Desktop\PokerMain\screenshot_taken\screenshot_taken.png")
    player_stack_sizes = [convert_stack_size_to_float(size) for size in player_stack_sizes]
    pot_size = convert_stack_size_to_float(pot_size)
    big_blind_size = float(input("Big blind size: "))

    opponent_hand_ranges = generate_opponent_hand_range(
        hole_cards_input,
        community_cards_input,
        num_opponents,
        player_positions,
        player_actions,
        player_stack_sizes,
        pot_size,
        big_blind_size
    )    

    print("Hole Cards:", hole_cards_input)
    print("Community Cards:", community_cards_input)
    print("Hand Strength:", hand_strength)
    print("Hand Equity:", hand_equity)

    for i, hand_range in enumerate(opponent_hand_ranges, 1):
        print(f'Opponent {i} hand range: {hand_range}')

        def print_hand_range(player_position, player_action):
            if player_position in HAND_RANGES:
                hand_range = HAND_RANGES[player_position]

                if player_action in hand_range:
                    print(f"For position {player_position} and action {player_action}, the hand range is: {hand_range[player_action]}")
                else:
                    print(f"Action {player_action} not found for position {player_position}.")
            else:
                print(f"Position {player_position} not found.")

if __name__ == "__main__":
    ...
    # Test print_hand_range function
    print_hand_range('Button', 'Call')


