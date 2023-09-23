import pandas as pd

player_df = pd.DataFrame(columns=['Name', 'Deck', 'Match W', 'Match L', 'Game W', 'Game L'])
matchup_df = pd.DataFrame(columns=['Deck', 'Opposing Deck', 'Match W', 'Match L', 'Game W', 'Game L'])


with open('worlds_lv.txt', 'r', encoding='ISO-8859-1') as file:
    while True:
        line = file.readline()
        if not line:
            break
        name1 = line.strip()
        deck1 = file.readline().strip()
        
        name2 = file.readline().strip()
        deck2 = file.readline().strip()
        
        result = file.readline().strip().split()
        winning_name = ' '.join(result[:-2])
        
        result = result[-1].split('-')
        if not 'Draw' in result:
            result = [int(x) for x in result]
        else:
            continue
        
        if winning_name in name1:
            player1_w = result[0]
            player1_l = result[1]
            player1_mw = 1
            player1_ml = 0
        else:
            player1_l = result[0]
            player1_w = result[1]
            player1_mw = 0
            player1_ml = 1
        
        if name1 not in player_df['Name'].values:
            player_df.loc[len(player_df)] = [name1, deck1, player1_mw, player1_ml, player1_w, player1_l]
        else:
            row = player_df[player_df['Name'] == name1]
            index = row.index[0]
            player_df.at[index, 'Match W'] += player1_mw
            player_df.at[index, 'Match L'] += player1_ml
            player_df.at[index, 'Game W'] += player1_w
            player_df.at[index, 'Game L'] += player1_l
            
        if name2 not in player_df['Name'].values:
            player_df.loc[len(player_df)] = [name2, deck2, player1_ml, player1_mw, player1_l, player1_w]
        else:
            row = player_df[player_df['Name'] == name2]
            index = row.index[0]
            player_df.at[index, 'Match W'] += player1_ml
            player_df.at[index, 'Match L'] += player1_mw
            player_df.at[index, 'Game W'] += player1_l
            player_df.at[index, 'Game L'] += player1_w
        
        if deck1 == deck2:
            continue
        
        row1 = matchup_df[(matchup_df['Deck'] == deck1) & (matchup_df['Opposing Deck'] == deck2)]
        row2 = matchup_df[(matchup_df['Deck'] == deck2) & (matchup_df['Opposing Deck'] == deck1)]
        if not row1.empty:
            index = row1.index[0]
            matchup_df.at[index, 'Match W'] += player1_mw
            matchup_df.at[index, 'Match L'] += player1_ml
            matchup_df.at[index, 'Game W'] += player1_w
            matchup_df.at[index, 'Game L'] += player1_l
            
            index = row2.index[0]
            matchup_df.at[index, 'Match W'] += player1_ml
            matchup_df.at[index, 'Match L'] += player1_mw
            matchup_df.at[index, 'Game W'] += player1_l
            matchup_df.at[index, 'Game L'] += player1_w
            
        else:
            matchup_df.loc[len(matchup_df)] = [deck1, deck2, player1_mw, player1_ml, player1_w, player1_l]
            matchup_df.loc[len(matchup_df)] = [deck2, deck1, player1_ml, player1_mw, player1_l, player1_w]
print(matchup_df[matchup_df['Deck'] == 'Selesnya Enchantments'])            
            
deck_df = matchup_df.groupby("Deck", as_index=False).agg({"Match W": "sum", "Match L": "sum"})
deck_df['winrate'] = deck_df['Match W']/(deck_df['Match W'] + deck_df['Match L']) 
deck_df.sort_values(by='winrate', ascending=False, inplace=True)            
        
player_df.sort_values(by=['Match W', 'Game W'], ascending=False, inplace=True)
deck_df['winrate'] = round(deck_df['winrate']*100, 2)     
        
for row in deck_df.itertuples(index=False):
    print(f"{row[0]}: {row[3]}% ({row[1]}-{row[2]})")