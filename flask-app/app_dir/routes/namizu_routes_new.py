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
    ranking names
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

def prettyPrintJson(jsonFile:dict):
    json_formatted_str = json.dumps(jsonFile, indent=4)
    print(json_formatted_str)

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
        "Type": "single,names,anonym",
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
        "Type": "single,ranking,anonym",
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
            "VID1": ["o2","o1","o4","o3"],
            "VID2": ["o4","o2","o1","o3"],
            "VID3": ["o1","o2","o4","o3"],
            "VID4": ["o3","o2","o1","o4"],
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

    dailyPoll = dailyPollMulti#dailyPollPrompt#dailyPollRank#dailyPollSingle#dailyPollMulti#dailyPollRange
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

    if(qTypeDescr["multichoice"] or qTypeDescr["single"]):
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

    if(qTypeDescr["names"] or qTypeDescr["ranking"] or qTypeDescr["openended"]):
        pass
    
    prettyPrintJson(answersProcessed)

    kudosMessage = "Grats!"
    comments = {}
    version = "3.0"

    if request.method == 'GET':    
        pass        

    elif request.method == 'POST':
        pass

    return render_template('namizu/dailyPollPage.html', 
                           banner=banner,qTypeDescr=qTypeDescr,answersProcessed=answersProcessed,
                           theme=theme, optionsBody=optionsBody,voterStat=voterStat,kudosMessage=kudosMessage,
                           questionBody=questionBody, pollster=pollster, pollSubmitted=True
                           )


@bp.route("/sidequest", methods=['GET', 'POST'])
def sideQuestApp():
    return 0
    alreadyLoggedIn, userName = check_user_logged_in("sidequest")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))
    
@bp.route('/editor', methods=['GET', 'POST'])
def editorApp():

    

    return render_template('namizu/editor.html')


@bp.route("/sketcher/canvas")
def sketcherApp():
    return 0

@bp.route("/gallery/welcome")
def galleryApp():
    return 0