from pathlib import Path

import pandas as pd
from riotwatcher import LolWatcher


class PlayerIds:
    def __init__(self, region: str):
        self.file_path = Path("Data/puuids.csv")
        self.puuids = None
        self.region = region

    @property
    def file_exists(self) -> bool:
        return Path.is_file(self.file_path)

    def load_puuids(self) -> None:
        """
        Loads the currently saved player ids and stores in puuids attribute
        """
        if not self.file_exists:
            raise FileNotFoundError("No local file database found, please use set_db method to setup local database")
        self.puuids = pd.read_csv(self.file_path)

    def setup_db(self, puuid: str) -> None:
        """
        Sets up local database with a single puuid to get started
        :param puuid:  single puuid to setup database
        """
        if self.file_exists:
            print("Local database already exists, can't run setup")
            return
        puuids = pd.DataFrame({"puuid": puuid, "region": self.region}, index=[0])
        puuids.to_csv(self.file_path, index=False)

    def _match_puuids_single_game(self, watcher: LolWatcher, puuid: str):
        """
        Get the players in the last match played for a single puuid
        """
        last_match_id = watcher.match.matchlist_by_puuid(
            region=self.region,
            puuid=puuid,
            count=1
        )[0]

        match_players = (
            watcher
                .match
                .timeline_by_match(self.region, last_match_id)
            ["info"]
            ["participants"]
        )
        return [x["puuid"] for x in match_players]

    def find_new_puuids(self, api_key: str, n_puuids: int) -> None:
        """
        Finds new puuids seeded from the existing stored puuids
        :param n_puuids: Number of additional puuids to add, wil likely go slightly over this number
        """

        watcher = LolWatcher(api_key)

        if self.puuids is None:
            self.load_puuids()

        n_players_found = 0

        while n_players_found <= n_puuids:
            puuid = self.puuids.iloc[-1]["puuid"]

            # Get puuids of players last played with
            new_puuids = self._match_puuids_single_game(watcher, puuid)

            # Add to stored puuids and remove duplicates
            new_rows = pd.DataFrame({"puuid": new_puuids})
            new_rows["region"] = self.region
            self.puuids = pd.concat([self.puuids, new_rows]).drop_duplicates().reset_index(drop=True)
            n_players_found += new_rows["puuid"].nunique() - 1

        print(f"{n_players_found} new players found. Writing to database...")

        return
