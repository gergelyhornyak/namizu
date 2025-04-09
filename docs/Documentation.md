# naMizu Docs

naMizu polls have the following members: 

- voter(s), 
- a pollster.

the polls have the following components: 

- a unique ID, 
- a type based on the catalogue of types, 
- the question, 
- answer(s), 
- a status, 
- a date-time.

### Questions

All questions fall under the following categories:

- Series of polls: create a story! -> each poll will inherit the previous answers
- Using variable in the poll or not (default)
- Requires extra text from users or no comment
- Single or multichoice
- Anonym or public (the voters)
- Names / Options / Range
- Yes-or-no or open-ended
- Normal (daily) poll or sidequest or letterloop

|var|exp|sin|pub|nam|yes|nor|

= almost 384 different poll types

Sidequest: trivia, 

---

*LEGACY TYPES:*

- **D**efault / Using **V**ariables
- **S**ingle or **M**ultiple choices
- **N**ames or **C**ustom options as choices
- The custom options are **Y**es-or-No questions, or user-defined **O**ptions

---

### Answers

### Comments

### Users - Voters

## Data insight

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