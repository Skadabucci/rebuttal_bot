# Rebuttle Bot
The goal of this project is to find good replies to comments.

## How it works
The reddit bot uses praw to look through each submission and each comment in the submission. Then if any reply to any given comment is above a specific threshold, a rebuttal is found and saved. Additionally a reply is made to the rebuttal letting the user know they are cunning.

### Example
If a user comments "Hello" with a score of 1000 and someone replies "There" with a score of roughly 2000, then a rebuttal is found. 

### Notes
* Not all comment replies will be the definition of a rebuttal. It's just a name.
* A scalar function determines the threshold for what is and is not a rebuttal.
* Rebuttals are currently stored in json files

## Future / Backlog
* Tests
* Implement ASYNCIO!!!
* Web API/DB for storing rebuttals and a dashboard that contains a leaderboard
* Web Servers to run this bot
* Optimization

## Requirements
* git
* python3.6

## Installation
1. Clone the project and cd to it `git clone https://github.com/Boomerkuwanger/rebuttal_bot.git && cd rebuttal_bot`
2. Set up a virtualenv `virtualenv -p python3.6 .env`
3. Activate the env `. .env/bin/activate`
4. Pip install the requirements `pip install -r requirements.txt`
5. Set up a `praw.ini` file with a reddit script (instructions not included)
6. Run the code `python rebuttal_bot.py`

## Contributions
Please feel free to contribute pull requests, issues, or features you'd like to see!
