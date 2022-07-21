from riotwatcher import LolWatcher


class PlayerIdSearch:
    """
    Finds unique puuids seeded from the initial puuid
    """
    def __init__(self, api_key: str, initial_puuid: str, region: str):
        """
        :param initial_puuid: Initial puuid to start player search
        :param region: League region
        """
        self._initial_puuid = initial_puuid
        self.puuids = [initial_puuid]
        self.watcher = LolWatcher(api_key)
        self.region = region

    def _match_puuids_single_game(self, match_id: str):
        match_players = (
            self.watcher
                .match
                .timeline_by_match(self.region, match_id)
            ["info"]
            ["participants"]
        )
        return [x["puuid"] for x in match_players]

    def _add_new_puuids(self, puuid: str, n_matches: int = 10):
        match_history = self.watcher.match.matchlist_by_puuid(
            region=self.region,
            puuid=puuid,
            count=n_matches
        )
        all_puuids = []
        for match_id in match_history:
            puuids = self._match_puuids_single_game(match_id)
            all_puuids += puuids
        self.puuids += all_puuids
        self.puuids = list(set(self.puuids))

    def find_puuids(self, n_players=200):
        """
        Finds new player ids seeded from initial puuid.
        Updates the puuids attribute
        :param n_players: Number of players to search for - this can be slightly exceeded
        """
        i = 0
        while len(self.puuids) <= n_players:
            self._add_new_puuids(self.puuids[i])
            i += 1
