from button_detector import find_button_in_screenshot
from difflib import SequenceMatcher
import re


current_player_pfr = {}
pfr_updated_in_current_round = {}
vpip_updated_in_current_round = {}
current_player_vpip = {}
current_player_cbet = {}
current_player_af = {}

def is_me(player_name):
    return player_name == "Matush777777"


def print_game_stage(community_cards):
    num_community_cards = len(community_cards)
    if num_community_cards == 0:
        stage = "Pre-flop"
    elif num_community_cards == 3:
        stage = "Flop"
    elif num_community_cards == 4:
        stage = "Turn"
    elif num_community_cards == 5:
        stage = "River"
    else:
        stage = "Unknown"
    print(f"Game stage: {stage}")
    return stage

current_player_actions = []

# def convert_stack_size_to_float(stack_size_str):
#     if not stack_size_str or stack_size_str.strip() == '':
#         return 0.0
#     if stack_size_str == "All In":
#         return 0
#     stack_size_str = stack_size_str.replace('$', '').replace(',', '')
#     if stack_size_str[-1] == '.':
#         stack_size_str = stack_size_str[:-1]
#     return round(float(stack_size_str), 2)


def convert_stack_size_to_float(stack_size):
    if isinstance(stack_size, int):
        return float(stack_size)
    else:
        stack_size_str = stack_size.replace("$", "").replace(",", "")
        if not stack_size_str or stack_size_str.strip() == '':
            return 0.0
        else:
            return float(stack_size_str)




previous_player_stack_sizes = []

def process_and_reset_actions(player_names, player_actions, new_round, community_cards):
    global current_player_actions

    updated_pfr = update_pfr(player_names, player_actions, new_round, community_cards)
    updated_vpip = update_vpip(player_names, player_actions, new_round, community_cards)
    updated_cbet = update_cbet(player_names, player_actions, new_round, community_cards)

    for i, action in enumerate(player_actions):
        if action.startswith(('Call', 'Raise', 'Bet')):
            current_player_actions[i] = ""

    return updated_pfr, updated_vpip, updated_cbet

def track_player_actions(player_names, player_actions, player_stack_sizes, new_round, community_cards):
    global current_player_actions
    global previous_player_stack_sizes
    call_cost = 0
    amount = 0

    if new_round or len(current_player_actions) != len(player_names):
        current_player_actions = [""] * len(player_names)

    if new_round or len(previous_player_stack_sizes) != len(player_stack_sizes):
        previous_player_stack_sizes = [0] * len(player_stack_sizes)
        for i, stack_size in enumerate(player_stack_sizes):
            if stack_size:
                previous_player_stack_sizes[i] = convert_stack_size_to_float(stack_size)

    for i, name in enumerate(player_names):
        action = current_player_actions[i]
        for keyword, action_value in player_actions.items():
            if keyword in name:
                action = action_value
                break

        if action == 'Fold' or action == 'sitOut' or action == 'sitout' or current_player_actions[i] != 'Fold':
            if action in ['Bet', 'Raise', 'Call']:
                current_stack_size = convert_stack_size_to_float(player_stack_sizes[i])
                amount = previous_player_stack_sizes[i] - current_stack_size
                if amount < 0:  # Make sure the amount is positive
                    amount = abs(amount)
                action = f"{action} ({amount:.2f})"
                player_stack_sizes[i] = f"${current_stack_size:.2f}"
            current_player_actions[i] = action
            if not is_me(name):
                call_cost = amount

        # Update the previous stack size after processing the action
        previous_player_stack_sizes[i] = convert_stack_size_to_float(player_stack_sizes[i])

    return current_player_actions, call_cost


def calculate_pot_odds(pot_size, call_cost):
    if call_cost == 0: 
        return float('inf')  # infinite odds if the call is free
    else:
        return pot_size / call_cost



def track_player_action_history(player_names, player_actions, player_stack_sizes, new_round, community_cards):
    global player_action_history

    # Initialize player_action_history if it does not exist or if it's a new round
    if new_round or 'player_action_history' not in globals():
        player_action_history = {name: [] for name in player_names}
        
    # Use the track_player_actions function to get current actions for all players
    current_actions = track_player_actions(player_names, player_actions, player_stack_sizes, new_round, community_cards)

    # Record each player's action in their history
    for name, action in zip(player_names, current_actions):
        player_action_history[name].append(action)

    return player_action_history






