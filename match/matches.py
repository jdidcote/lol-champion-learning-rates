from typing import List, Tuple

from riotwatcher import LolWatcher

from data.config import Config


def get_match_history_statistics(
        watcher: LolWatcher,
        puuid: str,
        region: str,
        n_matches: int
    ) -> Tuple[dict, list]:
    """
    Go through the game histories for a puuid and get some stats for each participant in each game
    :param watcher: Instantiated LolWatcher object
    :param puuid:
    :param region:
    :param n_matches:
    :return: Dictonary of match history statistics and a list of observed match ids
    """

    # TODO: Add the match ids from the database in here to check
    observed_match_ids = []

    observed_puuids = []
    # List to store all observed match stats
    match_stats = []

    # Loop through puuids
    observed_puuids.append(puuid)

    match_ids = watcher.match.matchlist_by_puuid(region, puuid, count=n_matches)

    # Loop through matches
    for match_id in match_ids:

        if match_id in observed_match_ids:
            continue
        observed_match_ids.append(match_id)

        match_summary = watcher.match.by_id(region, match_id)

        game_summary = {}

        game_summary["match_id"] = match_id
        game_summary["region"] = region
        game_summary["game_mode"] = match_summary["info"]["gameMode"]
        game_summary["start_time"] = match_summary["info"]["gameStartTimestamp"]
        game_summary["end_time"] = match_summary["info"]["gameEndTimestamp"]

        participants = match_summary["info"]["participants"]

        match_participants = []
        for i, participant in enumerate(participants):
            participant_stats = {
                "puuid": match_summary["metadata"]["participants"][i],
                "champion_id": participant["championId"],
                "champion_name": participant["championName"],
                "summoner_id": participant["summonerId"],
                "position": participant["teamPosition"],
                "win": participant["win"]
            }
            match_participants.append(participant_stats)

        game_summary["participant_stats"] = match_participants

        match_stats.append(game_summary)

    return match_stats, observed_match_ids
