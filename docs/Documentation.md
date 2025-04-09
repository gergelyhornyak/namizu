# naMizu Docs

logs current version

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

### Questions

All polls fall under the following categories:

- Event category: Story / SideQuest / DailyPoll **(default)**
    - DailyPoll: the usual daily poll, recurring every day.
    - Story: a series of polls, where each poll will inherit the previous answers, and voters can go on an DnD adventure.
    - SideQuest: pops up randomly, has a very unique task/poll for the voters
- Using variable in the poll or not **(default)**
    - Default: contains no variables
    - Variable: can be in poll question body or answers body, will be rendered during the edit stage
- Requires extra text from users or no comment **(default)**
    - Extra text: users need to submit a short answer
    - Nothing extra means answers are casual click buttons
- Single **(default)** or multichoice
    - Single: voters can only pick one answer
    - Multichoice: voters can pick more than 1 answer at a time
- Anonym **(default)** or public 
    - Public: the voters identity is shows next to their answers
    - Anonym: as usual, voters cannot see others' choices
- Names **(default)** / Options / Range
    - Names: The names of the voters are the answers
    - Options: The pollster can create custom options to vote for
    - Range: The pollster can set a range for the voters to select from - on a slider possibly
- (if Options) Yes-or-no or open-ended **(default)**
    - Open-ended options: voters can select more open ended options at a time
    - Yes-or-no: excludes multichoice, since yes is the opposite of no

---

*LEGACY TYPES:*

- **D**efault / Using **V**ariables
- **S**ingle or **M**ultiple choices
- **N**ames or **C**ustom options as choices
- The custom options are **Y**es-or-No questions, or user-defined **O**ptions

---

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

databases:

- user_db.json
- questions_bank.json
- visit_count.json
- history.json
- today_poll.json
- comments.json
- drawings.json

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


## Big update ideas:

- mysql setup,
- profile pics?
- anonym voting?
- app? android vs iOS
- separate apps under naMizu