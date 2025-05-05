import base64
from flask import Blueprint, render_template, request, redirect, send_from_directory, url_for, session, flash, current_app
import requests
from datetime import datetime, timedelta
import calendar
import random, json, re, string
import numpy as np
import os,shutil,subprocess

bp = Blueprint('namizu', __name__, template_folder='templates')

EVENTS_BANK = "database/events_bank.json"
USERS_DB = "database/users_db.json"
COMMENTS_CACHE = "database/comments.json"
SPELLING_BEE_BANK = "database/spelling_bee.json"
DAILY_POLL_CACHE = "database/daily_poll.json"
FUNNY_BANNERS_BANK = "database/funny_banners.json"
THEMES_BANK = "database/themes.json"
DATETIME_LONG = "%Y-%m-%d %H:%M:%S"
DATE_SHORT = "%Y-%m-%d"
TRADE_MARK = "naMizu\u2122"
VERSION = "3.0.1"
MOTTO_POOL = ["Built with care for the community.","By friends, for friends.","Community-powered fun, every single day.","Built together, played together."]
MOTTO = "Built with care for the community."

# session: userID,lastURL

#* ERROR HANDLING

#* SMALL FUNCTIONS

def updateSessionCookie(path:str):
    if "userID" in session:
        session['url'] = path
        session['time'] = datetime.now().strftime(DATETIME_LONG)
        with open(USERS_DB, 'r') as f:
            users_db = json.load(f)
        users_db[session["userID"]]["lastactive"] = datetime.now().strftime(DATETIME_LONG)
        with open(USERS_DB, 'w') as f:
            json.dump(users_db,f,indent=4)
    else:
        #print("")
        current_app.logger.error('userID missing, pls login')
        session['url'] = "landingPage"
        return redirect(url_for(f"namizu.loginPage"))

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

def usernameByID(uid:str) -> str:
    users_db = {}
    try:
        with open(USERS_DB, 'r') as f:
            users_db = json.load(f)
    except Exception as e:
        print(e)

    try:
        username = users_db[uid]["uname"]
    except KeyError:
        print("User cannot be found.\n")
    return username

def shortnameByID(uid:str) -> str:
    users_db = {}
    try:
        with open(USERS_DB, 'r') as f:
            users_db = json.load(f)
    except Exception as e:
        print(e)

    try:
        shortname = users_db[uid]["uname"][:2]
    except KeyError:
        print("User cannot be found.\n")
    return shortname

def appByID(aid):
    """DailyPoll: 1, SideQuest: 2, Story: 3"""
    return 1

def queryThemeDayMode(hour:int)->dict:
    themes = {}
    try:
        with open(THEMES_BANK, 'r') as f:
            themes = json.load(f)
    except Exception as e:
        print(e)
    return themes["default_day"]    
    if(hour > 20 or hour < 8):
        return themes["default_night"]
    else:
        return themes["default_day"]    
    
def queryThemeByName(name:str)->dict:
    themes = {}
    try:
        with open(THEMES_BANK, 'r') as f:
            themes = json.load(f)
    except Exception as e:
        print(e)
    return themes[name]    

def getTodayComments() -> dict:
    try:
        with open(COMMENTS_CACHE, 'r') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return {}    

def getUsersDatabase() -> dict:
    try:
        with open(USERS_DB, 'r') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return {}

def getDailyPoll() -> dict:
    try:
        with open(DAILY_POLL_CACHE, 'r') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return {}
    
def getEventsBank() -> dict:
    try:
        with open(EVENTS_BANK, 'r') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return {}
    
def queryMotto(day:int) -> str:
    random.seed(day)
    number = random.randint(0, len(MOTTO_POOL)-1)
    todayMotto = MOTTO_POOL[number]
    return todayMotto

def querySideEventOccurance(eventName) -> bool:
    """
    dailyJoke, sideQuest, story
    """
    sideQuestNumSeq = [1,4,8,11,15,18,22,25,28] # 3-4 days
    storyNumSeq =     [3,9,15,21,28]
    dailyJokeNumSeq = [2,3,5,6,7,9,10,12,13,14,16,17,19,20,21,23,24,26,27,29,30,31]
    
    yesterday = datetime.now() - timedelta(days=1)
    if(eventName == "dailyJoke"):
        if((datetime.now().day in dailyJokeNumSeq and datetime.now().hour >= 5) or
           ( yesterday.day in dailyJokeNumSeq and datetime.now().hour < 5)):
            return True
    if(eventName == "sideQuest"):
        if((datetime.now().day in sideQuestNumSeq and datetime.now().hour >= 5) or
           ( yesterday.day in sideQuestNumSeq and datetime.now().hour < 5)):
            return True
    if(eventName == "story"):
        if((datetime.now().day in storyNumSeq and datetime.now().hour >= 5) or
           ( yesterday.day in storyNumSeq and datetime.now().hour < 5)):
            return True
    return False

def switchUserThemeMode(currentTheme):
    if(currentTheme == "default_day"):
        return "default_night"
    elif(currentTheme == "default_night"):
        return "default_day"

#* PAGEs and APPs

@bp.route('/login', methods=['GET', 'POST'])
def loginPage():  
    wrongPasswCounter = 0
    theme = queryThemeDayMode(datetime.now().hour)
    footerText1 = f"\u00a9 {datetime.now().year} {TRADE_MARK}. Version {VERSION}." 
    footerText2 = queryMotto(datetime.now().day)
    userData = {}
    with open(USERS_DB, 'r') as f:
        userData = json.load(f)

    if request.method == "POST":
        uid = request.form["uid"]
        passw = request.form["password"]
        if( userData[uid]["passw"] == passw):
            print(f"Successful authentication!")
            current_app.logger.info("Successful authentication!")
            session["userID"] = uid
            session.modified = True
            session.permanent = True
            userData[uid]["loggedin"] = 1            
            userData[uid]["lastlogin"] = datetime.now().strftime(DATETIME_LONG)
            with open(USERS_DB, 'w') as f:
                json.dump(userData, f,indent=4)
            if 'url' in session:
                return redirect(url_for(f"namizu.{session['url']}"))
            return redirect(url_for("namizu.landingPage"))
        else:
            wrongPasswCounter+=1
            if(  wrongPasswCounter >= 3 ):
                print(f"Wrong password three times. Banned.")
            print(f"Wrong password. Try again.")
            
    return render_template('namizu/loginPage.html',userDataPacket=userData, theme=theme, 
                           footerText1=footerText1,footerText2=footerText2)

