from flask import Blueprint, render_template, request, redirect, jsonify, url_for, session, flash, get_flashed_messages, send_from_directory
from datetime import datetime
import random
import base64
import json
import os
import re

bp = Blueprint('namizu', __name__, template_folder='templates')

# session: userID,lastURL

#* ERROR HANDLING

@bp.errorhandler(404)
def page_not_found404(e):
    return render_template('namizu/404.html'), 404

@bp.errorhandler(500)
def page_not_found500(e):
    return render_template('namizu/500.html'), 500

@bp.errorhandler(400)
def page_not_found400(e):
    return render_template('namizu/400.html'), 400

#* SMALL FUNCTIONS

def check_user_logged_in(funcName) -> tuple[bool, str]:
    print(f"{session = }")
    userID = ""
    if "userID" in session:
        userID = session["userID"]
        return True,userID
    else:
        session['url'] = funcName
        return False,userID

def typeParser(qTypeRaw:dict) -> dict:
    """
    singlechoice multichoice anonym public
    ranking names range yesorno 
    openended prompt teams
    """
    qTypeDescr = {
        "singlechoice":False,
        "multichoice":False,
        "anonym":False,
        "public":False,
        "ranking":False,
        "names":False,
        "range":False,
        "yesorno":False,
        "openended":False,
        "prompt":False,
        "teams":False,
    }
    
    flags = qTypeRaw.split(",")

    if "singlechoice" in flags:
        qTypeDescr["singlechoice"] = True
        qTypeDescr["multichoice"] = False
    elif "multichoice" in flags:
        qTypeDescr["singlechoice"] = False
        qTypeDescr["multichoice"] = True

    if "anonym" in flags:
        qTypeDescr["anonym"] = True
        qTypeDescr["public"] = False
    elif "public" in flags:
        qTypeDescr["anonym"] = False
        qTypeDescr["public"] = True

    if "names" in flags:
        qTypeDescr["names"] = True
        qTypeDescr["buttons"] = True
    elif "range" in flags:
        qTypeDescr["range"] = True
    elif "yesorno" in flags:
        qTypeDescr["yesorno"] = True
        qTypeDescr["buttons"] = True
    elif "openended" in flags:
        qTypeDescr["openended"] = True
        qTypeDescr["buttons"] = True
    elif "prompt" in flags:
        qTypeDescr["prompt"] = True
    elif "teams" in flags:
        qTypeDescr["teams"] = True
        qTypeDescr["buttons"] = True
    elif "ranking" in flags:
        qTypeDescr["ranking"] = True
    
    return qTypeDescr

def prettyPrintJson(jsonFile:dict) -> None:
    json_formatted_str = json.dumps(jsonFile, indent=4)
    print(json_formatted_str)

def findByID(uid:str) -> str:
    users_db = {}
    try:
        with open('database/user_db.json', 'r') as f:
            users_db = json.load(f)
    except Exception as e:
        print(e)
    try:
        username = users_db[uid]["uname"]
    except KeyError:
        print("User cannot be found.\n")
    return username

#* PAGEs and APPs

@bp.route('/login', methods=['GET', 'POST'])
def loginPage():  
    wrongPasswCounter = 0
    userData = {}
    with open('database/user_db.json', 'r') as f:
        userData = json.load(f)

    if request.method == "POST":
        uid = request.form["uid"]
        passw = request.form["password"]
        if( userData[uid]["passw"] == passw):
            print(f"Successful authentication. Welcome {userData[uid]['uname']}!")
            session["userID"] = uid
            session.modified = True
            userData[uid]["loggedin"] = 1
            userData[uid]["lastlogin"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('database/user_db.json', 'w') as f:
                json.dump(userData, f,indent=4)
            if 'url' in session:
                print(f"Redirecting back to {session['url']}.")
                return redirect(url_for(f"namizu.{session['url']}"))
        else:
            wrongPasswCounter+=1
            if(  wrongPasswCounter >= 3 ):
                print(f"Wrong password three times. Banned.")
            print(f"Wrong password. Try again.")
            
    return render_template('namizu/loginPage.html',userDataPacket=userData)

@bp.route("/landingpage")
@bp.route("/index")
@bp.route("/")
def landingPage():

    user_db = {}#loadAllUserInfo()
    with open('database/user_db.json', 'r') as f:
        user_db = json.load(f)

    session['url'] = "landingPage"
    userID = ""
    if "userID" in session:
        userID = session["userID"]    
        session['url'] = "landingpage"
    else:
        # prompt for login
        return redirect(url_for(f"namizu.loginPage"))
    
    banner = "NaMizu"
    userName = findByID(userID)
    notices = ["notice 1","notice 2"]
    storyStatus = False
    sideQuestStatus = False
    footerText = "2025 naMizu. Version 3.0 alpha (1481dfb), Built with care for the community."
    activeUsers = 3
    funnyMessage = "Not the restaurant"
    renderPacket = {}
    return render_template('/namizu/landingPage.html', 
                           banner=banner, notices=notices, funnyMessage=funnyMessage,
                           userName=userName, sideQuestStatus=sideQuestStatus,
                           activeUsers=activeUsers, footerText=footerText)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("namizu.landingPage"),302)

