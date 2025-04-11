# naMizu Docs

need to log current version

and do backup every day -> private github repo

---

naMizu events have the following members: 

- voter(s), 
- a pollster.

the events have the following components: 

- a unique ID, 
- a type based on the catalogue of types, 
- the question, 
- answer(s), *(response options)*
- a status, 
- a date-time.
- a language format (HU, EN, DE, IT, ...)

events can be: Story / SideQuest / DailyPoll

## Question Types

All polls fall under the following categories:

- Event category: Story / SideQuest / DailyPoll **(default)**
    - <dailypoll,story,sidequest>
    - DailyPoll: the usual daily poll, recurring every day.
    - Story: a series of polls, where each poll will inherit the previous answers, and voters can go on an DnD adventure.
    - SideQuest: pops up randomly, has a very unique task/poll for the voters

### SideQuest

very similar to dailypoll, but extreme

Task: Create a meme, sketch, or drawing ( based on a weird prompt )
Task: Trivia
Task: make words from letters
Task: you can only use emojis
Task: 2 true 1 false
Task: bet the poll outcome
Task: hangman
Task: haiku battle

### DailyPoll

- Using variable in the poll or not **(default)**
    - <variable,novariable>
    - Default: contains no variables
    - Variable: can be in poll question body or answers body, will be rendered during the edit stage
- Prompt extra text from users or no comment **(default)**
    - <prompt,noprompt>
    - Extra text: users need to submit a short answer
    - Nothing extra means answers are casual click buttons
- Single **(default)** or multichoice
    - <single,multichoice>
    - Single: voters can only pick one answer
    - Multichoice: voters can pick more than 1 answer at a time
- Anonym **(default)** or public 
    - <anonym,public>
    - Public: the voters identity is shows next to their answers, plus pollster name
    - Anonym: as usual, voters cannot see others' choices, nor pollster name
- Names **(default)** / Options / Range
    - <names,yesorno,openended,range>
    - Names: The names of the voters are the answers
    - Range: The pollster can set a range for the voters to select from - on a slider possibly
    - Options: The pollster can create custom options to vote for
        - Yes-or-no or open-ended **(default)**
        - Open-ended options: voters can select more open ended options at a time
        - Yes-or-no: excludes multichoice, since yes is the opposite of no
---

question type format:

dailypoll,variable,prompt,single,anonym,names
dailypoll,novariable,noprompt,multichoice,public,options,openended

---

*LEGACY TYPES:*

- **D**efault / Using **V**ariables
- **S**ingle or **M**ultiple choices
- **N**ames or **C**ustom options as choices
- The custom options are **Y**es-or-No questions, or user-defined **O**ptions

---

## Components/Routes

### Landing page

1) Banner
    - could change seasonally
2) username
    - show username who is logged in
3) Alert / Notice popup
    - any important info should show up on the top
4) Story / Sidequest
    - if sidequest or story is active, show up before DailyPoll
5) DailyPoll
6) Event Editor
7) Canvas + Gallery
8) naMizu info: opensource, free, no data collection...
9) Special Thanks
10) Version log

### Login page + logout page

User session cookie expiry date set to 1 week

session: 

- expiry date: 1 week = 604800 sec
- userID
- last app/url

Users will get streak, if they participate in any event

Users can log out of course anytime, their session restarts

Session keeps track of: username, webpage/app/state they were in, 

### DailyPoll page

#### Pre-choice state

1) Banner - app name
2) Back icon
3) ---
4) Question body
5) Answer body
9) Version log

#### Post-choice state

1) Banner - app name
2) Back icon
3) Calendar
4) Question body
5) voters statistics
    - how many people have voted
6) Results
7) Kudos section
    - good choice, or thats a good one...
8) Comments
    - messages
    - input field
9) Version log

### SideQuest page

### EventEditor page

1) Banner - app name
2) Back button
3) Advanced mode
4) Question body
5) Event Category
6) Written answer or not switch
7) Single or Multichoice switch   
8) Anonym or Public switch
9) Names or Options or Range switch
10) Yes/No or open-ended switch
11) Tutorial button
12) Preview button
13) Preview window
14) Submission button
15) Version log

### Calendar page

1) Banner
2) Back
3) Calendar
    - today is highlighted

### History pages

remains as it is

### Admin page

1) visit
2) voters present
3) voters list
4) question bank
5) used question
6) remaining question
7) remaining question types
8) list of question

Drawing Canvas page

Gallery page


## Database insight

poll format:

```json
  "IDX": {
    "Type": "DSNX",
    "Question": "Who is most likely to cheat on a test?",
    "Answers": {
        "Voter1": 0,
        "Voter2": 0,
        "Voter3": 0,
        "Voter4": 1,
        "Voter5": 0,
        "Voter6": 0,
        "Voter7": 0
    },
    "Status": 1
  }
```

---

new poll format:

```json
  "IDX": {
    "Type": "a,b,c,d,e",
    "Question": "Who is most likely to cheat on a test?",
    "Pollster": "UID",
    "Answers": {
        "Voter1": 0,
        "Voter2": 0,
        "Voter3": 0,
        "Voter4": 1,
    },
    "Status": 0
  }
  "IDX": {
    "Type": "a,b,c,d,e",
    "Question": "Who is most likely to cheat on a test?",
    "Answers": {
        "endpoints":{
            "0":"text",
            "10":"text",
        },
        "steps": 1,
        "votes":{
            "UID1":2,
            "UID2":5,
        }
    },
    "Status": 0
  }
```

---

databases:

- user_db.json
- questions_bank.json
- visit_count.json
- history.json
- today_poll.json
- comments.json
- drawings.json

---

users_db

```json
    "IDX": {
        "name": "NAME",
        "passw": "PASS",
        "voted": 0,
        "loggedin": 0,
        "streak": 0
    },
```

---

new users_db

```json
    "IDX": {
        "name": "NAME",
        "passw": "PASS",
        "profilePic":"",
        "participated": {
            "dailyPoll":0,
            "sideQuest":0,
            "story":0
        },
        "loggedin": 0,
        "streak": {
            "dailyPoll":0,
            "sideQuest":0,
            "story":0
        },
    },
```

---

history file:

```json
  "DD-MM-YYYY": {
        "Type": "XXXX",
        "Question": "QUESTION",
        "Answers": {
            "Yes": 0,
            "No": 0,
            "Maybe": 0
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
    },
```

---

## naMizu 3.0 update:

- mysql setup,
- profile pics?
- app? android or iOS