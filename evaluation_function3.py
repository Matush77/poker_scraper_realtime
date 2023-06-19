from treys import Card, Evaluator, Deck
from table_information2 import print_game_stage, active_player, track_player_actions, previous_player_stack_sizes, is_new_round
from collections import Counter
from card_ranks import  premium_ranking_hands, high_ranking_hands, medium_ranking_hands, low_ranking_hands


def extract_bet_size(action):
    """
    Extract the size of a bet, call or raise from the action string.
    """
    if action in ['Check', 'Fold']:
        return 0
    else:
        try:
            return float(action.split('(')[1].replace(')', '').replace('$', ''))
        except IndexError:
            return 0

def average_bet_size(player_actions):
    """
    Calculate the average size of a bet, call or raise in the current round.
    """
    bet_sizes = [extract_bet_size(action) for action in player_actions.values()]
    return sum(bet_sizes) / len(bet_sizes) if bet_sizes else 0





def estimate_opponents_hand_range(num_players, player_names, player_actions, player_stack_sizes, hole_cards, community_cards, new_round, player_positions):

    # Track player actions
    tracked_player_actions = track_player_actions(player_names, player_actions, player_stack_sizes, new_round, community_cards)

    # Calculate the adjustment factor based on the board texture
    adjustment_factor = calculate_board_texture(hole_cards, community_cards, num_players)

    # Get the current stage of the game
    game_stage = print_game_stage(community_cards)

    # Iterate over each player's actions
    for i in range(num_players):
        # Start with an empty list to hold the potential hands
        potential_hands = []

        action = tracked_player_actions[i]
        position = player_positions[i]

        # Determine the bet size threshold for considering a hand to be high ranking or premium
        avg_bet_size = average_bet_size(player_actions)
        high_ranking_threshold = avg_bet_size + adjustment_factor * avg_bet_size
        premium_threshold = 1.5 * avg_bet_size + adjustment_factor * avg_bet_size

        # If a player raises or bets a large amount, they likely have a strong hand
        # Players in late positions may be more aggressive
        if action.startswith(('Raise', 'Bet')) and extract_bet_size(action) > premium_threshold:
            # If we're pre-flop, the player could have a wide range of hands
            if game_stage == "Pre-flop":
                potential_hands += premium_ranking_hands + high_ranking_hands + medium_ranking_hands + low_ranking_hands()
            else:
                # Assume they might have premium ranking hands and add them to potential hands
                potential_hands += premium_ranking_hands()

        elif action.startswith(('Raise', 'Bet')) and extract_bet_size(action) > high_ranking_threshold:
            # Assume they might have high ranking hands and add them to potential hands
            potential_hands += high_ranking_hands()

        # If a player only calls, they might have a medium strength hand
        # Players in early positions might be more conservative
        elif action.startswith('Call'):
            # Assume they might have medium ranking hands and add them to potential hands
            potential_hands += medium_ranking_hands()

        # If a player checks or folds, they likely have a weak hand
        elif action in ['Check', 'Fold']:
            # Assume they might have low ranking hands and add them to potential hands
            potential_hands += low_ranking_hands()

        print(f"Player {i+1} ({position}): {potential_hands}")





