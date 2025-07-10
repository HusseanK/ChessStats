import requests
from urllib.parse import urljoin
import json
import time

URL = "https://api.chess.com/pub/player/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "application/json",
}


def get_archives(username: str) -> None:
    """
    Get all game archives and save available year/dates in a json file
    
    *saved file under date_archive.json*

    Args:
        username (str): chess.com username
    """
    # Grab URL base url provided
    url = urljoin(URL, f"{username}/games/archives")
    # Get a response using appropriate headers (Change if neccessary)
    response = requests.get(url, headers=headers)
    # Error Checking
    response.raise_for_status()

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
        # Chose to dump to a json folder so that i'm not constantly doing get requests
        # Optionally you can remove this dump, in favour of just saving the data and returning it

def get_urls(username: str) -> list[str]:
    """
    Grab URLS according to all archived games.
    Args:
        username (str): chess.com username

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
                url_dates.append(urljoin(URL, f"{username}/games/{k}/{i}"))
        # Creating a list of url dates based on username, year, and months provided
        return url_dates

    except Exception as e:
        # Will change exceptions later.
        print(e)


def main(urls: list[str]) -> None:
    """
    Grab all chess.com data based on your games.
    Args:
        urls (list[str]): a list of fully-formatted urls passed in

    Raises:
        Exception: _description_
    """


    # Really want to change this. Will find a better way possibly.
    for url in urls:
        # Slight sleep timer, don't want to overload server
        time.sleep(0.5)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            split_url = url.split('/')
            year, month = split_url[-2], split_url[-1]
            
            #TODO - Re-do below following new format.
            # all_games = {date: []}

            # count = 0
            # for game in data["games"]:
            #     all_games[date].append(
            #         {
            #             "game_num": count,
            #             "white": game["white"],
            #             "black": game["black"],
            #             "accuracies": game["accuracies"],
            #         }
            #     )

            # print(all_games)
            # try:
            #     with open("games_list.json", "w") as f:
            #         json.dump(all_games, f, indent=2)
            # except Exception as e:
            #     raise Exception("something bad happened: ", e)


if __name__ == "__main__":
    username = "husy15"
    # get_archives(username)
    urls = get_urls("husy15")
    print(urls[0])
    # main(urls)
