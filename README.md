# sorcery
## A discord bot written using pycord.
Trying to build a full-fledged discord bot that can do almost everything.

## Music Features
### Core

- [x] **join** *join the voice channel user is in*
- [x] **disconnect** *disconnect from the voice channel if the bot is inactive*
- [x] **play** *search for a song or playlist and play*
- [x] **autoplay** *choose autoplay mode*
- [x] **toggle_playback** *pause/resume*
- [x] **skip** *skip current track*
- [x] **stop** *stop the track and clear the queue*
- [x] **volume** *set the volume*

### Sample Project Structure
```
project_root/
├── main.py
├── src/
│   ├── bot.py
│   └── __init__.py
├── cogs/
│   ├── fun/
│   │   ├── game.py
│   │   └── meme.py
│   ├── moderation/
│   │   ├── roles.py
│   │   └── ban.py
│   └── music/
│       ├── connect_lavalink.py
│       └── music_core.py
└── utils/
    ├── __init__.py
    └── shared_functions.py
```
