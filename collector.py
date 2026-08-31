import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

SEASON = int(os.getenv("ESPN_SEASON", "2026"))
SWID = os.getenv("ESPN_SWID")
ESPN_S2 = os.getenv("ESPN_S2")
LEAGUE_IDS = [
    x.strip()
    for x in [os.getenv("ESPN_LEAGUE_1", ""), os.getenv("ESPN_LEAGUE_2", "")]
    if x and x.strip()
]

BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season}/segments/0/leagues/{league_id}"
VIEWS = ["mTeam", "mRoster", "mMatchup", "mMatchupScore", "mSettings", "mStandings", "mStatus"]


def require_config():
    missing = []
    if not SWID:
        missing.append("ESPN_SWID")
    if not ESPN_S2:
        missing.append("ESPN_S2")
    if not LEAGUE_IDS:
        missing.append("ESPN_LEAGUE_1")
    if missing:
        raise SystemExit("Missing required .env values: " + ", ".join(missing))


def fetch_league(league_id: str) -> dict:
    url = BASE_URL.format(season=SEASON, league_id=league_id)
    params = [("view", view) for view in VIEWS]
    cookies = {"SWID": SWID, "espn_s2": ESPN_S2}
    headers = {"User-Agent": "fantasy-football-gm-assistant/0.1"}

    response = requests.get(url, params=params, cookies=cookies, headers=headers, timeout=30)

    if response.status_code in (401, 403):
        raise RuntimeError(
            f"ESPN denied access to league {league_id} ({response.status_code}). "
            "Your espn_s2 or SWID may be expired/incorrect, or the logged-in ESPN account may not have access."
        )
    response.raise_for_status()
    return response.json()


def normalize_league(raw: dict, league_id: str) -> dict:
    teams = []
    for team in raw.get("teams", []):
        roster_entries = team.get("roster", {}).get("entries", [])
        roster = []
        for entry in roster_entries:
            player = entry.get("playerPoolEntry", {}).get("player", {})
            roster.append(
                {
                    "player_id": player.get("id"),
                    "name": player.get("fullName"),
                    "default_position_id": player.get("defaultPositionId"),
                    "pro_team_id": player.get("proTeamId"),
                    "lineup_slot_id": entry.get("lineupSlotId"),
                    "injury_status": player.get("injuryStatus"),
                }
            )

        teams.append(
            {
                "team_id": team.get("id"),
                "name": team.get("name") or " ".join(
                    p for p in [team.get("location"), team.get("nickname")] if p
                ),
                "abbrev": team.get("abbrev"),
                "owners": team.get("owners", []),
                "record": team.get("record", {}),
                "waiver_rank": team.get("waiverRank"),
                "roster": roster,
            }
        )

    return {
        "source": "espn",
        "season": SEASON,
        "league_id": league_id,
        "league_name": raw.get("settings", {}).get("name"),
        "status": raw.get("status", {}),
        "settings": raw.get("settings", {}),
        "teams": teams,
        "schedule": raw.get("schedule", []),
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main():
    require_config()
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    print(f"Fetching {len(LEAGUE_IDS)} ESPN league(s) for {SEASON}...")

    for league_id in LEAGUE_IDS:
        try:
            raw = fetch_league(league_id)
            normalized = normalize_league(raw, league_id)

            raw_path = output_dir / f"espn_{league_id}_raw.json"
            normalized_path = output_dir / f"espn_{league_id}.json"

            raw_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
            normalized_path.write_text(json.dumps(normalized, indent=2), encoding="utf-8")

            team_count = len(normalized["teams"])
            league_name = normalized.get("league_name") or "Unnamed league"
            print(f"OK: {league_name} ({league_id}) — {team_count} teams")
            print(f"    Wrote {normalized_path}")
        except Exception as exc:
            print(f"ERROR league {league_id}: {exc}")


if __name__ == "__main__":
    main()
