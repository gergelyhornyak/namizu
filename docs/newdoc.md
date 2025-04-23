# naMizu Documentation

https://img.shields.io/badge/version-3.0.1-blue
https://img.shields.io/badge/release-develop-orange
https://img.shields.io/badge/stack-python-yellow

## Overview

naMizu is a dynamic event-based polling application, where users interact through various events like DailyPolls, SideQuests, and Story-based adventures. It supports rich customization, anonymity, and 

Tech Stack: Flask · Jinja · Python3 · CSS · Bootstrap

Backup Policy: Daily backup to a private GitHub repository

Version Log: Logged in version tracker

## Event Structure

Each event contains the following components:

- Unique ID
- Voter(s) / Participants
- Pollster / Author
- Event Type: DailyPoll, Story, SideQuest
- Question / Topic
- Answers (response options)
- Status
- DateTime
- Language Format: HU, EN, DE, IT, ...
- Theme

### Event Type IDs

- DailyPoll: 1
- SideQuest: 2
- Story: 3

### DailyPoll Categories

- Variable Support
- Selection Type: single or multichoice
- Visibility: anonym (default) or public
- Answer Format: names, range, yesorno, openended, prompt, teams, ranking (answers can be ranked by preference)
  + chained: Follow-up questions based on results.

### SideQuest

Randomized and creative polls, typically appearing every 5 days or on prime-numbered days.

Task Examples:

1. Create memes or sketches: Draw sketch based on prompt
2. Emoji-only responses - which one describes the best
3. Trivia: correct or closest wins
4. Two truths and a lie
5. Bet on outcome: bet before answering
6. Hangman: everyone gets 1 help
7. Haikus
8. Word-based games (county city names animal thing)

## Story

A multi-event narrative experience.

Each new poll inherits previous answers.

Designed like a branching DnD-style adventure.

## Question Type Format

`<category>,<variable>,<prompt>,<choice_type>,<visibility>,<answer_type>`

`dailypoll,variable,prompt,single,anonym,names`

### Question Rules (Incompatible Combinations)

- multichoice ❌ with yesorno, range, teams, prompt, public
- single ❌ with ranking
- anonym ❌ with teams
- ranking ❌ with prompt, yesorno, teams

## Question JSON Structure

```json
{
  "IDX": {
    "Type": "dailypoll,variable,prompt,single,anonym,names",
    "Theme": {
      "bgColour": "#HEX",
      "fontstyle": "style",
      "frontColour": "#HEX"
    },
    "Question": "Who is most likely to cheat on a test?",
    "Pollster": "UID",
    "Options": {
      "range config": "option list with IDs"
    },
    "Answers": {
      "Voter1": "value",
      "Voter2": 0
    },
    "Status": 0
  }
}
```

Legacy Type Format

Code	Meaning
S	Single Choice
M	Multi Choice
N	Names
C	Custom Options
Y	Yes/No
O	Open-ended
F	Teams (1v1)
Example: DMNX = Daily, Multi-choice, Names, Anonym

SVG & Graphing
Custom themes and range plots can use SVG Bezier curves:

html
Copy
Edit

SVG Commands:

M - Move

L - Line

C - Curve

Z - Close path

App Routes & Components
Landing Page
Seasonal Banner

Logged-in Username

Alert/Popup

Active Story / SideQuest

DailyPoll

Event Editor

Drawing Canvas & Gallery

naMizu Info

Special Thanks

Version Log

Login/Logout
Session lasts 1 week (604800 seconds)

Tracks:

userID, username, last app visited

Streak progression

Poll Pages
DailyPoll Page
Before Voting:

Banner, back icon, question & answers

After Voting:

Stats, results, kudos, comments, version log

SideQuest Page
EventEditor Page
All poll configuration options (Advanced Mode)

JSON editor

Live Preview

Calendar Page
Date-based navigation

Today highlighted

History Page
Archive of past polls

Admin Page
User visits

Voter tracking

Question bank management

Database Overview
Main Databases:
user_db.json

questions_bank.json

visit_count.json

history.json

today_poll.json

comments.json

drawings.json

New User DB Format
json
Copy
Edit
"IDX": {
  "name": "NAME",
  "passw": "PASS",
  "profilePic": "pic.png",
  "participated": {
    "dailyPoll": 0,
    "sideQuest": 0,
    "story": 0
  },
  "loggedin": 0,
  "streak": {
    "dailyPoll": 0,
    "sideQuest": 0,
    "story": 0
  }
}
Comments Format
json
Copy
Edit
"CID": {
  "uid": "UID",
  "appID": "APPID",
  "datetime": "DATETIME",
  "text": "TXT"
}
History Format
json
Copy
Edit
"DD-MM-YYYY": {
  "Type": "XXXX",
  "Question": "QUESTION",
  "Answers": {
    "Yes": 0,
    "No": 0
  },
  "Voted": {
    "IDX": {
      "name": "NAME",
      "voted": 0
    }
  },
  "Comments": [
    {
      "name": "NAME",
      "message": "COMMENT"
    }
  ]
}
Planned Features for v3.1+
MySQL support

Profile pictures

Mobile app (Android / iOS)