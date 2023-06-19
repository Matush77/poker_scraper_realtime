def convert_money_string_to_float(money_str):
    if money_str and isinstance(money_str, str):
        # remove any commas and dollar signs before converting to float
        return float(money_str.replace("$", "").replace(",", "").replace("", ""))
    else:
        return 0.0


class Table:
    def __init__(self, pot_size, community_cards, players, button_position):
        self.pot_size = convert_money_string_to_float(pot_size.replace("Pot: ", "").replace("ott", "").replace("pott", "").replace("ot", "").replace(": ", "").replace("t", "").replace("S", ""))  # remove "Pot: " and convert to float
        self.community_cards = community_cards
        self.players = players
        self.button_position = button_position
        self.my_cards = None
        for player in players:
            if player.name == "Matush777777":
                self.my_cards = player.hole_cards
        self.assign_positions()

    def is_new_hand(self, new_button_position):
        if new_button_position != self.button_position:
            self.button_position = new_button_position
            self.assign_positions()
            return True
        return False

    def assign_positions(self):
        positions = {
            6: ['Button', 'Small Blind', 'Big Blind', 'Under the Gun', 'Middle Position', 'Cut Off'],
            5: ['Button', 'Small Blind', 'Big Blind', 'Under the Gun', 'Cut Off'],
            4: ['Button', 'Small Blind', 'Big Blind', 'Under the Gun'],
            3: ['Button', 'Small Blind', 'Big Blind'],
            2: ['Button', 'Small Blind']
        }
        active_players = [player for player in self.players if player.present_at_table]
        num_players = len(active_players)
        if num_players not in positions:
            print(f"Unexpected number of players: {num_players}")
            return

        active_button_position = active_players.index(self.players[self.button_position])
        for i, player in enumerate(active_players):
            pos_index = (i - active_button_position) % num_players
            player.position = positions[num_players][pos_index]

    def update_player_activity(self, player_index, activity_status):
        self.players[player_index].active = activity_status

   

    def get_all_preflop_histories_and_raise_count(self):
        preflop_histories = {}
        preflop_raise_count = 0

        for player in self.players:
            preflop_histories[player.name] = player.hand_history["Pre-flop"]
            
            for action in player.hand_history["Pre-flop"]:
                if 'raise' in action.lower():  # assuming 'raise' is the keyword for a raise action
                    preflop_raise_count += 1
                    
        return preflop_histories, preflop_raise_count


    def stage_of_hand(self):
        num_community_cards = len(self.community_cards)
        if num_community_cards == 0 or num_community_cards == 1 or num_community_cards == 2:
            return "Pre-flop"
        elif num_community_cards == 3:
            return "Flop"
        elif num_community_cards == 4:
            return "Turn"
        elif num_community_cards == 5:
            return "River"
        else:
            return "Invalid stage"

    def __str__(self):
        community_cards_str = ', '.join(str(card) for card in self.community_cards)
        players_str = '\n'.join(str(player) for player in self.players)
        my_cards_str = ', '.join(str(card) for card in self.my_cards) if self.my_cards else 'None'
        stage_of_hand = self.stage_of_hand()
        return f'Pot size: {self.pot_size}, Stage: {stage_of_hand}, Button Position: {self.button_position}, Community Cards: {community_cards_str}, Players: \n{players_str}'