@bp.route("/landingpage")
@bp.route("/index")
@bp.route("/")
def landingPage():
    updateSessionCookie("landingPage")
    userID = ""
    if "userID" in session: userID = session["userID"]    
    else: return redirect(url_for(f"namizu.loginPage")) # prompt for login

    # log user activity

    user_db = getUsersDatabase()
    userEventStatus = {
        "dailyPoll":user_db[userID]["voted"]["dailyPoll"],
        "sideQuest":user_db[userID]["voted"]["sidequest"],
    }
    activeUsers = []
    #user_db[userID]["lastactive"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for uid, details in user_db.items():
        last_active_time = datetime.strptime(details["lastactive"], DATETIME_LONG)
        if( datetime.now() - last_active_time < timedelta(minutes=1,seconds=30) ):
            activeUsers.append(shortnameByID(uid))
    
    storyStatus = querySideEventOccurance("story")
    sideQuestStatus = querySideEventOccurance("sideQuest")
    dailyJokeStatus = querySideEventOccurance("dailyJoke")
    joke_data = {"joke":"NONE"}
    if(dailyJokeStatus):
        with open("database/daily_joke.json","r") as f:
            joke_data = json.load(f)
    dailyJoke = joke_data["joke"]
    
    userName = usernameByID(userID)
    noticeBank={}
    with open("database/notice_bank.json","r") as f:
        noticeBank = json.load(f)
    for n in noticeBank.keys():
        noticeBank[n]["remainingDays"] = (datetime.strptime(noticeBank[n]["endDate"], DATETIME_LONG) - datetime.now()).days
        if( noticeBank[n]["remainingDays"] == 0 ):
            noticeBank[n]["render"] = False
    banner = "naMizu"
    #\u00a9 COPYRIGHT SIGN
    footerDarkModeSwitchIcon = "🌘" if user_db[userID]["theme"] == "default_day" else "🌞"
    theme = queryThemeByName(user_db[userID]["theme"])
    footerText1 = f"{datetime.now().year} {TRADE_MARK}. Version {VERSION}." 
    footerText2 = queryMotto(datetime.now().day)
    
    funnyMessages = {}
    with open(FUNNY_BANNERS_BANK, 'r') as f:
        funnyMessages = json.load(f)
    random.seed(datetime.now().day)
    number = random.randint(1, len(funnyMessages))
    funnyMessage = funnyMessages[f"B{str(number)}"]

    #theme = queryThemeDayMode(datetime.now().hour)
    renderPacket = {}
    return render_template('/namizu/landingPage.html', 
                           banner=banner, noticeBank=noticeBank, funnyMessage=funnyMessage,
                           userName=userName, sideQuestStatus=sideQuestStatus,
                           activeUsers=activeUsers, footerTextTop=footerText1,footerTextBot=footerText2,footerDarkModeSwitchIcon=footerDarkModeSwitchIcon,
                           dailyJoke=dailyJoke, dailyJokeStatus=dailyJokeStatus, userEventStatus=userEventStatus,theme=theme)

@bp.route('/darkmode')
def darkMode():
    #updateSessionCookie("darkMode")
    users_db = getUsersDatabase()
    userID = session['userID']
    newTheme = switchUserThemeMode(users_db[userID]["theme"])
    users_db[userID]["theme"] = newTheme
    with open(USERS_DB, 'w') as f:
        json.dump(users_db,f,indent=4)
    return redirect(url_for("namizu.landingPage"),302)

@bp.route('/logout')
def logout():
    # set user to loggedout
    users_db = getUsersDatabase()
    users_db[session['userID']]["loggedin"] = 0
    with open(USERS_DB, 'w') as f:
        json.dump(users_db,f,indent=4)
    current_app.logger.info(f"User logged out.")
    session.clear()
    return redirect(url_for("namizu.landingPage"),302)

