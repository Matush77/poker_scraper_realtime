def assign_to_ranges(card1, card2):
    # Assign pairs to 'Strong' category
    if card1[0] == card2[0]:
        return 'Strong'
    # Assign cards with face values 10 or above to 'Medium' category
    elif card1[0] in ['T', 'J', 'Q', 'K', 'A'] or card2[0] in ['T', 'J', 'Q', 'K', 'A']:
        return 'Medium'
    # Assign all other hands to 'Weak' category
    else:
        return 'Weak'

def create_hand_ranges():
    suits = ['S', 'H', 'D', 'C']
    values = [str(n) for n in range(2, 10)] + list('TJQKA')
    cards = [v + s for v in values for s in suits]

    hand_strengths = ['Weak', 'Medium', 'Strong', 'Semi-Strong']
    stack_sizes = ['Small Stack', 'Medium Stack', 'Deep Stack']
    pot_sizes = ['Small Pot', 'Medium Pot', 'Large Pot', 'Massive Pot']
    actions = ['Fold', 'Call', 'Raise']
    tightness = ['Tight', 'Loose']
    positions = ['Under the Gun', 'Middle Position', 'Cut Off', 'Button', 'Small Blind', 'Big Blind']

    # Initially, no hands are assigned to any category
    hand_ranges = {}
    for position in positions:
        hand_ranges[position] = {}
        for stack_size in stack_sizes:
            hand_ranges[position][stack_size] = {}
            for pot_size in pot_sizes:
                hand_ranges[position][stack_size][pot_size] = {}
                for action in actions:
                    hand_ranges[position][stack_size][pot_size][action] = {}
                    for tightness_level in tightness:
                        hand_ranges[position][stack_size][pot_size][action][tightness_level] = {}
                        for hand_strength in hand_strengths:
                            hand_ranges[position][stack_size][pot_size][action][tightness_level][hand_strength] = []

    # Assign hands to categories based on a simplified model
    for position in positions:
        for stack_size in stack_sizes:
            for pot_size in pot_sizes:
                for action in actions:
                    for tightness_level in tightness:
                        for hand_strength in hand_strengths:
                            for i in range(len(cards)):
                                for j in range(i+1, len(cards)):
                                    if assign_to_ranges(cards[i], cards[j]) == hand_strength:
                                        hand_ranges[position][stack_size][pot_size][action][tightness_level][hand_strength].append((cards[i], cards[j]))
    return hand_ranges

hand_ranges = create_hand_ranges()

# Print the hand ranges
for position, stacks in hand_ranges.items():
    for stack_size, pots in stacks.items():
        for pot_size, actions in pots.items():
            for action, tightness_levels in actions.items():
                for tightness_level, strengths in tightness_levels.items():
                    for hand_strength, hands in strengths.items():
                        print(f"Position: {position}, Stack Size: {stack_size}, Pot Size: {pot_size}, Action: {action}, Play Style: {tightness_level}, Hand Strength: {hand_strength}, Hands: {hands}")
