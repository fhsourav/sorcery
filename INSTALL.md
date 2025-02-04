```bash
# For Ubuntu/Debian
sudo apt install libffi-dev
# Note: Use python 3.11
pip install -r requirements.txt
# Install wavelink manually with:
pip install -U wavelink --no-deps
```
- Lavalink server is required for music features.
- [Find Lavalink here.](https://lavalink.dev/)
- Keep Lavalink server address and password in a .env file
- Put your bot's discord token in the .env file as well. **!!!NEVER SHARE YOUR BOT'S TOKEN!!!**
```
<!-- example -->
LAVALINK_SERVER_ADDRESS=http://0.0.0.0:2333
LAVALINK_SERVER_PASSWORD=youshallnotpass
```
After the configurations are done, you can run the bot.
```bash
java -jar Lavalink.jar
```
```bash
python3 main.py
```