@bp.route("/dailypoll", methods=['GET', 'POST'])
def dailyPollApp():
    
    updateSessionCookie("dailyPollApp")
    userID = session['userID']

    pollSubmitted = False   
    users_db = getUsersDatabase()
    if(users_db[userID]["voted"]["dailyPoll"] == 1): # true
        pollSubmitted = True
    dailyPoll = getDailyPoll()
    questionBody = dailyPoll["Question"]
    pollster = dailyPoll["Pollster"]
    questionType = dailyPoll["Type"]
    theme = queryThemeDayMode(datetime.now().hour)
    optionsBody = dailyPoll["Options"]
    qTypeDescr = typeParser(questionType)
    answersBody = dailyPoll["Answers"]
    todayComments = getTodayComments()
    voteSum = np.sum([user["voted"]["dailyPoll"] for user in users_db.values()])
    voterStat = {
        "voteSum":voteSum,
        "voterSum":len(users_db)
    }
    answersProcessed = {}
    rankingProcessed = {}
    romanNumbers = []
    sidesProcessed = {}
    yesornoProcessed = {}
    rangeProcessed = {}
    answersList = []
    answersValue = None
    
    
    banner = ""
    kudosMessage = "Grats!"
    footerText1 = f"\u00a9 {datetime.now().year} {TRADE_MARK}. Version {VERSION}." 
    footerText2 = queryMotto(datetime.now().day)

    if request.method == 'GET':    
        pass        

    elif request.method == 'POST':
        if not pollSubmitted:
            if 'comment' not in request.form:

                if(qTypeDescr["ranking"]):
                    answersList = request.form["ranked_list"]
                    answersList = json.loads(answersList)
                elif(qTypeDescr["range"]):
                    answersValue = request.form["range_value"]
                elif(qTypeDescr["prompt"]):
                    answersList = request.form["prompt_message"]
                elif( (qTypeDescr["singlechoice"] and qTypeDescr["names"]) or
                    (qTypeDescr["singlechoice"] and qTypeDescr["openended"]) or
                        qTypeDescr["yesorno"] or qTypeDescr["teams"] ):
                    answersValue = request.form["vote"]
                elif( (qTypeDescr["multichoice"] and qTypeDescr["openended"]) or 
                    (qTypeDescr["multichoice"] and qTypeDescr["names"]) ): 
                    for value in request.form.values():
                        answersList.append(value)

                if(answersValue):
                    answersBody[userID] = answersValue
                elif(answersList):
                    answersBody[userID] = answersList

                pollSubmitted = True

                # update user vote info
                users_db[userID]["voted"]["dailyPoll"] = 1
                # also increase their streak
                with open(USERS_DB, 'w') as f:
                    json.dump(users_db,f,indent=4)     
                # also increase visits count
                with open("database/visit_count.json", 'r') as f:
                    visitCount = json.load(f)     
                visitCount["total"] += 1
                visitCount["dailypoll"] += 1
                with open("database/visit_count.json", 'w') as f:
                    json.dump(visitCount,f,indent=4)     
                # add new answer to today poll
                dailyPoll["Answers"] = answersBody
                with open(DAILY_POLL_CACHE, 'w') as f:
                    json.dump(dailyPoll,f,indent=4)              
                return redirect(url_for('namizu.dailyPollApp'))

        else:
            if 'comment' in request.form:
                comment = request.form['comment']
                current_date = datetime.now().strftime(DATETIME_LONG)
                
                todayComments["dailyPoll"][current_date] = {
                    "userID": userID,
                    "text":comment,
                    "username":usernameByID(userID)
                }           
                with open(COMMENTS_CACHE, 'w') as f:
                    json.dump(todayComments, f, indent=4)
                return redirect(url_for('namizu.dailyPollApp'))
            
    
    if( (qTypeDescr["singlechoice"] and qTypeDescr["names"]) or
        (qTypeDescr["singlechoice"] and qTypeDescr["openended"]) ):

        for uid, option in answersBody.items(): # option is a value
            if option not in answersProcessed:
                answersProcessed[option] = {}
                answersProcessed[option]["value"] = 1
                answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                answersProcessed[option]["voters"] = [shortnameByID(uid)]
            else:
                answersProcessed[option]["value"] += 1
                answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                if(uid not in answersProcessed[option]["voters"]):
                    answersProcessed[option]["voters"].append(shortnameByID(uid))
    elif( qTypeDescr["range"] ):
        preprocessed = {}
        rangeProcessed = {
            "mintext":optionsBody["mintext"],
            "maxtext":optionsBody["maxtext"],
            "maxvalue":optionsBody["maxvalue"],
            "range":[],
            "distribution":[]
        }
        preprocessed = {str(k):0 for k in range(1,int(optionsBody["maxvalue"])+1)}
        for uid, pick in answersBody.items(): # option is a value
            preprocessed[pick] += 1
        rangeProcessed["range"] = [int(k) for k in preprocessed.keys()]
        rangeProcessed["distribution"] = list(preprocessed.values())
            
    elif(qTypeDescr["prompt"]):
        for uid, text in answersBody.items(): # option is a value
            answersProcessed[uid] = {
                "username":usernameByID(uid),
                "text": text
            }
    elif(qTypeDescr["ranking"]):
        romanNumbers = ["I","II","III","IV","V","VI","VII","VIII","IX","X"]
        for uid, options in answersBody.items(): # options is a list

            #top_three = dict(zip(romanNumbers[:3], options[:3]))
            #top_three = {f"{i+1}": val for i, val in enumerate(options[:3])}
            top_three = {f"{i+1}": {"roman":romanNumbers[i], "name":val} for i, val in enumerate(options[:3]) }
            #others = dict(zip(romanNumbers[3:], options[3:]))
            #others = {f"{i+4}": val for i, val in enumerate(options[3:])}
            others = {f"{i+4}": {"roman":romanNumbers[i+3], "name":val} for i, val in enumerate(options[3:]) }
            rankingProcessed[uid] = {
                "username": usernameByID(uid),
                "profpic": users_db[uid]["profpic"],
                "top_three": top_three,
                "others": others
            }

    elif(qTypeDescr["teams"]):
        sidesProcessed = {}
        for sideName, value in optionsBody.items():
            sidesProcessed[sideName] = {
                "score":0,
                "name":value,
                "voters":[]
            }
            for uid, option in answersBody.items():
                if (option == value):
                    sidesProcessed[sideName]["score"] += 1
                    sidesProcessed[sideName]["voters"].append(usernameByID(uid))
    
    elif(qTypeDescr["yesorno"]):
        yesornoProcessed = {
            "Definitely":0,
            "Yes":0,
            "No":0,
            "Never":0,
            "YesSide":{},
            "NoSide":{}
        }
        for uid, option in answersBody.items(): # options is a value
            
            if(option.lower()=="yes"):
                yesornoProcessed["Yes"] += 1
                yesornoProcessed["YesSide"][uid] = shortnameByID(uid)
            elif(option.lower()=="definitely"):
                yesornoProcessed["Definitely"] += 1*3 # yesornoMultiplier
                yesornoProcessed["YesSide"][uid] = shortnameByID(uid)
            elif(option.lower()=="no"):
                yesornoProcessed["No"] += 1
                yesornoProcessed["NoSide"][uid] = shortnameByID(uid)
            elif(option.lower()=="never"):
                yesornoProcessed["Never"] += 1*3
                yesornoProcessed["NoSide"][uid] = shortnameByID(uid)

    elif( (qTypeDescr["multichoice"] and qTypeDescr["names"]) or
        (qTypeDescr["multichoice"] and qTypeDescr["openended"]) ):
        for uid, options in answersBody.items(): # option is a list
            for option in options:
                if option not in answersProcessed:
                    answersProcessed[option] = {}
                    answersProcessed[option]["value"] = 1
                    answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                    answersProcessed[option]["voters"] = [shortnameByID(uid)]
                else:
                    answersProcessed[option]["value"] += 1
                    answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                    if(uid not in answersProcessed[option]["voters"]):
                        answersProcessed[option]["voters"].append(shortnameByID(uid))    

    return render_template('namizu/dailyPollPage.html', 
                           banner=banner,footerTextTop=footerText1,footerTextBot=footerText2,
                           qTypeDescr=qTypeDescr,optionsBody=optionsBody,voterStat=voterStat,questionBody=questionBody,
                           answersProcessed=answersProcessed,rankingProcessed=rankingProcessed,
                           rangeProcessed=rangeProcessed,yesornoProcessed=yesornoProcessed,sidesProcessed=sidesProcessed,
                           theme=theme,kudosMessage=kudosMessage,roman=romanNumbers,
                           pollster=pollster, pollSubmitted=pollSubmitted,
                           todayComments=todayComments["dailyPoll"])

