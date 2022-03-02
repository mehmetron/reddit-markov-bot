


# Reddit Markov Bot

### What is this?
This is a bot that generates text using a Markov chain.

Then it posts it to random hot posts on a specified list of subreddits.


### Why?
Just to show everyone, if a dumbo with a potato for a computer can do it then a state actor with billions of $$$ can probably do it undetected.


### How do I use it?
Beautiful question!

1. Create an .env file in the same directory as this file.
2. Populate said .env file with 
```
username=
password=
client_id=
secret=
user_agent=
```
3. Setup virtual env
```
pip3 install virtualenv
python3 -m venv env
source env/bin/activate
```
4. Install the dependencies.
```bash
pip3 install -r requirements.txt
```
5. Run the bot.
```bash
python3 bot.py
```


### How can I contribute?
It's a pretty simple program. Just fork it and add whatever you think is necessary.