def update_pfr(player_names, player_actions, new_round, community_cards):
    global current_player_pfr
    global pfr_updated_in_current_round

    for name in player_names:
        if is_action_or_status(name):
            continue

        if name not in current_player_pfr:
            current_player_pfr[name] = 0  # Initialize with zeros
        if name not in pfr_updated_in_current_round:
            pfr_updated_in_current_round[name] = False  # Initialize with False

    for i, (name, action) in enumerate(zip(player_names, player_actions)):
        if is_action_or_status(name):
            continue

        if action.startswith("Raise") and print_game_stage(community_cards) == "Pre-flop" and not pfr_updated_in_current_round[name]:
            current_player_pfr[name] += 1  # Increment the count of "Y" occurrences
            pfr_updated_in_current_round[name] = True  # Mark the count as updated for the current round

    # Reset pfr_updated_in_current_round flags if it's a new round
    if new_round:
        for name in player_names:
            pfr_updated_in_current_round[name] = False

    return current_player_pfr

def update_vpip(player_names, player_actions, new_round, community_cards):
    global current_player_vpip
    global vpip_updated_in_current_round

    for name in player_names:
        if is_action_or_status(name):
            continue

        if name not in current_player_vpip:
            current_player_vpip[name] = 0  # Initialize with zeros
        if name not in vpip_updated_in_current_round:
            vpip_updated_in_current_round[name] = False  # Initialize with False

    for i, (name, action) in enumerate(zip(player_names, player_actions)):
        if is_action_or_status(name):
            continue

        if action.startswith(("Raise", "Bet", "Call")) and print_game_stage(community_cards) == "Pre-flop" and not vpip_updated_in_current_round[name]:
            current_player_vpip[name] += 1  # Increment the count of "Y" occurrences
            vpip_updated_in_current_round[name] = True  # Mark the count as updated for the current round

    # Reset vpip_updated_in_current_round flags if it's a new round
    if new_round:
        for name in player_names:
            vpip_updated_in_current_round[name] = False

    return current_player_vpip


current_player_cbet = {}
cbet_updated_in_current_round = {}
last_aggressor = None

def update_cbet(player_names, player_actions, new_round, community_cards):
    global current_player_cbet
    global cbet_updated_in_current_round
    global last_aggressor

    for name in player_names:
        if is_action_or_status(name):
            continue

        if name not in current_player_cbet:
            current_player_cbet[name] = 0  # Initialize with zeros
        if name not in cbet_updated_in_current_round:
            cbet_updated_in_current_round[name] = False  # Initialize with False

    game_stage = print_game_stage(community_cards)

    if game_stage == "Pre-flop":
        for i, (name, action) in enumerate(zip(player_names, player_actions)):
            if is_action_or_status(name):
                continue

            if action.startswith("Raise"):
                last_aggressor = name

    elif game_stage == "Flop" or  game_stage == "Turn":
        for i, (name, action) in enumerate(zip(player_names, player_actions)):
            if is_action_or_status(name):
                continue

            if action.startswith(("Bet", "Raise")) and name == last_aggressor and not cbet_updated_in_current_round[name] and not action.startswith("Raise"):
                current_player_cbet[name] += 1  # Increment the count of C-bet occurrences
                cbet_updated_in_current_round[name] = True  # Mark the count as updated for the current round

    # Reset cbet_updated_in_current_round flags if it's a new round
    if new_round:
        for name in player_names:
            cbet_updated_in_current_round[name] = False

    return current_player_cbet


current_player_aggressive_actions = {}
current_player_passive_actions = {}

previous_actions = {}

def update_af(player_names, player_actions, new_round, community_cards):
    global current_player_aggressive_actions
    global current_player_passive_actions
    global previous_actions

    game_stage = print_game_stage(community_cards)
    if game_stage == "Pre-flop":
        # Return the current AF values without updating counts
        player_af = {}
        for name in player_names:
            if is_action_or_status(name):
                continue

            aggressive_actions = current_player_aggressive_actions.get(name, 0)
            passive_actions = current_player_passive_actions.get(name, 0)

            if passive_actions == 0:
                af = aggressive_actions
            else:
                af = aggressive_actions / passive_actions

            player_af[name] = af

        return player_af

    for name in player_names:
        if is_action_or_status(name):
            continue

        if name not in current_player_aggressive_actions:
            current_player_aggressive_actions[name] = 0
        if name not in current_player_passive_actions:
            current_player_passive_actions[name] = 0
        if name not in previous_actions:
            previous_actions[name] = None

    for i, (name, action) in enumerate(zip(player_names, player_actions)):
        if is_action_or_status(name):
            continue

        if action == previous_actions[name]:
            continue

        if action.startswith(("Bet", "Raise")):
            current_player_aggressive_actions[name] += 1
        elif action.startswith("Call"):
            current_player_passive_actions[name] += 1

        previous_actions[name] = action

    # Calculate AF for each player
    player_af = {}
    for name in player_names:
        if is_action_or_status(name):
            continue

        aggressive_actions = current_player_aggressive_actions[name]
        passive_actions = current_player_passive_actions[name]

        if passive_actions == 0:
            af = aggressive_actions
        else:
            af = aggressive_actions / passive_actions

        player_af[name] = af

    return player_af





