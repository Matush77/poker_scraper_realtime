from difflib import SequenceMatcher

def assign_positions(players, button_index):
    # Define the poker positions for different numbers of players
    positions = {
        6: ['Button', 'Small Blind', 'Big Blind', 'Under the Gun', 'Middle Position', 'Cut Off'],
        5: ['Button', 'Small Blind', 'Big Blind', 'Under the Gun', 'Cut Off'],
        4: ['Button', 'Small Blind', 'Big Blind', 'Under the Gun'],
        3: ['Button', 'Small Blind', 'Big Blind'],
        2: ['Button', 'Small Blind']
    }

    # Only consider active players for position assignment
    active_players = [player for player in players if player.present_at_table]
    num_players = len(active_players)
    if num_players not in positions:
        print(f"Unexpected number of players: {num_players}")
        return

    for i, player in enumerate(active_players):
        # Calculate the position index, taking into account the button position and the clockwise order
        pos_index = (i - button_index) % num_players
        player.position = positions[num_players][pos_index]

def is_similar(a, b):
    return SequenceMatcher(None, a, b).ratio() >= 0.8
