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
    single multichoice anonym public
    ranking theme themeDescr names
    range yesorno openended prompt teams
    """
    qTypeDescr = {}
    flags = qTypeRaw.split(",")

    if "single" in flags:
        qTypeDescr["single"] = True
        qTypeDescr["multichoice"] = False
    else:
        qTypeDescr["single"] = False
        qTypeDescr["multichoice"] = True

    if "anonym" in flags:
        qTypeDescr["anonym"] = True
        qTypeDescr["public"] = False
    else:
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

#* LANDING PAGE

@bp.route("/landingpage")
@bp.route("/")
def landingPage():
    loggedin = True
    banner = "NaMizu"
    userName = check_user_logged_in("landingPage")
    notices = ["notice 1","notice 2"]
    storyStatus = False
    sideQuestStatus = False
    footerText = "2025 naMizu. Version 3.0 alpha (1481dfb), Built with care for the community."
    activeUsers = 3
    renderPacket = {}
    return render_template('/namizu/landingPage.html', 
                           banner=banner, notices=notices, 
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
            "mintext":"18 yrs",
            "maxtext":"33 yrs",
            "minvalue":18,
            "maxvalue":33,
        },
        "Answers": {
            "VID1": 22,
            "VID2": 25,
            "VID3": 19,
            "VID4": 33,
        },
        "Status": 0
    }

    dailyPollMulti = {
        "Type": "multichoice,names,public",
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
            "VID1": 22,
            "VID2": 25,
            "VID3": 19,
            "VID4": 33,
        },
        "Status": 0
    }

    dailyPollSingle = {
        "Type": "single,names,private",
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
            "VID1": 22,
            "VID2": 25,
            "VID3": 19,
            "VID4": 33,
        },
        "Status": 0
    }

    dailyPollRank = {
        "Type": "single,ranking,private",
        "Theme": "1",
        "Question": "Which would you eat the most?",
        "Pollster": "Lajos",
        "Options": {
            "o1":"Banana",
            "o2":"Garlic",
            "o3":"Cheese cake",
            "o4":"Cheddar cheese",
        },
        "Answers": {
            "VID1": "o2,o1,o4,o3",
            "VID2": "o4,o2,o1,o3",
            "VID3": "o1,o2,o4,o3",
            "VID4": "o3,o2,o1,o4",
        },
        "Status": 0
    }

    dailyPollPrompt = {
        "Type": "single,prompt,public",
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

    dailyPoll = dailyPollPrompt#dailyPollRank#dailyPollSingle#dailyPollMulti#dailyPollRange
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
    votersStats = dailyPoll["Answers"]
    kudosMessage = "Grats!"
    comments = ""
    version = "3.0"

    if request.method == 'GET':    
        pass        

    elif request.method == 'POST':
        pass

    return render_template('namizu/dailyPollPage.html', 
                           banner=banner,qTypeDescr=qTypeDescr,
                           theme=theme, optionsBody=optionsBody,
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
    return 0
    alreadyLoggedIn, userName = check_user_logged_in("editor")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))
    session.pop('_flashes', None)
    # define variables
    question = ""
    answers = []
    options = []
    qid = 0
    new_question_body = {}
    temp_q = {}
    names = get_user_names()
    submitPoll = False
    do_restart = False
    submitPoll = False
    select_mode = ""
    option_mode = ""

    ### V / D
    variable_in_question = False 
    multichoice = False #
    names_as_options = False
    custom_as_options = False
    yes_or_no = False
    showdown = False
    selected_names_1v1 = []

    # question types:

    # Variable in question: V
    # No variable in question: D

    # Single choice: S
    # Multichoice: M

    # Names as options: N
    #   put X at the end
    # Custom options as options: C
    #   Yes or no answers: Y
    #   Open-ended answers: O
    # 1v1 Showdown: F (fight)
    #   put X at the end

    # type examples: DMNX, VSFX

    #* restart if M and CY in type
    #* restart if M and F in type

    poll_type = ""

    if request.method == "GET":
        pass
    
    if request.method == "POST":
        print(f"{request.form = }")
        question = request.form["question"]
        if "{" in question and "}" in question:
            variable_in_question = True
        select_mode = request.form['radio-selection']
        if select_mode == "multiple":
            multichoice = True
        option_mode = request.form['radio-options']
        if option_mode == "names":
            names_as_options = True
        elif option_mode == "showdown":
            showdown = True
        elif option_mode == "options":
            custom_as_options = True
        answers = []   
        if names_as_options:
            answers = names
        elif custom_as_options:
            for key, val in request.form.items():
                if key.startswith("answer"):
                    answers.append(val)
        if custom_as_options:
            if "yes" in [a.lower() for a in answers] or "no" in [a.lower() for a in answers]:
                yes_or_no = True

        poll_type = ""
        poll_type += "V" if variable_in_question else "D"
        poll_type += "M" if multichoice else "S"
        if names_as_options:
            poll_type += "N"
        elif custom_as_options:
            poll_type += "C"
        elif showdown:
            poll_type += "F"

        if custom_as_options:
            if yes_or_no:
                poll_type += "Y"
            else:
                poll_type += "O"
        else:
            poll_type += "X" # names and 1v1, therefore yes or no is irrelevant
     
        if variable_in_question:
                
            text = question
            number_of_variables = text.count("{")
            number_of_variables_check = text.count("}")
            if number_of_variables!=number_of_variables_check:
                do_restart = True
                flash("Typo in random name {P}")
                # Names to replace
            selected_names = random.sample(names, number_of_variables)
            selected_names_1v1 = selected_names.copy()
                # Replace placeholders sequentially
            result = re.sub(r"{P}", lambda _: selected_names.pop(0), text)
            question = result           
            if showdown:
                answers = selected_names_1v1
            
        if custom_as_options:
            options = answers
            for option in options:
                if option == "":
                    do_restart = True
                    flash("Some options are empty. Session restarted")
        
        if multichoice and yes_or_no:
            do_restart = True
            flash("Cannot be YesOrNo and Multichoice at the same time. Session restarted")

        if multichoice and showdown:
            do_restart = True
            flash("Cannot be 1v1 and Multichoice at the same time. Session restarted")

        if question == "":
            do_restart = True
            flash("No question included. Session restarted")

        if not answers:
            do_restart = True
            flash("No answers included. Session restarted")
        
        answers = {key:0 for key in answers}

        submitPoll = True

        #* exclude
        qid = get_new_question_id()
        qid = "Q"+str(qid)
        new_question_body = {
            "Type": poll_type,
            "Question": question,
            "Answers": answers,
            "Status": 0
        }
        temp_q[qid] = new_question_body

    # add final check before submit question:
    # if exact question, exact type and exact answers exist, then do_restart

    questions_bank = load_question_bank()
    for details in questions_bank.values():
        if details["Question"] == question and details["Answers"] == answers and details["Type"] == poll_type:
            do_restart = True
            flash("Poll already exists. Session restarted.")
            break
    
    if submitPoll:
        if not do_restart:
            for k,v in temp_q.items():
                save_new_question(k,v)
                break
            flash("Submitted successfully.")

    return render_template('namizu/editor.html', namesList=names)


@bp.route("/sketcher/canvas")
def sketcherApp():
    return 0

@bp.route("/gallery/welcome")
def galleryApp():
    return 0