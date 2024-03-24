# poker_scraper_realtime
a script to scrape, collect and process data in realtime from PokerStart table. Testing purposes only.


MainFunction 3 is used to start the script and collects following data from the table:
- name of every player using OCR Tesseract
- stack sizes
- pot size
- detects every card on the table
- detects new round
- detect position of each player
- detects every action taken by every player
- detects stage of hand [Pre-flop, flop, turn and river]
- calculates hand equity for the "hero" player based on number of players at the table and given hole cards and community cards if available
- calculates varuious statistics such as PFR, VPIP, aggression rate, bet sizes if player makes a bet or raise.