@bp.route('/editor', methods=['GET', 'POST'])
def editorApp():
    updateSessionCookie("editorApp")
    users_db = {}
    users_db = getUsersDatabase()
    events_bank = {}
    namesList = [user["uname"] for user in users_db.values()]
    theme = queryThemeDayMode(datetime.now().hour)
    restartEditor = False
    
    userID = session['userID']
    
    pollBody = {
        "Type":"",
        "Options":{}
    }

    footerText1 = f"\u00a9 {datetime.now().year} {TRADE_MARK}. Version {VERSION}." 
    footerText2 = queryMotto(datetime.now().day)
    
    if request.method == "POST":
        
        session.pop('_flashes', None)
        if ( request.form["question"] == "" or
             request.form["selectionType"] == "" or
             "privacyType" not in request.form or
             ("optionsType" not in request.form or 
              "answer_openended-1" not in request.form or
              "answer_ranking-1" not in request.form or
              "answer_range-1" not in request.form or
              "answer_teams-1" not in request.form)
            ):
            restartEditor = True
            flash("Event incorrect. Session restarted")
            return redirect(url_for('namizu.editorApp'))

        eventType = "dailypoll"
        pollBody["Question"] = request.form["question"]
        pollBody["Type"] = f"{eventType},{request.form['selectionType']},{request.form['privacyType']},{request.form['optionsType']}"
        pollBody["Pollster"] = usernameByID(userID)
        pollBody["Theme"] = "default_day"
        pollBody["Status"] = 0
        pollBody["Answers"] = {}
        pollBody["Datetime"] = datetime.now().strftime(DATETIME_LONG)
        pollBody["Duedate"] = ""
        
        ## process Options

        if(request.form["optionsType"] == "prompt"):
            pollBody["Options"] = {"shape":"cloud"}
        if(request.form["optionsType"] == "yesorno"):
            pollBody["Options"] = {f"option{i+1}": val for i, val in enumerate(['Definitely', 'Yes', 'No', 'Never'])}
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
                "redteam": request.form["answer_teams-1"],
                "blueteam": request.form["answer_teams-2"],
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


        ## ERROR CHECKING

        if("multichoice" in pollBody["Type"] and "yesorno" in pollBody["Type"]):
            restartEditor = True
            flash("Cannot be yes-or-no and multi-choice at the same time. Session restarted")
        if("multichoice" in pollBody["Type"] and "range" in pollBody["Type"]):
            restartEditor = True
            flash("Cannot be range and multi-choice at the same time. Session restarted")
        if("multichoice" in pollBody["Type"] and "teams" in pollBody["Type"]):
            restartEditor = True
            flash("Cannot be teams and multi-choice at the same time. Session restarted")
        if("multichoice" in pollBody["Type"] and "prompt" in pollBody["Type"]):
            restartEditor = True
            flash("Cannot be prompt and multi-choice at the same time. Session restarted")
        if("singlechoice" in pollBody["Type"] and "ranking" in pollBody["Type"]):
            restartEditor = True
            flash("Cannot be ranking and single-choice at the same time. Session restarted")
        if("anonym" in pollBody["Type"] and "teams" in pollBody["Type"]):
            restartEditor = True
            flash("Cannot be anonym and teams at the same time. Session restarted")

        if( "ranking" in pollBody["Type"] ):
            if(len(pollBody["Options"]) < 3):
                restartEditor = True
                flash("Ranking requires at least 3 options. Session restarted")    

        if( "range" in pollBody["Type"] ):
            if( not pollBody["Options"]["maxvalue"].isdigit() ):
                restartEditor = True
                flash("Range must be a number. Session restarted")    
            else:
                if ( int(pollBody["Options"]["maxvalue"]) < 2 ):
                    restartEditor = True
                    flash("Range too low. Session restarted")    
                elif( int(pollBody["Options"]["maxvalue"]) > 10 ):  
                    restartEditor = True
                    flash("Range too high. Session restarted")

        if pollBody["Question"] == "":
            restartEditor = True
            flash("No question included. Session restarted")

        if not pollBody["Options"]:
            restartEditor = True
            flash("No answers included. Session restarted")

        # if options are matching
        if( len(set(pollBody["Options"].values())) != len(pollBody["Options"].values()) ):
            restartEditor = True
            flash("Some options are identical. Please add unique options. Session restarted")    

        for option in pollBody["Options"].values():
            if option == "":
                restartEditor = True
                flash("Some options are empty. Session restarted")    

        with open(EVENTS_BANK, 'r') as f:
            events_bank =  json.load(f)
        for details in events_bank.values():
            # chances are low
            if details["Question"] == pollBody["Question"] and details["Options"] == pollBody["Options"] and details["Type"] == pollBody["Type"]:
                restartEditor = True
                flash("This poll already exists. Session restarted.")
                break

        if not restartEditor:
            qid = "E"+str(len(events_bank)+1)
            events_bank[qid] = pollBody
            with open(EVENTS_BANK, 'w') as f:
                json.dump(events_bank, f, indent=4)
            flash(f"Good job! 😁 {eventType.upper()} submitted successfully.")

        return redirect(url_for('namizu.editorApp'))
    
    return render_template('namizu/editorPage.html',namesList=namesList, theme=theme, 
                           footerTextTop=footerText1,footerTextBot=footerText2)


