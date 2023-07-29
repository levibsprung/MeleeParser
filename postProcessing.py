import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class postProcessor:
    def __init__(self, dataLoc):
        with open(dataLoc, encoding="utf-8") as f:
            data = f.read().splitlines()
        self.data = data
        self.mainDecks = []
        self.matchupDicts = {}

    def identifyMetagame(self):
        players = {}
        for i in range(0, len(self.data), 5):
            player1, deck1, player2, deck2, result = self.data[i:i + 5]
            player1, deck1, player2, deck2, result = player1.strip(), deck1.strip(), player2.strip(), deck2.strip(), result.strip()
            if deck1 not in players:
                players[deck1] = set()
            players[deck1].add(player1)

            if deck2 not in players:
                players[deck2] = set()
            players[deck2].add(player2)
        total = sum([len(players[deck]) for deck in players])
        threshold = total * 0.03
        for deck in players:
            if len(players[deck]) >= threshold:
                self.mainDecks.append(deck)

    def generateMatrix(self):
        for i in range(0, len(self.data), 5):
            player1, deck1, player2, deck2, result = self.data[i:i + 5]
            player1, deck1, player2, deck2, result = player1.strip(), deck1.strip(), player2.strip(), deck2.strip(), result.strip()
            if deck1 == deck2 or "Draw" in result:
                continue

            if deck1 not in self.mainDecks:
                deck1 = "Other"
            if deck2 not in self.mainDecks:
                deck2 = "Other"

            winner = result.split(" won")[0].strip()
            winning_deck = deck1 if winner == player1 else deck2
            losing_deck = deck1 if winner == player2 else deck2

            if winning_deck not in self.matchupDicts.keys():
                self.matchupDicts[winning_deck] = {}
            if losing_deck not in self.matchupDicts[winning_deck].keys():
                self.matchupDicts[winning_deck][losing_deck] = [0, 0]
            self.matchupDicts[winning_deck][losing_deck][0] += 1

            if losing_deck not in self.matchupDicts.keys():
                self.matchupDicts[losing_deck] = {}
            if winning_deck not in self.matchupDicts[losing_deck].keys():
                self.matchupDicts[losing_deck][winning_deck] = [0, 0]
            self.matchupDicts[losing_deck][winning_deck][1] += 1

        for deck in self.matchupDicts.keys():
            for matchup in self.matchupDicts[deck].keys():
                wins, losses = self.matchupDicts[deck][matchup]
                self.matchupDicts[deck][matchup] = [wins / (wins + losses), wins + losses]

    def generateChart(self):
        flat_data = {"Deck": [], "Opponent": [], "Win Rate (%)": [], "Sample Size": []}
        for deck, opponents in self.matchupDicts.items():
            for opponent, data in opponents.items():
                flat_data["Deck"].append(deck)
                flat_data["Opponent"].append(opponent)
                flat_data["Win Rate (%)"].append(round((1 - data[0]) * 100, 1))
                flat_data["Sample Size"].append(data[1])

        df = pd.DataFrame(flat_data)

        win_rate_pivot = df.pivot(index="Deck", columns="Opponent", values="Win Rate (%)")
        sample_size_pivot = df.pivot(index="Deck", columns="Opponent", values="Sample Size")
        win_rate_pivot = win_rate_pivot.transpose()
        sample_size_pivot = sample_size_pivot.transpose()
        cols = list(win_rate_pivot.columns)
        cols.insert(len(cols), cols.pop(cols.index("Other")))
        win_rate_pivot = win_rate_pivot[cols]
        sample_size_pivot = sample_size_pivot[cols]
        annotations = win_rate_pivot.astype(str) + "\n\n(n=" + sample_size_pivot.astype(str) + ")"

        plt.figure(figsize=(10, 10))
        sns.heatmap(win_rate_pivot, annot=annotations, fmt="", linewidths=.5, cmap="RdYlGn", cbar=False)
        plt.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
        plt.xticks(rotation=30, ha="left")
        plt.show()


if __name__ == "__main__":
    pp = postProcessor("pt_lotr.txt")
    pp.identifyMetagame()
    pp.generateMatrix()
    pp.generateChart()
