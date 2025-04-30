# naMizu Documentation

## Overview

naMizu is a dynamic event-based polling application, where users interact through various events like DailyPolls, SideQuests, and Story-based adventures. It supports rich customization, anonymity, and 

Tech Stack: Flask · Jinja · Python3 · CSS · Bootstrap

Backup Policy: Daily backup to a private GitHub repository

Version Log: Logged in version tracker

## Theme - Day/Night

!fix! css variables

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

> `<html lang="en">` part of HTML needs to be changed according to event language, because of lang specific hyphenation rules

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

1. Create memes or sketches: Draw sketch based on prompt (weekend game - relaxed env)
2. Emoji-only responses - which one describes the best
3. Trivia / Honfoglaló: correct or closest wins ()
4. Two truths and a lie
5. Bet on outcome: bet before answering
6. Hangman: everyone gets 1 help
7. Haikus (could be difficult) - special event - based on celebrations - maybe based on full moons
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

---


## SVG & Graphing

Custom themes and range plots can use SVG Bezier curves:

SVG Commands:

M - Move \
L - Line \
C - Curve \
Z - Close path

## App Routes & Components

### Landing Page

1) Seasonal Banner
2) Logged-in Username
3) Alert/Popup
4) Active Story / SideQuest
5) Daily Joke
6) DailyPoll
7) Event Editor
8) Drawing Canvas & Gallery
9) naMizu Info
10) Special Thanks
11) Login/Logout
12) Version Log

> Session lasts 1 week (604800 seconds)
> Tracks:
> userID, last app visited

### Streak progression

Users will get streak, if they participate in any event

### Poll Pages

**DailyPoll Page**

Before Voting:

Banner, back icon, question & answers

After Voting:

Stats, results, comments, version log

**SideQuest Page**

**EventEditor Page**

All poll configuration options (Advanced Mode)

JSON editor in advanced mode

Live Preview

### Calendar Page

Date-based navigation
Today highlighted

### History Page

Archive of past polls
Could be in raw json format

### Admin Page

User visits
Voter tracking
Event bank management

## Database Overview

**Main Databases:**

- users_db.json
- events_bank.json
- visit_count.json
- history.json
- daily_poll.json
- comments.json
- drawings.json

## New User DB Format

```json
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
  "streak": 0
}
```
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

## Planned Features for v3.1+

- MySQL support
- Profile pictures
- Mobile app (Android / iOS)
- More minigames implemented


## TODO

részletesebben kifejteni az opciókat az Editorban ✅
gallery fix
comments to sidequest
spellingbee: categorise by topics, instead of players
switch between day and night theme

research new line and submit difference

new line in textarea

profile pics could be uploaded, to use funny images

range max: 10 ✅
range result visualise 

sideQuest - event maybe constrained to days
more events: for each
or 3 days

choose to show poll within 5 days

spontanous events / popups could be clear on duration: display how long 

range: when upgraded to gauss, can go over 10, right now keep it below 11

ranking: minimum 2 options

ranking: sum up points: 1st 5 pts 2nd 4 pts - show on bottom 

editor: range: scale size note on max 10 - integer 

country city male female

