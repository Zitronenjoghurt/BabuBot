# BabuBot
A discord bot with all kinds of stuff made with discord.py

# Features
- Very easily extendable entity-structure by making everything JSON de-/serializable using abstract entity classes, allowing for easy extension
- Database using sqlite which perfectly builds upon the JSON-serializable nature of entities
- An abstract API controller class with a custom rate limit decorator which makes it easy to interact with various APIs in a safe way
- Economy/Shop and Inventory system, being able to easily add new items
- Level System with leaderboard and rewards for level-ups
- Fishing Minigame with over 80 fish, prestige progression and commands to look into every aspect of the game
- Rocket launch notifications, keeping a specified channel up-to-date with recent rocket launches (also notifying about potantial hold-offs, failures or successes)
- A command to fetch random Astronomy Picture Of the Day entries from NASA and display them neatly
- Using the OpenAI API to randomly answer a message in a channel using 5 prior messages as context
- A command to fetch random pet (dog, cat, duck) pictures from different APIs
- Ability to set a custom server profile via a UI pop-up + the specified pronouns will also be provided for Gpt-4 when it answers a message
- A custom decorator for handling command costs making it possible to easily make commands cost currency from the economy system
- Abstract "scrollable" embeds enabling easy implementation of paged embeds wherever I need
- Simple routine system which will call a run method in specific modules in a specified interval
- An extensive set of useful utility function Im also reusing in other python projects

# Running it

`python bot.py`, with `src/config.json` filled in from `src/default_config.json`.
The database and both log files are written to the working directory.

There is also a `Dockerfile`. The image deliberately does **not** contain the
gitignored parts of the runtime — `src/config.json`, `src/assets/`,
`src/data/hidden_fish.json`, `src/data/ai_presets/` — so they have to be
bind-mounted over those paths at runtime:

```bash
docker build -t babubot .
docker run -d --name babubot \
  -e TZ=Europe/Berlin \
  -e BABUBOT_DB_PATH=/state/bot.db -e BABUBOT_LOG_DIR=/state \
  -v "$PWD/state:/state" \
  -v "$PWD/src/config.json:/app/src/config.json:ro" \
  -v "$PWD/src/assets:/app/src/assets:ro" \
  -v "$PWD/src/data/hidden_fish.json:/app/src/data/hidden_fish.json:ro" \
  -v "$PWD/src/data/ai_presets:/app/src/data/ai_presets:ro" \
  babubot
```

`TZ` matters: the bot reads a naive local clock for daily resets and cooldowns,
and a container with no `TZ` runs on UTC.

The Pokédex stat charts are generated to `BABUBOT_IMAGE_DIR` and then linked in
an embed by URL, so that directory has to be served by a web server at
`BABUBOT_IMAGE_BASE_URL` for the images to show up. Point both at whatever you
have; the bot only writes, and never reads them back.

| env var | default | |
|---|---|---|
| `BABUBOT_DB_PATH` | `bot.db` | where the SQLite database lives |
| `BABUBOT_LOG_DIR` | `.` | where `bot.log` and `discord.log` are written |
| `BABUBOT_LOG_LEVEL` | `DEBUG` | level for the bot's own logger |
| `BABUBOT_DISCORD_LOG_LEVEL` | `DEBUG` | level for the `discord.*` loggers |
| `BABUBOT_LOG_MAX_BYTES` | `0` | rotation size; `0` means never rotate |
| `BABUBOT_LOG_BACKUP_COUNT` | `3` | rotated files kept |
| `BABUBOT_IMAGE_DIR` | `tmp/images` | where generated Pokédex stat charts are written |
| `BABUBOT_IMAGE_BASE_URL` | `https://media.lemon.industries/pokemon` | public base URL those charts are served from |

The defaults are exactly what the bot did before any of these existed. Note that
`discord.log` at `DEBUG` writes a line per gateway frame and will reach gigabytes
over a few months, so set a level and a rotation size for any long-lived deploy.
