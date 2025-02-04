# sorcery
## A discord bot written using pycord.
Trying to build a full-fledged discord bot that can do almost everything.

## Music Features
### Core

- [x] join
- [x] disconnect
- [x] play
- [x] toggle_playback
- [x] skip
- [x] stop
- [x] volume

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
