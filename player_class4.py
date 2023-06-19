import re
import time
from hand_equity import calculate_hand_equity_treys

def convert_money_string_to_float(money_str):
    try:
        if isinstance(money_str, int):
            return float(money_str)
        elif money_str == "AllIn":
            return 0.0
        else:
            return float(money_str)
    except ValueError:
        print(f'Error: unable to convert "{money_str}" to float.')
        return 0.0  # return a default value



class Player:
    def __init__(self, name, stack_size, position=None, action=None, hole_cards=None):
        self.name = name
        self.stack_size = convert_money_string_to_float(stack_size)
        self.previous_stack_size = self.stack_size
        self.position = position
        self.action = action
        self.hole_cards = hole_cards if hole_cards else []
        self.hand_history = {"Pre-flop": [], "Flop": [], "Turn": [], "River": []}
        self.vpip_counter = 0  # Initialize VPIP counter
        self.pfr_counter = 0  # Initialize PFR counter
        self.vpip_incremented = False  # Initialize VPIP increment flag
        self.pfr_incremented = False  # Initialize PFR increment flag
        self.hands_played = 0  # Initialize hands played counter
        self.last_action_time = 0
        self.bet_counter = 0  # Initialize Bet counter
        self.raise_counter = 0  # Initialize Raise counter
        self.call_counter = 0  # Initialize Call counter
        self.preflop_raise = False  # Initialize Pre-flop raise flag
        self.cbet_counter = 0  # Initialize C-Bet counter
        self.showdown_count = 0
        self.showdown_detected = False
        self.wmsd_count = 0
        self.wmsd_incremented = False
        self.seen_flop_counter = 0  # Initialize Seen flop counter
        self.seen_flop = False  # Initialize Seen flop flag
        self.flop_fold_counter = 0  # Initialize Flop fold counter
        self.turn_fold_counter = 0  # Initialize Turn fold counter
        self.river_fold_counter = 0  # Initialize River fold counter
        self.present_at_table = True
        self.leaving = False
        self.hand_equity = None
        self.is_active = True

    def fold(self):
        self.action = 'Fold'
        self.is_active = False

    def leave_table(self):
        self.present_at_table = False
        self.is_active = False

    def return_to_table(self):
        self.present_at_table = True
        self.is_active = True
    
    def calculate_hand_equity(self, community_cards, active_players):
        # Assuming calculate_hand_equity_treys is a function that computes hand equity
        self.hand_equity = calculate_hand_equity_treys(self.hole_cards, community_cards, active_players)

    def calculate_pot_odds(self, pot, action):
            if action.startswith(("Call", "Bet", "Raise")):  # Check if action involves betting
                action_parts = action.split()
                if len(action_parts) > 1:  # Check if action contains bet size
                    amount = float(action_parts[1])  # Extract bet size from action string
                else:
                    return None  # Return None if bet size is not specified in action
            else:
                return None  # Return None if action does not involve betting

            required_bet = amount
            total_pot = pot + amount

            return total_pot / required_bet



        
    def check_activity(self, empty_seats, player_index):
        if player_index in empty_seats and self.present_at_table:
            self.leaving = True
            self.is_active = False
        elif not self.present_at_table and player_index not in empty_seats:
            self.leaving = False
            self.present_at_table = True
            self.is_active = True


    def cooldown_passed(self, cooldown=2.2):
        return time.time() - self.last_action_time >= cooldown
        

    def update_action(self, action, stage):
        if not self.cooldown_passed():
            return
        self.action = action
        if stage == "Pre-flop":
            if action in ['Bet', 'Raise', 'Call']:
                self.vpip_counter += 1
                self.vpip_incremented = True
            if action == 'Raise':
                self.pfr_counter += 1
                self.pfr_incremented = True
                self.preflop_raise = True  # Player made a pre-flop raise
            if action == 'Bet':
                self.bet_counter += 1
            elif action == 'Raise':
                self.raise_counter += 1
            elif action == 'Call':
                self.call_counter += 1
        elif stage == "Flop":
            if self.preflop_raise and action in ['Bet', 'Raise']:
                self.cbet_counter += 1  # Player made a C-bet
            self.preflop_raise = False  # Reset the pre-flop raise flag
        if stage in ["Flop", "Turn", "River"] and action in ['Fold', 'Raise', 'Call', 'Bet', 'Check'] and not self.seen_flop:
            self.seen_flop_counter += 1
            self.seen_flop = True
        if action == 'Fold':
            if stage == 'Flop':
                self.flop_fold_counter += 1
            elif stage == 'Turn':
                self.turn_fold_counter += 1
            elif stage == 'River':
                self.river_fold_counter += 1


    def new_hand(self):
        self.hands_played += 1
        self.vpip_incremented = False  # Reset VPIP increment flag
        self.pfr_incremented = False  # Reset PFR increment flag
        self.preflop_raise = False  # Reset pre-flop raise flag
        self.showdown_detected = False
        if self.present_at_table:
            self.is_active = True
        self.wmsd_incremented = False
        self.seen_flop = False  # Reset Seen flop flag
        if self.leaving:
            self.present_at_table = False
            self.leaving = False
        self.reset_hand_history()

    def add_action(self, stage, action):
        # Only process the action if the cooldown has passed
        if not self.cooldown_passed():
            return

        # Check if action is Bet, Raise or Call and calculate the amount
        if action in ["Call", "Bet", "Raise"]:
            amount = round(self.previous_stack_size - self.stack_size, 2)
            action += f' {amount}'

        if stage not in self.hand_history:
            self.hand_history[stage] = []  # Initialize list for new stages

        # Update the last action time
        self.last_action_time = time.time()

        # Append tuple of (timestamp, action) to the list
        self.hand_history[stage].append(action)

        if action == 'Bet':
            self.bet_counter += 1
        elif action == 'Raise':
            self.raise_counter += 1
        elif action == 'Call':
            self.call_counter += 1

    def get_aggression_factor(self):
        if self.call_counter == 0:  # prevent division by zero
            return float('inf')
        else:
            return (self.bet_counter + self.raise_counter) / self.call_counter
        
    def detect_showdown(self):
        if not self.showdown_detected:
            self.showdown_count += 1
            self.showdown_detected = True

    def detect_wmsd(self, action):
        if self.showdown_detected and action == 'Won':
            self.wmsd_count += 1
            self.wmsd_incremented = True


    def update_stack_size(self, stack_size):
        if stack_size.strip() != '':  # Check if the stack size string is not empty
            self.previous_stack_size = self.stack_size
            self.stack_size = convert_money_string_to_float(stack_size)


    def update_name(self, name):
        action_words = ["Post SB", "Post BB", "Resume", "Cash Out", "Muck", "Fold", "Call", "Check", "Raise", "Bet", "Sit out", "sitOut"]
        won_pattern = r"Won \$\d+(\.\d+)?"
        time_pattern = r"Time [1-5]?[0-9] sec"

        if name not in action_words and not re.match(won_pattern, name) and not re.match(time_pattern, name):
            self.name = name

    def reset_hand_history(self):
        self.hand_history = {"Pre-flop": [], "Flop": [], "Turn": [], "River": []}

    def __str__(self):
        hole_cards_str = ', '.join(str(card) for card in self.hole_cards)
        hand_history_str = ', '.join(f'{stage}: {actions}' for stage, actions in self.hand_history.items())
        return f'Name: {self.name}, Stack size: {self.stack_size}, Position: {self.position}, Action: {self.action}, Hole Cards: {hole_cards_str}, Hand History: {hand_history_str}'