def active_player(player_actions, player_names):
    active_status = []
    for idx, action in enumerate(player_actions):
        if is_me(player_names[idx]) or action == 'Fold' or action == 'sitOut' or action == 'sitout':
            active_status.append('N/A')
        else:
            active_status.append('Y')
    return active_status


current_positions = []
previous_button_player = None

def similar(a, b):
    if a is None or b is None:
        return 0
    return SequenceMatcher(None, a, b).ratio()


def is_action_or_status(name):
    actions_and_statuses = ["Post SB", "Post BB", "Resume", "Cash Out", "Muck", "Fold", "Call", "Check", "Raise", "Bet", "Sit out"]
    for action_or_status in actions_and_statuses:
        if action_or_status in name:
            return True
    
    won_pattern = r"Won \$\d+(\.\d+)?"
    time_pattern = r"Time [1-5]?[0-9] seconds"
    
    if re.search(won_pattern, name) or re.search(time_pattern, name):
        return True

    return False

def is_new_round(player_names, button_index, previous_button_player):
    button_player = player_names[button_index]
    name_similarity = similar(previous_button_player, button_player)
    name_changed_to_action = is_action_or_status(button_player)

    if previous_button_player != button_player and name_similarity < 0.7 and not name_changed_to_action:
        return True, button_player
    else:
        return False, previous_button_player

active_statuses = {}
current_player_pfr = {}

def determine_positions(player_names, player_stack_sizes, empty_seats, player_actions, screenshot_path, button_sample_folder, community_cards, current_player_pfr, current_player_vpip, current_player_cbet, current_player_af):
    global current_positions
    global previous_button_player

    # Remove empty seats from player_names and player_stack_sizes
    for empty_seat in sorted(empty_seats, reverse=True):
        player_names.pop(empty_seat)
        player_stack_sizes.pop(empty_seat)

    button_index = find_button_in_screenshot(screenshot_path, button_sample_folder)

    # If the number of players has changed, reset current_positions
    if len(player_names) != len(current_positions):
        current_positions = ['Unknown'] * len(player_names)

    new_round = False
    if button_index is not None:
        # Adjust button index according to the empty seats
        adjusted_button_index = sum([1 for i in empty_seats if i < button_index])
        button_index -= adjusted_button_index

        # Check if it's a new round
        new_round, previous_button_player = is_new_round(player_names, button_index, previous_button_player)

        position_names_dict = {
            6: ['Button', 'Small Blind', 'Big Blind', 'Under the Gun', 'Middle Position', 'Cut Off'],
            5: ['Button', 'Small Blind', 'Big Blind', 'Under the Gun', 'Cut Off'],
            4: ['Button', 'Small Blind', 'Big Blind', 'Under the Gun'],
            3: ['Button', 'Small Blind', 'Big Blind'],
            2: ['Button', 'Small Blind']
        }

        position_names = position_names_dict.get(len(player_names), ['Unknown'] * len(player_names))

        # Check if current_positions is empty or a new button player is detected
        if not current_positions or current_positions[button_index] != 'Button':
            current_positions = []
            for i in range(len(player_names)):
                position = position_names[(i - button_index) % len(position_names)]
                current_positions.append(position)
    else:
        # If no button player is found, use the previous positions or fill with 'Unknown'
        if not current_positions:
            current_positions = ['Unknown'] * len(player_names)

    player_actions_list = track_player_actions(player_names, player_actions, player_stack_sizes, new_round, community_cards)
    current_player_pfr = update_pfr(player_names, player_actions_list, new_round, community_cards)
    current_player_vpip = update_vpip(player_names, player_actions_list, new_round, community_cards)
    current_player_cbet = update_cbet(player_names, player_actions_list, new_round, community_cards)
    current_player_af = update_af(player_names, player_actions_list, new_round, community_cards)


    return player_names, player_stack_sizes, current_positions, player_actions_list, new_round, current_player_pfr, current_player_vpip, current_player_cbet, current_player_af
