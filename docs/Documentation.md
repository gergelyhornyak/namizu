# naMizu Documentation

## Overview

naMizu is a dynamic event-based polling application, where users interact through various events like DailyPolls, SideQuests, and Story-based adventures. It supports rich customization, anonymity, and 

Tech Stack: Flask · Jinja · Python3 · CSS · Bootstrap

Backup Policy: Daily backup to a private GitHub repository

Version Log: Logged in version tracker

## Table Of Content

1. [Background](#example)
2. [Content](#example)
3. [Apps](#example)
4. [Event Structures](#example2)
5. [Type Formats](#third-example)
6. [Roadmap](#third-example)
7. [Planned Features](#third-example)
8. [TODO](#third-example)

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

1. **SKETCHER**: Create memes or sketches: Draw sketch based on prompt (weekend game - relaxed env)
2. Emoji-only responses - which one describes the best
3. **TRIVIA**: Trivia / Honfoglaló: correct or closest wins ♻
4. Two truths and a lie 
5. **BETTING**: Bet on outcome: bet before answering -> evaluation is next day
6. **HANGMAN**: Hangman: everyone gets 1 help *
7. Haikus (could be difficult) - special event - based on celebrations - maybe based on full moons
8. **CATEGORIES**: Word-based games (county city names animal thing) ✅

* Genre: Turn-based Cooperative Word Game,
Style: Hangman,
Mode: Asynchronous Multiplayer,
Goal: Collaboratively guess the word before running out of lives (wrong attempts)

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
- public ❌ range

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


Future update: use SVG curve for Range plotting

```css

path {
    fill: #4f46e5; /* Indigo-600 */
    stroke: #1e40af; /* Indigo-900 */
    stroke-width: 2;
}
svg {
    width: 400px;
    height: 300px;
    background-color: white;
}

  <svg viewBox="0 0 400 200">
    <!-- Cubic Bezier Curve filled and closed to make a shape -->
    <path d="
      M 50 150
      C 150 110, 50 50, 350 150
      L 350 160
      L 50 160
      Z
    " />
  </svg>

```

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

differs based on the sidequest type

Country City Thing Animal Name:

- timer
- input field for each category
- exit button
- scoreboard
- comments

Trivia

- 3 questions sequencially
- Scoreboard
- comments?

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

## SideQuest DB Format

```json
{
    "Type": "trivia",
    "Datetime": "2025-05-08",
    "Body": {},
    "Submissions": {},
    "Comments": {}
}
```

## Roadmap

3.0.1: new poll types, new login system, sidequests
3.0.2: history fix
3.1.0: new sidequest: trivia
3.1.1: gallery fix
3.2.0: sql database instead of json
3.3.0: new mobile app

## Planned Features for v3.1+

- MySQL support
- Profile pictures
- Mobile app (Android / iOS)
- More minigames implemented


## TODO

!!!TEST CRONJOB!!!

gallery fix X

button to switch between day and night theme X

research new line and submit difference

new line in textarea - <pre> and "white-space: pre-wrap;"

profile pics could be uploaded, to use funny images

sideQuest - event maybe constrained to days
more events: for each
or 3 days

IMPORTANT: implement notice system: notice bank, expiry, message, colour [...]

ranking: minimum 3 options ✅
ranking: maximum 7 options ✅

ranking: sum up points: 1st 5 pts 2nd 4 pts - show on bottom 

editor: range: scale size note on max 10 - integer ✅

country city male female ✅

yesorno ✅