@bp.route("/calendar")
def calendarApp():
    updateSessionCookie("calendarApp")
    theme = queryThemeDayMode(datetime.now().hour)
    return render_template('namizu/calendarPage.html', theme=theme)

## Funny Apps

@bp.route('/spellingbee/countdown', methods=['POST'])
def startCountdown():
    userID = session['userID']
    usersDB = getUsersDatabase()
    username = usernameByID(userID)
    if request.method == "POST":
        with open(SPELLING_BEE_BANK,"r") as f:
            spellingBee = json.load(f)
        if( userID in spellingBee["submissions"].keys() ):
            submissionDatetime = datetime.strptime(spellingBee["submissions"][userID]["begin"], DATETIME_LONG)
            pass
        else:
            userSubmission = {
            "uname": username,
            "begin": datetime.now().strftime(DATETIME_LONG),
            "end": "",
            "cheated": False,
            "country": {
                "answer": "",
                "correct":0,
                "colour":"transparent"
                },
            "city": {
                "answer": "",
                "correct":0,
                "colour":"transparent"
                },
            "thing": {
                "answer": "",
                "correct":0,
                "colour":"transparent"
                },
            "animal": {
                "answer": "",
                "correct":0,
                "colour":"transparent"
                },
            "male": {
                "answer": "",
                "correct":0,
                "colour":"transparent"
                },
            "female": {
                "answer": "",
                "correct":0,
                "colour":"transparent"
                }
            }
            spellingBee["submissions"][userID] = userSubmission
        with open(SPELLING_BEE_BANK,"w") as f:
            json.dump(spellingBee,f,indent=4)
    return '', 204  # No Content
        

@bp.route('/spellingbee',methods=['GET','POST'])
def spellingBeeApp():
    updateSessionCookie("spellingBeeApp")
    userID = session['userID']
    usersDB = getUsersDatabase()
    theme = queryThemeDayMode(datetime.now().hour)
    guessTime = 70 ## seconds
    data = {}
    words = []
    spellingBee = {}
    if request.method == "GET":

        with open(SPELLING_BEE_BANK,"r") as f:
            spellingBee = json.load(f)

        # check if user already played it
        if( usersDB[userID]["voted"]["sidequest"] == 1 ):
            return redirect(url_for('namizu.spellingBeeScoreBoard'))

        if( userID in spellingBee["submissions"].keys() ):
            submissionDatetime = datetime.strptime(spellingBee["submissions"][userID]["begin"], DATETIME_LONG)
            guessTime -= (datetime.now() - submissionDatetime).total_seconds()
            guessTime = max(0,int(guessTime))

        return render_template('namizu/spellingBeePage.html', 
                               letter=spellingBee["letter"], countdown=guessTime, theme=theme)
    
    elif request.method == "POST":

        with open(SPELLING_BEE_BANK,"r") as f:
            spellingBee = json.load(f)
        
        submissionDatetime = datetime.strptime(spellingBee["submissions"][userID]["begin"], DATETIME_LONG)
        current_app.logger.info(f"Minigame guess time: {datetime.now() - submissionDatetime} > {timedelta(seconds=guessTime+4)}")
        if( datetime.now() - submissionDatetime > timedelta(seconds=guessTime+4) ):
            current_app.logger.error("Spelling bee guess time error: longer guess time. Probably restarted session.")
            spellingBee["submissions"][userID]["cheated"] = True

        spellingBee["submissions"][userID]["country"]["answer"] = request.form.get("country").lower()
        spellingBee["submissions"][userID]["city"]["answer"] = request.form.get("city").lower()
        spellingBee["submissions"][userID]["thing"]["answer"] = request.form.get("thing").lower()
        spellingBee["submissions"][userID]["animal"]["answer"] = request.form.get("animal").lower()
        spellingBee["submissions"][userID]["male"]["answer"] = request.form.get("male").lower()
        spellingBee["submissions"][userID]["female"]["answer"] = request.form.get("female").lower()        
        
        todaysLetter_lower = spellingBee["letter"].lower()

        for uid,details in spellingBee["submissions"].items():
            for uid_DIFF,details_DIFF in spellingBee["submissions"].items():
                if( uid != uid_DIFF ):
                    if( details["country"] == details_DIFF["country"] ):
                        spellingBee["submissions"][uid]["country"]["alreadyExists"] = 1
                        spellingBee["submissions"][uid_DIFF]["country"]["alreadyExists"] = 1
                    if( details["city"] == details_DIFF["city"] ):
                        spellingBee["submissions"][uid]["city"]["alreadyExists"] = 1
                        spellingBee["submissions"][uid_DIFF]["city"]["alreadyExists"] = 1

        # continue for each category, then put them into 3 categories:
        # correct, correct and unique, wrong

        """
        "ID3": {
            "uname": "Geri",
            "begin": "2025-05-04 09:29:07",
            "end": "2025-05-04 09:30:17",
            "cheated": false,
            "country": {
                "answer": "\u00e9szorsz\u00e1g",
                "correct": 0,
                "colour": "transparent"
            },
            "city": {
                "answer": "\u00e9rd",
                "correct": 0,
                "colour": "transparent"
            },
        """
        
        # with open("database/words.txt","r") as f:
        #     words = [line.strip().lower() for line in f if line.strip()]

        # for word in words:
        #     if( spellingBee["submissions"][userID]["country"]["answer"] == word and 
        #         spellingBee["submissions"][userID]["country"]["answer"][0] == todaysLetter_lower ):

        #         spellingBee["submissions"][userID]["country"]["correct"] = 1
        #         spellingBee["submissions"][userID]["country"]["colour"] = "#648f2380"


        #     if( spellingBee["submissions"][userID]["city"]["answer"] == word and 
        #         spellingBee["submissions"][userID]["city"]["answer"][0] == todaysLetter_lower ):

        #         spellingBee["submissions"][userID]["city"]["correct"] = 1
        #         spellingBee["submissions"][userID]["city"]["colour"] = "#648f2380"


        #     if( spellingBee["submissions"][userID]["thing"]["answer"] == word and 
        #         spellingBee["submissions"][userID]["thing"]["answer"][0] == todaysLetter_lower ):

        #         spellingBee["submissions"][userID]["thing"]["correct"] = 1
        #         spellingBee["submissions"][userID]["thing"]["colour"] = "#648f2380"


        #     if( spellingBee["submissions"][userID]["animal"]["answer"] == word and 
        #         spellingBee["submissions"][userID]["animal"]["answer"][0] == todaysLetter_lower ):
                
        #         spellingBee["submissions"][userID]["animal"]["correct"] = 1
        #         spellingBee["submissions"][userID]["animal"]["colour"] = "#648f2380"


        #     if( spellingBee["submissions"][userID]["male"]["answer"] == word and 
        #         spellingBee["submissions"][userID]["male"]["answer"][0] == todaysLetter_lower ):

        #         spellingBee["submissions"][userID]["male"]["correct"] = 1
        #         spellingBee["submissions"][userID]["male"]["colour"] = "#648f2380"


        #     if( spellingBee["submissions"][userID]["female"]["answer"] == word and 
        #         spellingBee["submissions"][userID]["female"]["answer"][0] == todaysLetter_lower ):

        #         spellingBee["submissions"][userID]["female"]["correct"] = 1
        #         spellingBee["submissions"][userID]["female"]["colour"] = "#648f2380"

        spellingBee["submissions"][userID]["end"] = datetime.now().strftime(DATETIME_LONG)
        #cellColour = "greenyellow","tomato"
        with open(SPELLING_BEE_BANK,"w") as f:
            json.dump(spellingBee,f,indent=4)
        usersDB[userID]["voted"]["sidequest"] = 1
        with open(USERS_DB,"w") as f:
            json.dump(usersDB,f,indent=4)
        return redirect(url_for('namizu.spellingBeeScoreBoard'))
    
