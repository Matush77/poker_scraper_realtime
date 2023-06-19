from treys import Deck, Evaluator, Card
from collections import Counter


#HAND EQUITY CALCULATIONS
def calculate_hand_equity_treys(hole_cards, community_cards, active_players, nb_simulation=2000):
    # Convert cards to Treys format
    my_cards = [Card.new(card) for card in hole_cards]
    table_cards = [Card.new(card) for card in community_cards]
    
    evaluator = Evaluator()
    
    win = 0
    tie = 0
    for _ in range(nb_simulation):
        deck = Deck()  # Create a new deck for each simulation

        # Remove my cards and table cards from the deck
        for card in my_cards + table_cards:
            deck.cards.remove(card)

        # Generate opponent hole cards for each active player
        opponent_cards = [deck.draw(2) for _ in range(active_players - 1)]

        # Generate remaining community cards
        new_community_cards = []
        if len(table_cards) < 5:
            community_to_draw = 5 - len(table_cards)
            new_community_cards = deck.draw(community_to_draw)

        my_rank = evaluator.evaluate(table_cards + new_community_cards, my_cards)
        opp_ranks = [evaluator.evaluate(table_cards + new_community_cards, hand) for hand in opponent_cards]
        
        # Compare ranks
        if my_rank < min(opp_ranks):  # In Treys, lower rank number is better
            win += 1
        elif my_rank == min(opp_ranks):  # Consider ties
            tie += 1

    equity = (win + 0.5 * tie) / nb_simulation  # Half equity when tied
    return equity



if __name__ == "__main__":

    active_players = 2
    hole_cards_input = ["Kc", "Ac"]  # Aces of Spades and Hearts
    community_cards_input = ['Jc', '3c', 'Qc', 'Tc']  # Flop example
    hand_equity = calculate_hand_equity_treys(hole_cards_input, community_cards_input, active_players)

    print("Hand Equity:", hand_equity)

 

