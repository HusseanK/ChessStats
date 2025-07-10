import matplotlib.pyplot as plt
import json
import numpy as np

DATES = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "Aug",
    "09": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}


def import_games():
    with open("games_list.json", "r") as f:
        data = json.load(f)
    return data


def handle_games():
    # All Data from file
    data = import_games()
    # K = Year, V = Dict of months (05, 06 etc)
    final = {}
    for k, v in data.items():
        # Month, enumerated above, with each game
        total = {}

        for month, data in v.items():
            white_wins = 0
            black_wins = 0
            white_enemy_wins = 0
            black_enemy_wins = 0
            total_draws = 0
            for i in range(len(data)):
                winner = data[i]["winner"]
                if winner != "Husy15":
                    if winner == "Draw":
                        total_draws += 1
                        continue
                    if data[i]["white"] == "Husy15":
                        black_enemy_wins += 1
                        continue
                    else:
                        white_enemy_wins += 1
                        continue

                if data[i]["white"] == "Husy15":
                    white_wins += 1
                    continue
                black_wins += 1

            total[month] = {
                "white_wins": white_wins,
                "black_wins": black_wins,
                "white_enemy_wins": white_enemy_wins,
                "black_enemy_wins": black_enemy_wins,
                "total_draws": total_draws,
            }

        final[k] = total
    return final


def create_plot(
    year, wins_white, wins_black, white_enemy_wins, black_enemy_wins, draws
):

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    n = len(months)
    spacing = 2
    x = np.arange(n) * spacing
    width = 0.5

    _, ax = plt.subplots(figsize=(12, 6))

    ax.bar(
        x - width,
        wins_white,
        width,
        color="#FF6565",
        label="Wins (White)",
        edgecolor="#A50000",
    )

    ax.bar(
        x - width,
        wins_black,
        width,
        color="#B90000",
        bottom=wins_white,
        label="Wins (Black)",
        edgecolor="#A50000",
    )

    # Loss bars
    ax.bar(
        x,
        white_enemy_wins,
        width,
        color="#659BFF",
        label="Losses (White)",
        edgecolor="#001336",
    )

    ax.bar(
        x,
        black_enemy_wins,
        width,
        color="#002F87",
        bottom=white_enemy_wins,
        label="Losses (Black)",
        edgecolor="#001336",
    )

    ax.bar(x + width, draws, width, color="#25D312", label="Draws", edgecolor="green")

    ax.margins(0)
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.set_ylabel("wins")
    ax.legend(ncol=2, frameon=False)
    plt.title(year)
    plt.tight_layout()
    plt.show(block=False)


def handle_data():
    data = handle_games()
    for year, year_data in data.items():
        wins_white = np.zeros(12, dtype=int)
        wins_black = np.zeros(12, dtype=int)
        white_enemy_wins = np.zeros(12, dtype=int)
        black_enemy_wins = np.zeros(12, dtype=int)
        draws = np.zeros(12, dtype=int)
        for month, res in year_data.items():
            idx = int(month) - 1
            wins_white[idx] = int(res["white_wins"])
            wins_black[idx] = int(res["black_wins"])

            white_enemy_wins[idx] = int(res["white_enemy_wins"])
            black_enemy_wins[idx] = int(res["black_enemy_wins"])

            draws[idx] = int(res["total_draws"])

        create_plot(
            year, wins_white, wins_black, white_enemy_wins, black_enemy_wins, draws
        )


if __name__ == "__main__":
    handle_data()
    input()
