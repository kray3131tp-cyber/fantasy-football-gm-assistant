# Fantasy Football GM Assistant

A personal, read-only fantasy football analytics project for private decision support across Yahoo Fantasy Football and ESPN Fantasy Football leagues.

## Purpose

The project is designed to retrieve fantasy league data and turn it into weekly roster-management recommendations. It is intended for a single user's private use and is not a commercial product.

The planned analysis includes:

- League settings and scoring rules
- Team rosters and starting lineups
- Standings and weekly matchups
- Available players and waiver options
- Recent league transactions
- Injury, practice, depth-chart, and role changes
- Start/sit recommendations
- Waiver add/drop recommendations
- Trade analysis and proposed offers
- Rest-of-season roster construction
- D/ST and kicker streaming decisions

## Data Access

### Yahoo Fantasy Sports

Yahoo Fantasy Sports data will be accessed through Yahoo's official Fantasy Sports API using OAuth 2.0. The integration is intended to be read-only.

### ESPN Fantasy Football

ESPN league data will be collected separately for the user's private leagues. Authentication credentials and session values will never be committed to this public repository.

## Privacy and Security

This repository does not contain private fantasy-league credentials, OAuth secrets, browser-session cookies, personal league exports, or other sensitive account information.

Secrets will be stored outside version control, such as in local environment variables or a private secrets store.

## Transactions

The application is advisory only. It generates recommendations but does not autonomously submit lineup changes, waiver claims, add/drop transactions, or trades.

## Status

Early personal project / integration setup.