@bp.route("/dailypoll", methods=['GET', 'POST'])
def dailyPollApp():
    banner = ""
    dailyPoll = {}#getDailyPoll()
    ## test scenarios

    dailyPollRange = {
        "Type": "single,range,anonym",
        "Theme": "1",
        "Question": "What is the best age?",
        "Pollster": "X",
        "Options": {
            "mintext":"01234567890123456789",
            "maxtext":"01234567890123456789",
            "minvalue":1,
            "maxvalue":10,
        },
        "Answers": {
            "VID1": "4",
            "VID2": "5",
            "VID3": "8",
            "VID4": "5",
            "VID5": "5",
        },
        "Status": 0
    }

    dailyPollMulti = {
        "Type": "multichoice,names,anonym",
        "Theme": "1",
        "Question": "Who is the tallest?",
        "Pollster": "Lajos",
        "Options": {
            "o1":"Bálint",
            "o2":"Bella",
            "o3":"Geri",
            "o4":"Herczi",
            "o5":"Hanna",
            "o6":"Koppány",
            "o7":"Márk"
        },
        "Answers": {
            "VID1": ["o1","o5"],
            "VID2": ["o1","o5"],
            "VID3": ["o2"],
            "VID4": ["o5"],
            "VID5": ["o7"],
        },
        "Status": 0
    }

    dailyPollSingle = {
        "Type": "singlechoice,names,anonym",
        "Theme": "1",
        "Question": "Who is the tallest?",
        "Pollster": "Lajos",
        "Options": {
            "o1":"Bálint",
            "o2":"Bella",
            "o3":"Geri",
            "o4":"Herczi",
            "o5":"Hanna",
            "o6":"Koppány",
            "o7":"Márk"
        },
        "Answers": {
            "VID1": ["o1"],
            "VID2": ["o6"],
            "VID3": ["o3"],
            "VID4": ["o6"],
        },
        "Status": 0
    }

    dailyPollRank = {
        "Type": "multichoice,ranking,anonym",
        "Theme": "default",
        "Question": "Rank the following places!",
        "Pollster": "Geri",
        "Options": {
            "option1": "Budapest",
            "option2": "Debrecen",
            "option3": "P\u00e9cs",
            "option4": "G\u00f6d"
        },
        "Answers": {
            "VID1": ["option2","option1","option4","option3"],
            "VID2": ["option4","option2","option1","option3"],
            "VID3": ["option1","option2","option4","option3"],
            "VID4": ["option3","option2","option1","option4"],
        },
        "Status": 0
    }

    dailyPollPrompt = {
        "Type": "single,prompt,anonym",
        "Theme": "1",
        "Question": "Describe your best day.",
        "Pollster": "Lajos",
        "Options": {},
        "Answers": {
            "VID1": "jndkj dajsndjka sdkj naskjdn ajkdk ksa nd",
            "VID2": "odsao jaso jd oia sjd oi jwo idcnqincq cwqc",
            "VID3": "dn idjasc di cha sbhd csha chjd cj d",
            "VID4": "po pfdsfpoiswejc bhjc whd uqwuch qwuxn u wc éőéő",
            "VID5": "haha nope",
        },
        "Status": 0
    }

    dailyPoll = dailyPollSingle#dailyPollPrompt#dailyPollRank#dailyPollSingle#dailyPollMulti#dailyPollRange
    questionBody = dailyPoll["Question"]
    pollster = dailyPoll["Pollster"]
    questionType = dailyPoll["Type"]
    theme = dailyPoll["Theme"]
    theme = {
        "mainBG":"#bfe5f7",
        "bannerBG":"#50bbf3",
        "bannerTXT":"#000000",
        "questionBG":"#7bcdf6",
        "questionTXT":"#000000",
        "infoTXT":"#000000",
        "voteboxBG":"#dcded1",
        "voteboxTXT":"#000000"
    }
    optionsBody = dailyPoll["Options"]
    qTypeDescr = typeParser(questionType)
    voterStat = {
        "voteSum":2,
        "voterSum":7
    }
    answersBody = dailyPoll["Answers"]
    answersProcessed = {}

    if(not qTypeDescr["range"] and not qTypeDescr["prompt"]):
        # create unique list of choices
        for uid, oList in answersBody.items(): # optionList
            for oid in oList:
                option = optionsBody[oid] # get actual choice by ID
                if option not in answersProcessed:
                    answersProcessed[option] = {}
                    answersProcessed[option]["value"] = 1
                    answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                    answersProcessed[option]["voters"] = [uid]
                else:
                    answersProcessed[option]["value"] += 1
                    answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                    if(uid not in answersProcessed[option]["voters"]):
                        answersProcessed[option]["voters"].append(uid)

    if(qTypeDescr["range"]):
        for uid, option in answersBody.items():
            if option not in answersProcessed:
                answersProcessed[option] = {}
                answersProcessed[option]["value"] = 1
                answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                answersProcessed[option]["voters"] = [uid]
            else:
                answersProcessed[option]["value"] += 1
                answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                if(uid not in answersProcessed[option]["voters"]):
                    answersProcessed[option]["voters"].append(uid)

    if(qTypeDescr["prompt"]):
        pass

    if(qTypeDescr["names"] or qTypeDescr["ranking"] or qTypeDescr["openended"]):
        pass
    
    prettyPrintJson(answersProcessed)

    kudosMessage = "Grats!"
    comments = {}
    version = "3.0"

    if request.method == 'GET':    
        pass        

    elif request.method == 'POST':
        print(f"{request.form = }")
        # [('ranked_list', '["Göd","Budapest","Pécs","Debrecen"]')]
        # [('range_value', '3')]
        # [('promptMessage', 'jdassk jdnd kasd kas ndkka dsa ')]
        # MULTI [('o3', 'Geri'), ('o5', 'Hanna'), ('o6', 'Koppány')]
        # SINGLE [('o2', 'Geri')]

    return render_template('namizu/dailyPollPage.html', 
                           banner=banner,qTypeDescr=qTypeDescr,answersProcessed=answersProcessed,
                           theme=theme, optionsBody=optionsBody,voterStat=voterStat,kudosMessage=kudosMessage,
                           questionBody=questionBody, pollster=pollster, pollSubmitted=False
                           )


