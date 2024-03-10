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
- Notifications for new youtube videos using the YouTube Data API v3
- Ability to set a custom server profile via a UI pop-up + the specified pronouns will also be provided for Gpt-4 when it answers a message
- A custom decorator for handling command costs making it possible to easily make commands cost currency from the economy system
- Abstract "scrollable" embeds enabling easy implementation of paged embeds wherever I need
- Simple routine system which will call a run method in specific modules in a specified interval
- An extensive set of useful utility function Im also reusing in other python projects
