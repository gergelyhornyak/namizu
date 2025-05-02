# naMizu Manual

**How to setup naMizu for you and your friends?**

## Prerequisites

You gonna need a 

1) server or a virtual machine, to host the backend. It consists of a *docker* container, running the webapp backend, and an *apache* reverse proxy.
2) best pracise is a Linux distro for the server, possibly Redhat, Ubuntu, or Debian. Neither Windows or MacOS is working. 
3) beginner skills in Python, Bash, and maybe HTML + CSS. In order to setup the server, you will need Bash skills to ssh to the server, clone the repository and start up the docker container. Python and HTML is helpful to modify the source code according to your needs.
4) one or two hours of your time. Setting up the server might last for only 10 minutes, however if you are new to AWS or Azure, or Linux, then it might take some time to get used to the terminal.

## Configure the server

If you have successfully set up the server, then you will need to set up the user database, and optionally the events bank database. These two databases serve the core of naMizu.

1) The user database keeps track of the information about all of the users/players.
2) The events bank database stores the events, polls, etc. It can grow large over the time.

### User DB setup

Place the following JSON file inside `namizu/flask-app/database` directory and name it users_db.json:

```json
{
    "ID1": {
        "uname": "NAME",
        "passw": "PASS",
        "profpic": "picX.png",
        "streak": 0,
        "loggedin": 0,
        "voted": {
            "dailyPoll": 0,
            "story": 0,
            "sidequest": 0
        },
        "lastlogin": "",
        "lastactive": "",
        "admin": 0
    }
}
```

> You add more users, and also customise each username, password, profile pic, and admin permission

### Events Bank setup

```json
{
    "E1": {
        "Type": "dailypoll,multichoice,public,ranking",
        "Options": {
            "option1": "London",
            "option2": "New York",
            "option3": "Paris",
            "option4": "Berlin",
            "option5": "Athen"
        },
        "Question": "Rank these cities.",
        "Pollster": "NAME",
        "Theme": "default_day",
        "Status": 0,
        "Answers": {},
        "Datetime": "2025-01-01 11:11:11",
        "Duedate": ""
    },
    "E2": {
        "Type": "dailypoll,singlechoice,anonym,yesorno",
        "Options": {
            "option1": "Definitely!",
            "option2": "Yes",
            "option3": "No",
            "option4": "Never!"
        },
        "Question": "Would you jump from a plane?",
        "Pollster": "NAME",
        "Theme": "default_day",
        "Status": 0,
        "Answers": {},
        "Datetime": "2025-02-02 22:22:22",
        "Duedate": ""
    }
}

```