@bp.route("/sidequest", methods=['GET', 'POST'])
def sideQuestApp():
    return 0
    alreadyLoggedIn, userName = check_user_logged_in("sidequest")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))
    
@bp.route('/editor', methods=['GET', 'POST'])
def editorApp():
    namesList = ["Bálint","Bella","Geri","Herczi","Hanna","Koppány","Márk"]
    restartEditor = False
    session.pop('_flashes', None)
    pollBody = {
        "Type":"",
        "Question":"",
        "Options":{},
        "Pollster":"",
        "Theme":""
    }
    if request.method == "POST":
        #print(f"{request.form = }")
        pollBody["Question"] = request.form["question"]
        pollBody["Type"] = request.form["selectionType"] + "," + request.form["privacyType"] + "," + request.form["optionsType"]
        pollBody["Pollster"] = findByID("ID3")
        pollBody["Theme"] = "default"
        
        ## process Options

        if(request.form["optionsType"] == "yesorno"):
            pollBody["Options"] = {f"option{i+1}": val for i, val in enumerate(['Definitely!', 'Yes', 'No', 'Never!'])}
        if(request.form["optionsType"] == "names"):
            pollBody["Options"] = {f"option{i+1}": val for i, val in enumerate(namesList)}
        if(request.form["optionsType"] == "range"):
            pollBody["Options"] = {            
                "mintext": request.form["answer_range-1"],
                "maxtext": request.form["answer_range-2"],
                "minvalue":"1",
                "maxvalue":request.form["answer_range-3"],
            }
        if(request.form["optionsType"] == "teams"):
            pollBody["Options"] = {            
                "Team A": request.form["teams-1"],
                "Team B": request.form["teams-2"],
            }
        if(request.form["optionsType"] == "ranking"):
            rankingAnswers = [value for key, value in request.form.items() if key.startswith('answer_ranking')]
            #print(f"{rankingAnswers = }\n")
            pollBody["Options"] = {f"option{i+1}": val for i, val in enumerate(rankingAnswers)}
        if(request.form["optionsType"] == "openended"):
            openendedAnswers = [value for key, value in request.form.items() if key.startswith('answer_openended')]
            #print(f"{openendedAnswers = }\n")
            pollBody["Options"] = {f"option{i+1}": val for i, val in enumerate(openendedAnswers)}

        ## process the Question

        if "{" in pollBody["Question"] and "}" in pollBody["Question"]:
            text = pollBody["Question"]
            number_of_variables = text.count("{")
            number_of_variables_check = text.count("}")
            if number_of_variables!=number_of_variables_check:
                restartEditor = True
                flash("Typo in random name {P}.")
            if number_of_variables > 7:#voterSum()
                restartEditor = True
                flash("Too many variables.")
            # Names to replace - double the lenght, so less errors
            selected_names = random.sample(namesList, number_of_variables)
            # Replace placeholders sequentially
            try:
                result = re.sub(r"{P}", lambda _: selected_names.pop(0), text)
            except IndexError:
                print("No more names to pop out.\n")
            pollBody["Question"] = result

        prettyPrintJson(pollBody)

        ## ERROR CHECKING

        if("multichoice" in pollBody["Type"] and "yesorno" in pollBody["Type"]):
            flash("Cannot be yes-or-no and multi-choice at the same time. Session restarted")
        if("multichoice" in pollBody["Type"] and "range" in pollBody["Type"]):
            flash("Cannot be range and multi-choice at the same time. Session restarted")
        if("multichoice" in pollBody["Type"] and "teams" in pollBody["Type"]):
            flash("Cannot be teams and multi-choice at the same time. Session restarted")
        if("multichoice" in pollBody["Type"] and "prompt" in pollBody["Type"]):
            flash("Cannot be prompt and multi-choice at the same time. Session restarted")
        if("singlechoice" in pollBody["Type"] and "ranking" in pollBody["Type"]):
            flash("Cannot be ranking and single-choice at the same time. Session restarted")
        if("anonym" in pollBody["Type"] and "teams" in pollBody["Type"]):
            flash("Cannot be anonym and teams at the same time. Session restarted")

        if pollBody["Question"] == "":
            restartEditor = True
            flash("No question included. Session restarted")

        if not pollBody["Options"]:
            restartEditor = True
            flash("No answers included. Session restarted")

        for option in pollBody["Options"].values():
            if option == "":
                restartEditor = True
                flash("Some options are empty. Session restarted")    

        with open('database/questions_bank.json', 'r') as f:
            questions_bank =  json.load(f)
        for details in questions_bank.values():
            # chances are low
            if details["Question"] == pollBody["Question"] and details["Options"] == pollBody["Options"] and details["Type"] == pollBody["Type"]:
                restartEditor = True
                flash("This poll already exists. Session restarted.")
                break

        if not restartEditor:
            qid = "Q"+str(len(questions_bank)+1)
            questions_bank[qid] = pollBody
            with open('database/questions_bank.json', 'w') as f:
                json.dump(questions_bank, f, indent=4)
            flash("Poll submitted successfully.")
    
    return render_template('namizu/editorPage.html',namesList=namesList)


@bp.route("/sketcher/canvas")
def sketcherApp():
    return 0

@bp.route("/gallery/welcome")
def galleryApp():
    return 0

@bp.route("/calendar")
def calendarApp():
    return 0