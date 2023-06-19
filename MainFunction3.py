import pandas as pd
from tabulate import tabulate
import keyboard
import time
from datetime import datetime
import pyautogui
from player_class4 import Player
from table_class import Table
from showdown_detector import find_showdown_on_table
from table_logic import assign_positions, is_similar
from button_detector import find_button_in_screenshot
from empty_seat_detector import check_empty_seats
from action_detector import find_player_actions     
from card_detector2 import find_cards_on_table
from storing_data import store_data
from hand_equity import calculate_hand_equity_treys
from player_stats_detector import get_player_stats, find_stacks_on_table, get_pot_size
from config import *


if __name__ == "__main__":

    current_button_index = None
    initial_screenshot = pyautogui.screenshot(region=(67, 72, 950, 550))
    names, _, _ = get_player_stats(initial_screenshot, STACK_TEMPLATES_DIR, POT_TEMPLAES_DIR)
    players = [Player(name, 0) for name in names]
    previous_stage = None
    stage_change_time = time.time()
    last_name_check = time.time()

    while True:

        # Take screenshot every 0.20 second
        screenshot = pyautogui.screenshot(region=(67, 72, 950, 550))
        time.sleep(0.20)

        if keyboard.is_pressed('space'):
            print("Exiting script...")
            break

        current_time = time.time()

        # Check name regions only once per 5 seconds
        if current_time - last_name_check >= 5:
            names, _, _ = get_player_stats(screenshot, POT_TEMPLAES_DIR, STACK_TEMPLATES_DIR, check_names=True)
            last_name_check = current_time
        else:
            names = [player.name for player in players]  # we don't need to call the OCR function for names      

        # use the template matching method for stack sizes
        stacks = find_stacks_on_table(screenshot, STACK_TEMPLATES_DIR)
        
        # update the pot size
        pot = get_pot_size(screenshot, POT_TEMPLAES_DIR)

        # Check for empty seats and update player activity status
        empty_seats = check_empty_seats(screenshot, EMPTY_SEAT_TEMPLATES_DIR)

        for i, (player, name, stack) in enumerate(zip(players, names, stacks)):
            player.update_name(name)
            player.update_stack_size(stack)
            player.check_activity(empty_seats, i)
            if player.leaving:
                player.leave_table()



        button_index = find_button_in_screenshot(screenshot, DEALER_BUTTON_DIR)
        if button_index is not None and button_index != current_button_index:
            print("New hand started.")
            current_button_index = button_index
            for player in players:
                player.new_hand()
                player.reset_hand_history()

        assign_positions(players, current_button_index)

        showdowns = find_showdown_on_table(screenshot, SHOWDOWN_TEMPLATES_DIR)
        for i in showdowns.keys():
            if not players[i].showdown_detected:
                players[i].showdown_count += 1
                players[i].showdown_detected = True

        found_actions = find_player_actions(screenshot, ACTION_TEMPLATES_DIR)
        for i, action in found_actions.items():
            players[i].action = action
            if action == 'Fold':
                players[i].is_active = False  # Set the player as inactive if they have folded
            elif action == 'Won' and players[i].showdown_detected and not players[i].wmsd_incremented:
                players[i].detect_wmsd(action)




        hole_cards, community_cards = find_cards_on_table(screenshot, CARDS_TEMPLATES_DIR)
        table = Table(pot, community_cards, players, current_button_index)
        current_stage = table.stage_of_hand()  # determine the stage


        if current_stage != previous_stage:  # stage transition
            if previous_stage == "Pre-flop":
                table.get_all_preflop_histories_and_raise_count()
            previous_stage = current_stage
            time.sleep(0.35) # Add a delay of 0.35 seconds before changing stages

        for i, action in found_actions.items():
            timestamp = datetime.now().time()
            players[i].update_action(action, current_stage)
            if players[i].cooldown_passed():
                players[i].add_action(current_stage,action)  # add timestamp and action to hand history

        for player in players:
            if is_similar(player.name, "Matush777777"):
                player.hole_cards = hole_cards
                
        active_players = sum(player.is_active for player in players)
        for player in players:
            player.calculate_hand_equity(community_cards, active_players)
        

        data = {
            'Name': [player.name for player in players],
            'Active' :[player.is_active for player in players],
            'Present' :[player.present_at_table for player in players],
            #'Stack Size': [player.stack_size for player in players],
            'Position': [player.position for player in players],
            #'Action': [player.action for player in players],
            'AF': [round((player.get_aggression_factor()), 2) for player in players],
            'CBET %': [round((player.cbet_counter / player.hands_played * 100), 2) if player.hands_played > 0 else 0 for player in players], 
            'VPIP %': [round((player.vpip_counter / player.hands_played * 100), 2) if player.hands_played > 0 else 0 for player in players],
            'PFR %': [round((player.pfr_counter / player.hands_played * 100), 2) if player.hands_played > 0 else 0 for player in players],
            'Hand Equity' : [player.hand_equity for player in players],
            'Hole Cards': [', '.join(player.hole_cards) if player.hole_cards else 'None' for player in players],
            #'Hand History': [', '.join(f'{k}: {v}' for k, v in player.hand_history.items()) for player in players],
            'Community Cards': ', '.join(str(card) for card in table.community_cards),
            #'WTSD %': [round((player.showdown_count / player.hands_played * 100), 2) if player.hands_played > 0 else 0 for player in players],
            #'W$SD %': [round((player.wmsd_count / player.showdown_count * 100), 2) if player.showdown_count > 0 else 0 for player in players],
            #'Seen flop %': [round((player.seen_flop_counter / player.hands_played * 100), 2) if player.hands_played > 0 else 0 for player in players],
            #'Pot Size': table.pot_size,
            #'Flop Fold %': [round((player.flop_fold_counter / player.hands_played * 100), 2) if player.hands_played > 0 else 0 for player in players],
            #'Turn Fold %': [round((player.turn_fold_counter / player.hands_played * 100), 2) if player.hands_played > 0 else 0 for player in players],
            #'River Fold %': [round((player.river_fold_counter / player.hands_played * 100), 2) if player.hands_played > 0 else 0 for player in players],
        }


        df = pd.DataFrame(data)

        store_data(players)  

        print(tabulate(df, headers='keys', tablefmt='psql'))

        


    

