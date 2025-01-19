# naMizu Docs

## Introduction

naMizu is a free and open-source application based on askUs app.

## Features - Apps

### naMizu Poll

You can create, vote, and add comments for daily polls.

### naMizu Draw

You can draw a sketch and submit it, then you can see your artwork in the gallery 

## Polls

### Questions

All questions fall under some categories:

- **D**efault / Using **V**ariables
- **S**ingle or **M**ultiple choices
- **N**ames or **C**ustom options as choices
- The custom options are **Y**es-or-No questions, or user-defined **O**ptions

Some example questions:
- "Who is ..."
- "What would XYZ do ..."
- "Do you think XYZ would do ..."
- "Would XYZ1 and XYZ2 work together ..."
- "Would you rather do X or Y ..."
- "Pick all who would do X."

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
        "B\u00e1lint": 0,
        "Bella": 0,
        "Geri": 0,
        "Herczi": 1,
        "Hanna": 0,
        "Kopp\u00e1ny": 0,
        "M\u00e1rk": 0
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