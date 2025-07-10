"""
Parse json data from chess.com's api and save into a json
"""

import requests
from urllib.parse import urljoin
import json
import time

# Chess.com Url
URL = "https://api.chess.com/pub/player/"

# Headers, Change if necessary
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "application/json",
}

# Add your username/friend user here
USERNAME = ""
FRIEND_USERNAME = ""

# Win/Loss/Draw conditions, everything i could find.
WIN_CONDS = ["win"]
LOSS_CONDS = ["lose", "checkmated", "timeout", "resigned", "threecheck"]
DRAW_CONDS = [
    "agreed",
    "repetition",
    "stalemate",
    "insufficient",
    "50move",
    "timevsinsufficient",
    "abandoned",
]

# Creating a session rather than separate requests, this is faster etc.
session = requests.Session()
# Only attach headers once
session.headers.update(HEADERS)


def get_archives() -> None:
    """
    Get all game archives and save available year/dates in a json file

    *saved file under date_archive.json*
    """
    # Grab URL base url provided
    url = urljoin(URL, f"{USERNAME}/games/archives")
    # Get a response using appropriate headers (Change if neccessary)
    response = session.get(url)
    # Error Checking
    response.raise_for_status()

    # Error code 200 is a get request success code, anything else should error
    if response.status_code == 200:
        print("Success")
        data = response.json()
        dates = data["archives"]
        all_dates = {}
        # Grabs all data in archives, splitting the dates.
        for i in dates:
            value = i.split("/")
            year, month = value[-2], value[-1]
            if int(year) < 2017:
                # Optional ^ only dates i care about are 2017 +
                continue
            # Adding each month to the provided year
            if year in all_dates:
                all_dates[year] += [month]
            else:
                all_dates[year] = [month]

        # Dumping it all in a json file - isn't actually needed
        with open("date_archive.json", "w") as f:
            json.dump(all_dates, f, indent=2)
        # Chose to dump to a json folder so that i'm not constantly doing get requests during testing etc
        # Optionally you can remove this dump, in favour of just saving the data and returning it
    else:
        raise Exception(
            "Something went wrong, response code: ",
            response.status_code,
            " is not status code 200",
        )


def get_urls() -> list[str]:
    """
    Grab URLS according to all archived games.

    Returns:
        list[str]: a list of url's in string format
    """
    try:
        with open("date_archive.json", "r") as f:
            data = json.load(f)
        # Load saved data, once again you can omit this step and change how the data is saved above
        # if you choose to return as a variable, just add the variable above
        url_dates = []
        for k, v in data.items():
            for i in v:
                url_dates.append(urljoin(URL, f"{USERNAME.lower()}/games/{k}/{i}"))
        # Creating a list of url dates based on username, year, and months provided
        return url_dates

    except Exception as e:
        raise Exception(f"Something went wrong: {e}")


def get_response(url: str) -> dict:
    """
    Args:
        url (str): input url to fetch data

    Raises:
        Exception: If status code is not 200
        RuntimeError: If Something goes wrong during fetching

    Returns:
        dict : response.json() for all the parsed info
    """

    try:
        # Use session and raise any errors
        response = session.get(url)
        response.raise_for_status()
        # handle proper status code and return the data
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                "Something went wrong, invalid status code: ", response.status_code
            )
    except Exception as e:
        raise RuntimeError(f"Something went wrong: {e}") from e


def skip_game(white, black):
    """
    Check if the game should be skipped.

    Args:
        white ( dict ): the json-data as a dict for the *white* player
        black ( dict ): the json-data as a dict for the *black* player

    Returns:
        bool: True if the game isn't against my friend, Else False

    """
    if FRIEND_USERNAME not in [white["username"], black["username"]]:
        # Skip over games that aren't against friend.
        return True
    return False


def check_winner(res) -> str:
    """
    Args:
        res (str): the result of the match (based on the *username*'s result)

    Raises:
        ValueError: If the condition is unknown

    Returns:
        str : returns the winner, either username or "draw"
    """
    if res in WIN_CONDS:
        return USERNAME
    elif res in LOSS_CONDS:
        return FRIEND_USERNAME
    elif res in DRAW_CONDS:
        return "Draw"
    else:
        raise ValueError(f"Unknown condition {res!r}")


def main(urls: list[str]) -> None:
    """
    Grab all chess.com data based on your games.
    Args:
        urls (list[str]): a list of fully-formatted urls passed in
    """

    # Final dict that gets pushed into a json file.
    final = {}
    # Each URL is unique Day/Month URL based on above get_urls()
    for url in urls:
        # get-request using Session
        data = get_response(url)
        # Just to show everything's not broken and still working
        print("Continuining.. New Url Processing")
        # Slight sleep timer, don't want to overload server, could remove or shorten
        time.sleep(0.5)

        # Splitting the url to use year/month in the dict (urls: {url}/{player}/games/{year}/{month})
        split_url = url.split("/")
        year, month = split_url[-2], split_url[-1]
        # List of all games played in the current year/month
        all_games = []

        for game in data["games"]:
            if game["time_class"] != "daily":
                # Skip non-daily games. Can change to anything you want here.
                continue

            # game['colour'] is a json dict that includes data on the username of the player, and the result etc
            white = game["white"]
            black = game["black"]

            if skip_game(white, black):
                # Skip games not against friend
                continue

            # Finds the desired username colour
            if USERNAME == white["username"]:
                res = white["result"]
            else:
                res = black["result"]

            # Sets winning status for below
            winner = check_winner(res)
            # append onto the list above
            all_games.append(
                {
                    "white": white["username"],
                    "black": black["username"],
                    "winner": winner,
                }
            )

        # Skip empty lists
        if all_games:
            # create an empty result in the dict
            if year not in final:
                final[year] = {}
            # set the new result
            final[year][month] = all_games
    # Final save into a json file. always indent-2 for readability
    try:
        with open("games_list.json", "w") as f:
            json.dump(final, f, indent=2)
    except Exception as e:
        raise Exception("something bad happened: ", e)


if __name__ == "__main__":
    # Run Separately/first then comment out (or change above logic for return status rather than save)
    # get_archives(USERNAME)

    # Run both together when above json is ready.
    urls = get_urls()
    main(urls)
