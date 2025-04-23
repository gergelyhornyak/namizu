from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import random, json, re, string
import numpy as np

bp = Blueprint('namizu', __name__, template_folder='templates')

EVENTS_BANK = "database/events_bank.json"
USERS_DB = "database/users_db.json"
COMMENTS_CACHE = "database/comments.json"
SPELLING_BEE_BANK = "database/spelling_bee.json"
DAILY_POLL_CACHE = "database/daily_poll.json"
FUNNY_BANNERS_BANK = "database/funny_banners.json"
THEMES_BANK = "database/themes.json"

# session: userID,lastURL

#* ERROR HANDLING

@bp.errorhandler(404)
def page_not_found404(e):
    return "ERROR 404", 404

@bp.errorhandler(500)
def page_not_found500(e):
    return "ERROR 500", 500

@bp.errorhandler(400)
def page_not_found400(e):
    return "ERROR 400", 400

#* SMALL FUNCTIONS

def updateSessionCookie(path:str):
    if "userID" in session:
        session['url'] = path
        session['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(USERS_DB, 'r') as f:
            users_db = json.load(f)
        users_db[session["userID"]]["lastactive"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(USERS_DB, 'w') as f:
            json.dump(users_db,f,indent=4)

    else:
        print("userID missing, pls login")
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

def prettyPrintJson(jsonFile:dict) -> None:
    json_formatted_str = json.dumps(jsonFile, indent=4)
    print(json_formatted_str)

def findByID(uid:str) -> str:
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

def queryThemeDayMode(hour)->dict:
    themes = {}
    try:
        with open(THEMES_BANK, 'r') as f:
            themes = json.load(f)
    except Exception as e:
        print(e)
    if(hour > 18 or hour < 7):
        return themes["default_night"]
    else:
        return themes["default_day"]    

def getTodayComments() -> dict:
    try:
        with open(COMMENTS_CACHE, 'r') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return {}    
    except Exception as e:
        print(e)

#* PAGEs and APPs

@bp.route('/login', methods=['GET', 'POST'])
def loginPage():  
    wrongPasswCounter = 0
    theme = queryThemeDayMode(datetime.now().hour)
    footerText = "naMizu 2025. Version 3.X"
    userData = {}
    with open(USERS_DB, 'r') as f:
        userData = json.load(f)

    if request.method == "POST":
        uid = request.form["uid"]
        passw = request.form["password"]
        if( userData[uid]["passw"] == passw):
            print(f"Successful authentication. Welcome {userData[uid]['uname']}!")
            session["userID"] = uid
            session.modified = True
            session.permanent = True
            userData[uid]["loggedin"] = 1
            userData[uid]["lastlogin"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            
    return render_template('namizu/loginPage.html',userDataPacket=userData, theme=theme, footerText=footerText)

@bp.route("/landingpage")
@bp.route("/index")
@bp.route("/")
def landingPage():
    updateSessionCookie("landingPage")
    userID = ""
    if "userID" in session: userID = session["userID"]    
    else: return redirect(url_for(f"namizu.loginPage")) # prompt for login

    # log user activity

    user_db = {}#loadAllUserInfo()
    with open(USERS_DB, 'r') as f:
        user_db = json.load(f)
    activeUsers = []
    #user_db[userID]["lastactive"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for uid,details in user_db.items():
        last_active_time = datetime.strptime(details["lastactive"], "%Y-%m-%d %H:%M:%S")
        if( datetime.now() - last_active_time < timedelta(minutes=1) ):
            activeUsers.append(details["shortname"])
    
    showDailyJoke = False
    dailyJoke = ""
    primeNumbers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    if ( datetime.now().day in primeNumbers ):
        showDailyJoke = True
        # Set the headers to accept plain text response
        headers = {"Accept": "text/plain"}
        # Perform the GET request to the dad joke API
        #response = requests.get("https://icanhazdadjoke.com/", headers=headers)
        # Store the joke text
        dailyJoke = "DAILY_JOKE"#response.text
    
    banner = "NaMizu"
    userName = findByID(userID)
    notices = ["notice 1","notice 2"] #queryNotices
    storyStatus = False # queryStory
    sideQuestStatus = False # querySideQ
    footerText = "2025 naMizu. Version 3.0 alpha (1535c0d), Built with care for the community."
    
    funnyMessages = {}
    with open(FUNNY_BANNERS_BANK, 'r') as f:
        funnyMessages = json.load(f)
    random.seed(datetime.now().day)
    number = random.randint(1, len(funnyMessages))
    
    funnyMessage = funnyMessages[f"B{str(number)}"]
    #funnyMessage = "I Solemnly Swear I’m Up to Polling Good"
    theme = queryThemeDayMode(datetime.now().hour)
    renderPacket = {}
    return render_template('/namizu/landingPage.html', 
                           banner=banner, notices=notices, funnyMessage=funnyMessage,
                           userName=userName, sideQuestStatus=sideQuestStatus,
                           activeUsers=activeUsers, footerText=footerText,
                           dailyJoke=dailyJoke, theme=theme)

@bp.route('/logout')
def logout():
    # set user to loggedout
    with open(USERS_DB, 'r') as f:
        users_db = json.load(f)
    users_db[session['userID']]["loggedin"] = 0
    with open(USERS_DB, 'w') as f:
        json.dump(users_db,f,indent=4)
    print(users_db[session['userID']]["uname"],"logged out.\n")
    session.clear()
    return redirect(url_for("namizu.landingPage"),302)

@bp.route("/dailypoll", methods=['GET', 'POST'])
def dailyPollApp():
    
    updateSessionCookie("dailyPollApp")
    userID = session['userID']

    pollSubmitted = False   
    with open(USERS_DB, 'r') as f:
        users_db = json.load(f)
    if(users_db[userID]["voted"]["dailyPoll"] == 1): # true
        pollSubmitted = True

    with open(DAILY_POLL_CACHE, 'r') as f:
        dailyPoll = json.load(f)
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
        "voterSum":7
    }
    answersProcessed = {}
    rankingProcessed = {}
    romanNumbers = []
    sidesProcessed = {}
    answersList = []
    answersValue = None
    
    
    banner = ""
    kudosMessage = "Grats!"
    footerText = "© 2025 naMizu™. Version 3.X . Built with care for the community."

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
                users_db[userID]["streak"] += 1
                # also increase their streak
                with open(USERS_DB, 'w') as f:
                    json.dump(users_db,f,indent=4)     

                # add new answer to today poll
                dailyPoll["Answers"] = answersBody
                with open(DAILY_POLL_CACHE, 'w') as f:
                    json.dump(dailyPoll,f,indent=4)              
                return redirect(url_for('namizu.dailyPollApp'))

        else:
            if 'comment' in request.form:
                comment = request.form['comment']
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                appID = 1
                
                todayComments[current_date] = {
                    "userID": userID,
                    "appID": appID,
                    "text":comment,
                    "username":findByID(userID)
                }           
                with open(COMMENTS_CACHE, 'w') as f:
                    json.dump(todayComments, f, indent=4)
                return redirect(url_for('namizu.dailyPollApp'))
            
    
    if( qTypeDescr["range"] or 
        (qTypeDescr["singlechoice"] and qTypeDescr["names"]) or
        (qTypeDescr["singlechoice"] and qTypeDescr["openended"]) ):

        for uid, option in answersBody.items(): # option is a value
            if option not in answersProcessed:
                answersProcessed[option] = {}
                answersProcessed[option]["value"] = 1
                answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                answersProcessed[option]["voters"] = [users_db[uid]["shortname"]]
            else:
                answersProcessed[option]["value"] += 1
                answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                if(uid not in answersProcessed[option]["voters"]):
                    answersProcessed[option]["voters"].append(users_db[uid]["shortname"])

    elif(qTypeDescr["prompt"]):
        for uid, text in answersBody.items(): # option is a value
            answersProcessed[uid] = {
                "username":findByID(uid),
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
                "username": findByID(uid),
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
                    sidesProcessed[sideName]["voters"].append(findByID(uid))
    
    elif(qTypeDescr["yesorno"]):
        sidesProcessed["Yes"] = 0
        sidesProcessed["No"] = 0
        for uid, option in answersBody.items(): # options is a value
            if(option.lower()=="yes"):
                sidesProcessed["Yes"] += 1
            elif(option.lower()=="definitely"):
                sidesProcessed["Yes"] += 1*3 # yesornoMultiplier
            elif(option.lower()=="no"):
                sidesProcessed["No"] += 1
            elif(option.lower()=="never"):
                sidesProcessed["No"] += 1*3 # yesornoMultiplier

    elif( (qTypeDescr["multichoice"] and qTypeDescr["names"]) or
        (qTypeDescr["multichoice"] and qTypeDescr["openended"]) ):
        for uid, options in answersBody.items(): # option is a list
            for option in options:
                if option not in answersProcessed:
                    answersProcessed[option] = {}
                    answersProcessed[option]["value"] = 1
                    answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                    answersProcessed[option]["voters"] = [users_db[uid]["shortname"]]
                else:
                    answersProcessed[option]["value"] += 1
                    answersProcessed[option]["width"] = int(answersProcessed[option]["value"]/voterStat["voterSum"]*100)
                    if(uid not in answersProcessed[option]["voters"]):
                        answersProcessed[option]["voters"].append(users_db[uid]["shortname"])    

    return render_template('namizu/dailyPollPage.html', 
                           banner=banner,qTypeDescr=qTypeDescr,answersProcessed=answersProcessed,rankingProcessed=rankingProcessed,
                           theme=theme, optionsBody=optionsBody,voterStat=voterStat,kudosMessage=kudosMessage,
                           questionBody=questionBody, pollster=pollster, pollSubmitted=pollSubmitted,
                           footerText=footerText,todayComments=todayComments,roman=romanNumbers, sidesProcessed=sidesProcessed
                           )

@bp.route('/editor', methods=['GET', 'POST'])
def editorApp():
    updateSessionCookie("editorApp")
    users_db = {}
    with open(USERS_DB, 'r') as f:
        users_db = json.load(f)
    events_bank = {}
    namesList = [user["uname"] for user in users_db.values()]
    theme = queryThemeDayMode(datetime.now().hour)
    restartEditor = False
    
    userID = session['userID']
    
    pollBody = {
        "Type":"",
        "Options":{}
    }
    if request.method == "POST":
        session.pop('_flashes', None)

        pollBody["Question"] = request.form["question"]
        pollBody["Type"] = request.form["selectionType"] + "," + request.form["privacyType"] + "," + request.form["optionsType"]
        pollBody["Pollster"] = findByID(userID)
        pollBody["Theme"] = "default_day"
        pollBody["Status"] = 0
        pollBody["Answers"] = {}
        pollBody["Datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pollBody["Duedate"] = ""
        
        ## process Options

        if(request.form["optionsType"] == "prompt"):
            pollBody["Options"] = {"shape":"cloud"}
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

        if( "range" in pollBody["Type"] ):
            if( not pollBody["Options"]["maxvalue"].isdigit() ):
                restartEditor = True
                flash("Range must be a number. Session restarted")    

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
            flash("DailyPoll submitted successfully.")

        return redirect(url_for('namizu.editorApp'))
    
    return render_template('namizu/editorPage.html',namesList=namesList, theme=theme)

@bp.route("/sketcher/canvas")
def sketcherApp():
    return 0

@bp.route("/gallery/welcome")
def galleryApp():
    return 0

@bp.route("/calendar")
def calendarApp():
    return 0

## Funny Apps

@bp.route('/spellingbee',methods=['GET','POST'])
def spellingBeeApp():
    updateSessionCookie("spellingBeeApp")
    data = {}
    words = []
    cities = []
    spellingbee = {}
    if request.method == "GET":
        # Get all lowercase letters
        alphabet = string.ascii_uppercase
        # Select a random letter
        random_letter = random.choice(alphabet)
        return render_template('namizu/spellingBeePage.html', letter=random_letter)
    elif request.method == "POST":
        userID = session['userID']
        username = findByID(userID)
        data = {
            "uname": username,
            "country": {
                "answer":request.form.get("country").lower(),
                "correct":0,
                "colour":"transparent"
                },
            "city": {
                "answer": request.form.get("city").lower(),
                "correct":0,
                "colour":"transparent"
                },
            "thing": {
                "answer": request.form.get("thing").lower(),
                "correct":0,
                "colour":"transparent"
                },
            "animal": {
                "answer": request.form.get("animal").lower(),
                "correct":0,
                "colour":"transparent"
                },
            "male": {
                "answer": request.form.get("male").lower(),
                "correct":0,
                "colour":"transparent"
                },
            "female": {
                "answer": request.form.get("female").lower(),
                "correct":0,
                "colour":"transparent"
                }
            }
        with open("database/words.txt","r") as f:
            words = [line.strip().lower() for line in f if line.strip()]
        with open("database/cities.txt","r") as f:
            cities = [line.strip().lower() for line in f if line.strip()]

        for city in cities:
            if( data["city"]["answer"] == city ):
                data["city"]["correct"] = 1
                data["city"]["colour"] = "greenyellow"

        for word in words:
            if( data["country"]["answer"] == word ):
                data["country"]["correct"] = 1
                data["country"]["colour"] = "greenyellow"

            if( data["thing"]["answer"] == word ):
                data["thing"]["correct"] = 1
                data["thing"]["colour"] = "greenyellow"

            if( data["animal"]["answer"] == word ):
                data["animal"]["correct"] = 1
                data["animal"]["colour"] = "greenyellow"

            if( data["male"]["answer"] == word ):
                data["male"]["correct"] = 1
                data["male"]["colour"] = "greenyellow"

            if( data["female"]["answer"] == word ):
                data["female"]["correct"] = 1
                data["female"]["colour"] = "greenyellow"
            
        with open(SPELLING_BEE_BANK,"r") as f:
            spellingbee = json.load(f)
        spellingbee["submissions"][userID] = data
        #cellColour = "greenyellow","tomato"
        with open(SPELLING_BEE_BANK,"w") as f:
            json.dump(spellingbee,f,indent=4)
        return redirect(url_for('namizu.spellingBeeScoreBoard'))
    
@bp.route('/spellingbee/scoreboard', methods=['GET'])
def spellingBeeScoreBoard():
    with open(SPELLING_BEE_BANK,"r") as f:
        all_submissions = json.load(f)
    print(all_submissions)
    #darkseagreen
    ## implement scoring system - check if a user entered a unique word
    return render_template('namizu/spellingBeeScoreBoard.html', all_submissions=all_submissions)

@bp.route("/sidequest", methods=['GET', 'POST'])
def sideQuestApp():
    return 0
    
@bp.route("/funnybanner", methods=["GET","POST"])
def funnyBannerApp():
    updateSessionCookie("funnyBannerApp")
    bannerTexts = {}
    # max char len: 40
    if request.method == "GET":
        return render_template('namizu/funnyBannerPage.html')
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


@bp.route("/admin")
def adminApp():
    updateSessionCookie("adminApp")
    # visit count
    # active users
    # currently logged in
    # dailyPoll completed
    # sideQuest completed
    # all questions/events count
    # unused questions/events count
    # list of questions