@bp.route('/spellingbee/scoreboard', methods=['GET','POST'])
def spellingBeeScoreBoard():
    userID = session['userID']
    with open(SPELLING_BEE_BANK,"r") as f:
        all_submissions = json.load(f)
    #darkseagreen
    theme = queryThemeDayMode(datetime.now().hour)
    commenstData = getTodayComments()
    if request.method == "GET":
        pass
    elif request.method == "POST":
        # Save comment (e.g., to database or session)
        comment_text = request.form.get('comment_text')
        current_date = datetime.now().strftime(DATETIME_LONG)
        commenstData["miniGame"][current_date] = {
            "userID": userID,
            "text":comment_text,
            "username":usernameByID(userID)
        }        
        with open(COMMENTS_CACHE, 'w') as f:
            json.dump(commenstData, f, indent=4)
        return redirect(url_for('namizu.spellingBeeScoreBoard'))
    ## implement scoring system - check if a user entered a unique word
    return render_template('namizu/spellingBeeScoreBoard.html', all_submissions=all_submissions, theme=theme,comments=commenstData)

@bp.route("/sidequest", methods=['GET', 'POST'])
def sideQuestApp():
    return 0
    
@bp.route("/funnybanner", methods=["GET","POST"])
def funnyBannerApp():
    updateSessionCookie("funnyBannerApp")
    bannerTexts = {}
    # max char len: 40
    if request.method == "GET":
        theme = queryThemeDayMode(datetime.now().hour)
        return render_template('namizu/funnyBannerPage.html', theme=theme)
    elif request.method == "POST":
        bannerText = request.form.get("bannertext")
        # check text for links
        if( "www" in bannerText or ".com" in bannerText or 
           bannerText == ""):
            return redirect(url_for('namizu.funnyBannerApp'))
        with open(FUNNY_BANNERS_BANK,"r") as f:
            bannerTexts = json.load(f)
        bannerTexts[f"B{len(bannerTexts)+1}"] = bannerText
        with open(FUNNY_BANNERS_BANK,"w") as f:
            json.dump(bannerTexts,f,indent=4)
        return redirect(url_for('namizu.landingPage'))

@bp.route("/drawing/canvas")    
def drawingApp():
    updateSessionCookie("drawingApp")
    return render_template("namizu/drawing_canvas.html")    

