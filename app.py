from cs50 import SQL
import sqlite3
import glob
import os
import warnings
import textract
import requests
from flask import (Flask,session, g, json, Blueprint,flash, jsonify, redirect, render_template, request,
                   url_for, send_from_directory)
from gensim.summarization import summarize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from werkzeug import secure_filename
from urllib.request import urlopen
import json
import pdf2txt as pdf
import PyPDF2

import screen
import search
import hashlib
from machine import run

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

app = Flask(__name__)

app.config.from_object(__name__) # load config from this file , flaskr.py
username="arunima811"

# Load default config and override config from an environment variable
app.config.update(dict(
    USERNAME='admin',
    PASSWORD='7b4d7a208a333b46acdc9da159e5be7a',
    SECRET_KEY='development key',
))


app.config['UPLOAD_FOLDER'] = 'Original_Resumes/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

class jd:
    def __init__(self, name):
        self.name = name

def getfilepath(loc):
    temp = str(loc).split('\\')
    return temp[-1]
    



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif app.config['PASSWORD'] != hashlib.md5(request.form['password'].encode('utf-8')).hexdigest():
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))


@app.route('/')
def home():
    x = []
    for f in glob.glob("./Job_Description/*.txt"):
        file=f[18:]
        res = jd(file)
        x.append(jd(getfilepath(file)))
    print(x)
    return render_template('index.html', results = x)




@app.route('/results', methods=['GET', 'POST'])
def res():
    if request.method == 'POST':
        jobfile = request.form['des']
        print(jobfile)
        return_flask_name = screen.res(jobfile)
        flask_return=return_flask_name[0]
        name_string=return_flask_name[1]
        linked_in=return_flask_name[2]
        major_list=zip(flask_return,name_string,linked_in)
        print(flask_return)
        return render_template('result.html', results=major_list)



@app.route('/resultscreen' ,  methods = ['POST', 'GET'])
def resultscreen():
    if request.method == 'POST':
        jobfile = request.form.get('Name')
        print(jobfile)
        flask_return = screen.res(jobfile)
        return render_template('result.html', results = flask_return)



@app.route('/resultsearch' ,methods = ['POST', 'GET'])
def resultsearch():
    if request.method == 'POST':
        search_st = request.form.get('Name')
        print(search_st)
    return_flask_name = search.res(search_st)
    flask_return=return_flask_name[0]
    name_string=return_flask_name[1]
    linked_in=return_flask_name[2]
    major_list=zip(flask_return,name_string,linked_in)
    print(flask_return)
    return render_template('result.html', results=major_list)
    # return result

@app.route('/last_function', methods = ['POST', 'GET'])
def git_function():
    if request.method=='GET':
        url = "https://api.github.com/users/"+username
        data = json.load(urlopen(url))
        tot_info={}
        tot_info["BASIC INFO"]=""
        tot_info ["GIT ID  "]=data.get("id")   
        tot_info ["NAME   "]=data.get("name")  
        tot_info ["COMPANY   "]=data.get("company")  
        tot_info ["LOCATION  "]=data.get("location") 
        tot_info ["EMAIL   "]=data.get("email")  
        tot_info ["BIO    "]=data.get("bio")
        tot_info ["FOLLOWERS    "]=data.get("followers")   
        tot_info ["FOLLOWLING   "]=data.get("following")
        tot_info ["CREATED AT   "]=data.get("created_at")  
        tot_info ["LAST UPDATED AT   "]=data.get("updated_at")
        tot_info ["NO OF PUBLIC REPO    "]=data.get("public_repos")
        tot_info["NUMBER OF PUBLIC GIST    "]=data.get("public_gists") 
 

        print('-----------------------------------------------------')
        url = "https://api.github.com/users/"+username+"/repos"
        tot_info["All repos/projects"]=""
        data = json.load(urlopen(url))
        count=0
        for item in data:
             print('***')
             tot_info['REPO NAME ',count]=item.get("full_name")
             tot_info["DESCRIPTION  ",count]=item.get('description')
             tot_info["CREATED AT ",count]=item.get("created_at")  
             tot_info["LAST UPDATED AT  ",count]=item.get("updated_at")
             tot_info["PUSHED AT   ",count]=item.get("pushed_at")
             tot_info["SIZE ",count]=item.get("size")
             tot_info["LANGUAGE ",count]=item.get("language")
             tot_info["LINK OF REPO ",count]= "https://github.com/"+item.get("full_name") 
             count+=1
 



        print('-----------------------------------------------------')
        url = "https://api.github.com/users/"+username+"/followers"
        data = json.load(urlopen(url))
        tot_info["FOLLOWERS"]=""
        c=0
        for item in data:
            temp=item.get("login")
            tot_info["User Name ",c]=temp
            tot_info["User name link ",c]="github link: https://github.com/"+temp
            c+=1
     
        print('-----------------------------------------------------')
        url = "https://api.github.com/users/"+username+"/following"
        data = json.load(urlopen(url))
        tot_info["FOLLOWING"]=""
        c=0
        for item in data:
            temp=item.get("login")
            tot_info["User Name ",c]=temp
            tot_info["User name link ",c]="github link: https://github.com/"+temp
            c+=1

        print('-----------------------------------------------------')
    return render_template('result1.html', tot_info=tot_info)



@app.route('/Original_Resume/<path:filename>')
def custom_static(filename):
    return send_from_directory('./Original_Resumes', filename)


@app.route("/attrition")

def attrition():
    conn = sqlite3.connect("dataset.db")
    cur = conn.execute("SELECT * FROM dataset")
    data = cur.fetchall()
    att, skills = run(data)
    #print(">>>>>>>>>>>>>>Attrition>>>>>>>>>>>>>>>>")
    #print(att)
    newd = []
    i=0
    for row in range(len(att)):
        t = ()
        t = t + (i,)
        t = t + (att[row],)
        t = t + (skills[row],)
        i = i+1
        newd.append(t)
    return render_template("attrition.html", data=newd)

@app.route("/graph")
def graph():
    return render_template("graph.html")

if __name__ == '__main__':
   # app.run(debug = True) 
    # app.run('127.0.0.1' , 5000 , debug=True)
    app.run('0.0.0.0' , 5000 , debug=True , threaded=True)
    
