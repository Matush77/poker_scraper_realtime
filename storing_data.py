import pandas as pd
from config import *

def store_data(players):
    data = {
        'Name': [player.name for player in players],
        'Hands Played': [player.hands_played for player in players],
        'Stack Size': [player.stack_size for player in players],
        'Position': [player.position for player in players],
        'Action': [player.action for player in players],
        'Hole Cards': [','.join(player.hole_cards) for player in players],
        'VPIP Counter': [player.vpip_counter for player in players],
        'PFR Counter': [player.pfr_counter for player in players],
        'Hands Played': [player.hands_played for player in players],
        'Bet Counter': [player.bet_counter for player in players],
        'Raise Counter': [player.raise_counter for player in players],
        'Call Counter': [player.call_counter for player in players],
        'CBET Counter': [player.cbet_counter for player in players],
        'Showdown Count': [player.showdown_count for player in players],
        'WMSD Count': [player.wmsd_count for player in players],
        'Seen Flop Counter': [player.seen_flop_counter for player in players],
        'Flop Fold Counter': [player.flop_fold_counter for player in players],
        'Turn Fold Counter': [player.turn_fold_counter for player in players],
        'River Fold Counter': [player.river_fold_counter for player in players],
    }


    df = pd.DataFrame(data)
    df.to_csv(PLAYER_DATA_PATH, index=False)