@bp.route("/drawing/save", methods=['GET', 'POST'])
def drawing_save():
    image_data = ""
    image_title = ""
    image_descr = ""
    image_author = ""
    image_date = ""
    directory_path = "uploads"
    if request.method == "POST":
        image_data = request.form.get('imageData')
        image_title = request.form.get('title')
        image_descr = request.form.get('descr')
        image_author = usernameByID(session["userID"])
        image_date = "2025" #datetime.now().strftime("%Y") #! hardcoded date
    if image_data:
        # Decode the base64 image
        header, encoded = image_data.split(',', 1)
        image_data = base64.b64decode(encoded)
        try:
            # List all entries in the directory
            entries = os.listdir(directory_path)    
            # Count files only
            file_count = sum(1 for entry in entries if os.path.isfile(os.path.join(directory_path, entry)))
            filename = file_count+1
        except FileNotFoundError:
            print(f"The directory '{directory_path}' does not exist.")
            return 1
        except PermissionError:
            print(f"Permission denied to access the directory '{directory_path}'.")
            return 2
        file_path = os.path.join(directory_path, f'drawing_{filename}.png')
        with open(file_path, 'wb') as f: f.write(image_data)
        with open(f"database/drawings.json", 'r') as f:
            imageJson =  json.load(f)        
        full_filename = f"drawing_{filename}.png"
        imageJson[full_filename] = {}
        imageJson[full_filename]['filename'] = full_filename
        imageJson[full_filename]['author'] = image_author
        imageJson[full_filename]['title'] = image_title
        if image_title == "":
            imageJson[full_filename]['title'] = "Untitled"
        imageJson[full_filename]['date'] = image_date
        imageJson[full_filename]['descr'] = image_descr
        imageJson[full_filename]['submitted'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open(f"database/drawings.json", 'w') as f:
            json.dump(imageJson, f, indent=4)  

        print(f"Image saved")
        return redirect(url_for('namizu.landingPage'))
    return "No image data received!", 400

@bp.route("/gallery/welcome", methods=['GET'])
def gallery_welcome():
    updateSessionCookie("gallery_welcome")
    userID = session['userID']
    userName = usernameByID(userID)
    drawing_sum = len(os.listdir("uploads"))
    drawings = {}
    with open(f"database/drawings.json", 'r') as f:
        drawings =  json.load(f)        
    authors = {item["author"] for item in drawings.values()}
    authors_names = ', '.join(authors)
    if request.method == "GET":
        return render_template("namizu/gallery_welcome.html", drawing_sum=drawing_sum, name=userName, authors=authors_names)

@bp.route("/gallery/lift")
def gallery_lift():
    updateSessionCookie("gallery_lift")
    flash_message = "Select Floor"
    #! buttons hardcoded
    with open(f"database/drawings.json", 'r') as f:
        drawings =  json.load(f)        
    buttons = []
    buttons.append({"day":"X","month":"HOME"})
    date_saved = []
    for drawing_id,details in drawings.items():
        temp_date = {}
        date_obj = datetime.strptime(details["submitted"], "%d/%m/%Y %H:%M:%S")
        if (date_obj.day.__str__()+"-"+date_obj.month.__str__()) not in date_saved:    
            temp_date = {"day":date_obj.day,"month":date_obj.strftime("%b").upper()}
            date_saved.append(date_obj.day.__str__()+"-"+date_obj.month.__str__())
            if datetime.today().day == date_obj.day and datetime.today().month == date_obj.month:
                # is today
                temp_date["today"] = True
            buttons.append(temp_date)
    
    session.pop('_flashes', None)
    return render_template("namizu/gallery_lift.html", buttons=buttons)

@bp.route('/uploads/<filename>')
def serve_uploads(filename):
    return send_from_directory("../uploads", filename)

@bp.route("/gallery/<target_date>")
def gallery_day(target_date):
    updateSessionCookie("gallery_day")
    directory_path = "uploads"
    date_found = False
    drawings_dir = os.listdir(directory_path)
    with open(f"database/drawings.json", 'r') as f:
        art_db = json.load(f)        
    target_day_n_month = target_date.split("-")
    date_str = f"{target_day_n_month[0]} {target_day_n_month[1]} 2025" #! hardcoded year
    date_obj = datetime.strptime(date_str, "%d %b %Y")
    
    screenshots = []
    for filename, details in art_db.items():
        submit_date = datetime.strptime(details["submitted"], "%d/%m/%Y %H:%M:%S")
        if filename not in art_db:
            print("missing drawing. abort import.")
            break
        if submit_date.day == datetime.now().day and submit_date.month == datetime.now().month:
            date_found = True
            screenshot = {}
            screenshot["filename"] = filename
            screenshot["author"] = art_db[filename]["author"]
            screenshot["title"] = art_db[filename]["title"]
            screenshot["date"] = art_db[filename]["date"]
            screenshot["descr"] = art_db[filename]["descr"]
            screenshots.append(screenshot)
    
    if not date_found:
        session.pop('_flashes', None)
        flash(f"Floor {date_obj.day} {date_obj.strftime('%b')} is empty")
        return redirect(url_for('namizu.gallery_lift'))
    return render_template("namizu/gallery_swiper.html", screenshots=screenshots)


@bp.route("/admin")
def adminApp():
    updateSessionCookie("adminApp")
    userID = session['userID']
    with open("database/visit_count.json") as f:
        visit_count = json.load(f)
    visitCount = visit_count["total"]
    user_db = getUsersDatabase()
    funnyBanners={}
    with open(FUNNY_BANNERS_BANK,"r") as f:
        funnyBanners = json.load(f)

    historyData = {}
    with open("database/history.json","r") as f:
        historyData = json.load(f)
    if(user_db[userID]["admin"]!=1):
        current_app.logger.error("Unauthorised user - not admin.")
        return redirect(url_for('namizu.landingPage'))
    activeUsers = []
    usersCompletedDailyPoll = []
    loggedinUsers = []
    for uid,details in user_db.items():
        last_active_time = datetime.strptime(details["lastactive"], "%Y-%m-%d %H:%M:%S")
        if( datetime.now() - last_active_time < timedelta(minutes=1) ):
            activeUsers.append(details["uname"])
        if( details["loggedin"] == 1 ):
            loggedinUsers.append(details["uname"])
        if( details["voted"]["dailyPoll"] == 1):
            usersCompletedDailyPoll.append(details["uname"])
    with open(EVENTS_BANK, 'r') as f:
        events = json.load(f)
    allEventsCount = len(events)
    bannersCount = len(funnyBanners)
    historyCount = len(historyData)
    unusedEventsCount = np.sum([event["Status"] == 0 for event in events.values()])
    return render_template('namizu/adminPage.html', 
                           visitCount=visitCount,activeUsers=', '.join(activeUsers),
                           loggedinUsers=', '.join(loggedinUsers),bannersCount=bannersCount,
                           historyCount=historyCount,usersCompletedDailyPoll=', '.join(usersCompletedDailyPoll),
                           allEventsCount=allEventsCount,unusedEventsCount=unusedEventsCount)

    # dailyPoll completed
    # sideQuest completed

@bp.route("/admin/eventslist")
def eventsList():
    updateSessionCookie("eventsList")
    events = getEventsBank()
    return render_template('namizu/eventsbankPage.html', events=events)

@bp.route("/admin/historyList")
def historyList():
    updateSessionCookie("historyList")
    historyData = {}
    with open("database/history.json","r") as f:
        historyData = json.load(f)
    return render_template('namizu/historyBankPage.html', historyData=historyData)

@bp.route("/admin/bannerslist")
def bannersList():
    updateSessionCookie("bannersList")
    with open(FUNNY_BANNERS_BANK,"r") as f:
        banners = json.load(f)
    return render_template('namizu/bannerMessageBankPage.html', bannerMessages=banners)

@bp.route("/admin/resetday")
def resetDayCommand():
    resetDay()
    return redirect(url_for('namizu.adminApp'))

def resetDay():
    current_app.logger.info(f"Reset initiated")

    ## SAVE history

    eventsBank = getEventsBank()
    dailyPollData = getDailyPoll()
    commentsData = getTodayComments()
    usersData = getUsersDatabase()
    comments_packet = {}
    yesterday = datetime.now() - timedelta(days=1)
    yesterdayDate = yesterday.strftime(DATE_SHORT)
    if(dailyPollData and "dailyPoll" in commentsData):
        for timestamp, details in commentsData["dailyPoll"].items():
            comments_packet[timestamp] = {} 
            comments_packet[timestamp]["UID"] = details["userID"]
            comments_packet[timestamp]["message"] = details["text"]

        historyData = {
            "DailyPoll": {
                "Type": dailyPollData["Type"],
                "Question": dailyPollData["Question"],
                "Options": dailyPollData["Options"],
                "Answers": dailyPollData["Answers"],
                "Pollster": dailyPollData["Pollster"],
                "Theme": dailyPollData["Theme"],
                "Comments": comments_packet
            }
        }
        
        with open("database/history.json","r") as f:
            historyAll = json.load(f)
        if(yesterdayDate not in historyAll):
            historyAll[yesterdayDate] = historyData
        else:
            print("History log already exists for this date.")
        
        with open("database/history.json","w") as f:
            json.dump(historyAll,f,indent=4)
    current_app.logger.info(f"DAILY_RESET: History saved")

    ## CHANGE streak according to events
    
    for uid, details in usersData.items():
        if details["voted"]["dailyPoll"] == 1:
            usersData[uid]["streak"] += 1
        elif details["voted"]["dailyPoll"] == 0:
            usersData[uid]["streak"] = 0

        # reset votes
        usersData[uid]["voted"]["dailyPoll"] = 0
        usersData[uid]["voted"]["story"] = 0
        usersData[uid]["voted"]["sidequest"] = 0
        usersData[uid]["theme"] = "default_day"

    with open(USERS_DB,"w") as f:
        json.dump(usersData,f,indent=4)

    current_app.logger.info(f"DAILY_RESET: Users data saved")

    ## RESET comments

    with open(COMMENTS_CACHE,"w") as f:
        json.dump({"dailyPoll":{},"miniGame":{},"story":{}},f,indent=4)
    current_app.logger.info(f"DAILY_RESET: Comments cleaned")

    ## CHANGE main event - DailyPoll

    yesterdayPollID = ""
    for eid, details in eventsBank.items():
        if "dailypoll" in details["Type"]:
            if details["Status"] == 1:
                yesterdayPollID = eid
                break
    if(yesterdayPollID):
        eventsBank[yesterdayPollID]["Status"] = 2

    unusedPollIDs = [eid for eid,details in eventsBank.items() 
                     if details["Status"] == 0 and "dailypoll" in details["Type"]]

    if( len(unusedPollIDs) == 2 ):
        current_app.logger.error("1 dailypoll event left in bank")

    # select question randomly
    newPollID = random.choice(unusedPollIDs)
    # change
    eventsBank[newPollID]["Status"] = 1 # set for today's poll

    with open(EVENTS_BANK,"w") as f:
        json.dump(eventsBank,f,indent=4)

    with open('database/daily_poll.json', 'w') as f:
        json.dump(eventsBank[newPollID], f, indent=4)

    current_app.logger.info(f"DAILY_RESET: daily poll set")

    ## SideQuest

    # Get all lowercase letters
    alphabet = ["A","Á","B","C","D","E","É","F","G","H","I","J","K","L","M","N","O","P","R","S","T","U","Ü","V","Z"]
    # Select a random letter
    random.seed(datetime.now().day*datetime.now().month) # theoretically should play every letter within 60 days
    random_letter = random.choice(alphabet)
    spellingBeeBody = {
        "Datetime": datetime.now().strftime(DATE_SHORT),
        "letter": random_letter,
        "submissions": {}
    }

    with open("database/spelling_bee.json","w") as f:
        json.dump(spellingBeeBody,f,indent=4)

    current_app.logger.info(f"DAILY_RESET: sidequest set")

    ## secure GH backup

    ## set daily joke 

    dailyJokeStatus = querySideEventOccurance("dailyJoke")
    current_app.logger.info(f"{dailyJokeStatus = }")
    joke_data = {}
    if(dailyJokeStatus):
        # Set the headers to accept plain text response
        headers = {"Accept": "application/json"}
        # Perform the GET request to the dad joke API
        response = requests.get("https://icanhazdadjoke.com/", headers=headers)
        joke_data = response.json()
    else:
        joke_data = {"joke":"NONE"}
    with open("database/daily_joke.json","w") as f:
        json.dump(joke_data,f,indent=4)

    current_app.logger.info(f"DAILY_RESET: daily joke set")

    # check for sidequest    

## ARCHIVED APPS

@bp.route("/sketcher/canvas")
def oldSketcherApp():
    updateSessionCookie("oldSketcherApp")
    return render_template("namizu/sketcher_canvas.html")

@bp.route("/sketcher/save", methods=['GET', 'POST'])
def sketcher_save():
    image_data = ""
    image_title = ""
    image_descr = ""
    image_author = ""
    image_date = ""
    directory_path = "uploads"
    if request.method == "POST":
        image_data = request.form.get('imageData')
        image_title = request.form.get('title')
        image_descr = request.form.get('descr')
        image_author = session["user"]
        image_date = "2025" #datetime.now().strftime("%Y") #! hardcoded date
    if image_data:
        # Decode the base64 image
        header, encoded = image_data.split(',', 1)
        image_data = base64.b64decode(encoded)

        #success = save_drawing(directory_path,image_data,image_author,image_title,image_date,image_descr)
        #if success == 0:
         #   print(f"Image saved")
        return redirect(url_for('namizu.index'))
    return "No image data received!", 400
