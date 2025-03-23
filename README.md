# sorcery
## A discord bot written using pycord.
Trying to build a full-fledged discord bot that can do almost everything.

## Music Features
### Core

- [x] **play** *search for a song or playlist and play*
- [x] **disconnect** *disconnect from the voice channel if the bot is inactive*
- [x] **autoplay** *choose autoplay mode*
- [x] **pausetoggle** *pause/resume*
- [x] **skip** *skip current track*
- [x] **stop** *stop the track and clear the queue*
- [x] **volume** *set the volume*
- [x] **lyrics** *display lyrics of the current track*
- [x] **nowplaying** *display information of the current track*

### Queue

- [x] **queue** *display the current queue*
- [x] **history** *display the queue history*
- [x] **autoplay queue** *display the autoplay queue*
- [x] **autoplay history** *display the autoplay history*
- [x] **autoplay mode** *set autoplay mode*
- [x] **loop** *set loop mode*
- [x] **remove** *remove from queue*
- [x] **skipto** *skip to another track in the queue*
- [x] **shuffle** *shuffle the queue*

### Playback Position Controls

- [x] **seek**
- [x] **fastforward**
- [x] **rewind**

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