def calculate_board_texture(hole_cards, community_cards, num_opponents):
    all_cards = hole_cards + community_cards
    suits = [card[-1] for card in all_cards]
    ranks = [card[:-1] for card in all_cards]

    # Define conversion dictionary for ranks
    rank_conversion = {str(i): i for i in range(2, 10)}
    rank_conversion.update({'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14})

    # Convert ranks to integers
    ranks = [rank_conversion[rank] for rank in ranks]

    suit_counts = Counter(suits)
    rank_counts = Counter(ranks)

    # Define lists for broadway and low straight cards
    broadway_cards = [10, 11, 12, 13, 14]
    low_straight_cards = [14, 2, 3, 4, 5]

    # Define adjustment factors
    flush_adjustment = 0
    paired_adjustment = 0
    connectivity_adjustment = 0
    broadway_adjustment = 0
    low_straight_adjustment = 0
    high_card_adjustment = 0
    opponents_adjustment = 0
    set_potential_adjustment = 0
    two_pair_or_trips_potential_adjustment = 0
    blocker_effect_adjustment = 0

    # Set potential
    for card in hole_cards:
        if rank_counts[rank_conversion[card[:-1]]] == 2:
            set_potential_adjustment = 0.02
            print("Set potential!")

    # Two pair or trips potential
    for card in hole_cards:
        if rank_counts[rank_conversion[card[:-1]]] == 3:
            two_pair_or_trips_potential_adjustment = 0.04
            print("Two pair or trips potential!")

    # Blocker effect
    # For flush
    if max(suit_counts.values()) >= 4:
        for card in hole_cards:
            if card[-1] == max(suit_counts, key=suit_counts.get):
                blocker_effect_adjustment += 0.02
                print("Blocker effect for flush!")
                break
    # For straight
    sorted_ranks = sorted(ranks)
    for i in range(len(sorted_ranks) - 4):
        if sorted_ranks[i+4] - sorted_ranks[i] == 4:
            for card in hole_cards:
                if rank_conversion[card[:-1]] in sorted_ranks[i:i+4 + 1]:
                    blocker_effect_adjustment += 0.02
                    print("Blocker effect for straight!")
                    break



   # High card considerations
    if max(ranks) in ranks and max(ranks) in [rank_conversion[card[:-1]] for card in hole_cards]:
        high_card_adjustment = 0.02
        print("High card in the hole!")


    # Number of opponents considerations
    if num_opponents > 1:
        opponents_adjustment = -0.02 * num_opponents
        print("More opponents, increased risk!")

    # Adjust equity based on suitedness
    max_suit_count = max(suit_counts.values())
    if max_suit_count >= 5:  # Possible Flush or better
        flush_adjustment = -0.1
        print("Possible flush or better!")
    elif max_suit_count == 4:  # Possible Flush draw
        flush_adjustment = -0.05
        print("Possible flush draw!")

    # Adjust equity based on pairedness
    max_rank_count = max(rank_counts.values())
    if max_rank_count >= 4:  # Four of a Kind
        paired_adjustment = -0.1
        print("Four of a kind!")
    elif max_rank_count == 3:  # Possible Full House or better
        paired_adjustment = -0.07
        print("Possible full house or three of a kind!")
    elif max_rank_count == 2:  # Possible Two Pair or Three of a Kind
        paired_adjustment = -0.03
        print("Possible two pair or three of a kind!")

    # Adjust equity based on connectivity
    sorted_ranks = sorted(list(set(ranks)))
    if len(sorted_ranks) > 1:
        gaps = [b - a for a, b in zip(sorted_ranks[:-1], sorted_ranks[1:])]
        if 0 in gaps and 1 in gaps and len(sorted_ranks) >= 4:  # Multiple draw possibilities
            connectivity_adjustment = -0.08
            print("Multiple straight draw possibilities!")
        elif max(gaps) <= 1 and len(sorted_ranks) >= 5:  # Possible Straight
            connectivity_adjustment = -0.1
            print("Possible straight!")
        elif min(gaps) <= 1 and len(sorted_ranks) >= 3:  # Possible Straight draw
            connectivity_adjustment = -0.05
            print("Possible straight draw!")
        else:
            connectivity_adjustment = 0

    # Adjust equity based on presence of Broadway cards
    if any(card in ranks for card in broadway_cards):
        broadway_adjustment = -0.05
        print("Broadway cards present!")

    # Adjust equity based on potential for a low straight
    sorted_ranks = sorted(list(set([rank_conversion[card[:-1]] for card in community_cards])))
    low_straight_possibilities = [[14, 2, 3, 4, 5], [2,3,4,5,6]]
    for possibility in low_straight_possibilities:
        if set(possibility).issubset(set(sorted_ranks)):
            low_straight_adjustment = -0.03
            print("Potential for a low straight!")
            break


    # Combine all adjustments
    adjustment_factor = flush_adjustment + paired_adjustment + connectivity_adjustment + broadway_adjustment + low_straight_adjustment + high_card_adjustment + opponents_adjustment + set_potential_adjustment + two_pair_or_trips_potential_adjustment + blocker_effect_adjustment

    return adjustment_factor





def calculate_hand_strength_and_equity_treys(hole_cards, community_cards=None, num_opponents=3, num_simulations=3000, player_actions=None, player_names=None):
    if not hole_cards:
        return None, None

    if community_cards is None:
        community_cards = []

    game_stage = print_game_stage(community_cards)

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


def calculate_hand_strength_and_equity_adjusted(hole_cards, community_cards=None, num_opponents=3, num_simulations=3000, player_actions=None, player_names=None):
    if not hole_cards:
        return None, None
    
    hand_strength_adjusted, hand_equity_adjusted = calculate_hand_strength_and_equity_treys(hole_cards, community_cards, num_opponents, num_simulations, player_actions, player_names)

    adjustment_factor = calculate_board_texture(hole_cards, community_cards, num_opponents)

    # Adjust hand equity based on board texture
    hand_equity_adjusted *= (1 + adjustment_factor)

    return hand_strength_adjusted, hand_equity_adjusted



def convert_card_notation(card):
    if not card:
        return None
    suit_conversion = {'S': 's', 'H': 'h', 'D': 'd', 'C': 'c'}
    rank, suit = card[:-1], card[-1]
    return rank + suit_conversion[suit]



if __name__ == "__main__":
    # Input hole cards and community cards manually
    hole_cards_input = ["5C", "6C"]  # Aces of Spades and Hearts
    community_cards_input = ["9H", "8S", "7D"]  # Flop example

    # Convert cards to the format used in the calculate_hand_strength_and_equity_treys function
    hole_cards = [convert_card_notation(card) for card in hole_cards_input]
    community_cards = [convert_card_notation(card) for card in community_cards_input]

    # Calculate hand strength and equity
    hand_strength, hand_equity = calculate_hand_strength_and_equity_treys(hole_cards, community_cards)
    hand_strength_adjusted, hand_equity_adjusted = calculate_hand_strength_and_equity_adjusted(hole_cards, community_cards)

    print("Hole Cards:", hole_cards_input)
    print("Community Cards:", community_cards_input)
    print("Hand Strength:", hand_strength)
    print("Hand Equity:", hand_equity)
    print("Hand Strength with board texture:", hand_strength_adjusted)
    print("Hand Equity  with board texture:", hand_equity_adjusted)


        # Define a list of player stack sizes. Replace with actual values.
    player_stack_sizes = [100, 200, 150, 300]

    # Initialize a new round. Replace with actual logic to determine a new round.
    new_round = True

    
    player_names = ['Player1', 'Player2']
    player_actions = {'Player1': 'Raise (100)', 'Player2': 'Call (50)'}
    community_cards = ['9H', '8S', '7D']
    num_players = 2
    player_positions =  ['Button', 'Small Blind', 'Big Blind', 'Under the Gun', 'Middle Position', 'Cut Off']


    estimate_opponents_hand_range(num_players, player_names, player_actions, player_stack_sizes, hole_cards, community_cards, new_round, player_positions)


