naMizu Documentation
Version: 3.0
Tech Stack: Flask · Jinja · Python 3 · CSS · Bootstrap
Backup Policy: Daily backup to a private GitHub repository
Version Log: Logged in version tracker

Overview
naMizu is a dynamic event-based polling application where users interact through various poll types like DailyPolls, SideQuests, and Story-based adventures. It supports rich customization, anonymity, and game-like progression.

Event Structure
Each event contains the following components:

Voter(s)

Pollster

Unique ID

Event Type: DailyPoll, Story, SideQuest

Question

Answers (response options)

Status

DateTime

Language Format: HU, EN, DE, IT, ...

Event Type IDs

Event Type	ID
DailyPoll	1
SideQuest	2
Story	3
Poll Categories
1. DailyPoll (default)
Variable Support:

variable or novariable

Selection Type:

single or multichoice

Visibility:

anonym (default) or public

Answer Format:

names, range, yesorno, openended, prompt, teams

Optional Features:

ranking: Answers can be ranked by preference.

chained: Follow-up questions based on results.

theme: Custom themes for appearance.

2. SideQuest
Randomized and creative polls, typically appearing every 5 days or on prime-numbered days.

Task Examples:

Create memes or sketches

Emoji-only responses

Trivia

Two truths and a lie

Bet on outcome

Hangman

Haiku battles

Word-based games

3. Story
A multi-event narrative experience.

Each new poll inherits previous answers.

Designed like a branching DnD-style adventure.

Question Type Format
Formatted as:

php-template
Copy
Edit
<category>,<variable>,<prompt>,<choice_type>,<visibility>,<answer_type>
Example:

plaintext
Copy
Edit
dailypoll,variable,prompt,single,anonym,names
Question Rules (Incompatible Combinations)
multichoice ❌ with yesorno, range, teams, prompt, public

single ❌ with ranking

anonym ❌ with teams

ranking ❌ with prompt, yesorno, teams

Question JSON Structure
json
Copy
Edit
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