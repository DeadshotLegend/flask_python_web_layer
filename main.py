# used for making GET / POST / PUT / DELETE requests
import requests
# used for JSON handling
import json
# flask imports
from flask import render_template, request, redirect, url_for, session, make_response
# flask login manager
from flask_login import LoginManager
# import "packages" from "this" project
from __init__ import app, login_manager  # Definitions initialization

# not sure this is needed - to be tested
import threading

# URL of the DB layer - may need to externalize this in docker
rootUrl = "http://172.24.148.228:8343/api"

# catch for URL not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# index page
# there is an option to sign up or login or play game in guest mode
# if the user is logged in, the user's score is saved every time the game ends
# guest mode does not save the scores
@login_manager.user_loader
@app.route('/') 
def index():
    # ensure sessions are destroyed when browser is closed
    session.permanent = False 

    # check if the loginuser attribute is in session
    # its presence is a test of logged in user
    # this attribute is a JSON object that holds following data:
    # dob - user DOB
    # highscore - user's high score
    # id - id - primary key
    # level - difficulty level
    # message - last message (used for failed logins)
    # name - user's display name
    # uid - user's login id
    # valid - login valid (True | False)
    if 'loginuser' in session:
        loginuser = session["loginuser"]
        id = loginuser['id']
        user_scores_json = getUserScores(id)
        # render index.html wth user's last scores and loginuser object
        return render_template("index.html", user_json_object=loginuser, user_scores_json=user_scores_json)
    
    # if loginuser is not found in session look for user_json_object in request
    # this happens when login fails 
    if 'user_json_object' in request.args:
        user_data = request.args["user_json_object"]
        print(user_data.replace("'", '"').replace("False", '"False"'))
        if user_data != None:
            user_data = user_data.replace("'", '"').replace("False", '"False"')
            user_json_object = json.loads(user_data)
            # user_json_object.valid will be False when login has failed
            if not user_json_object["valid"]:
                loginmsg =  user_json_object["message"]
                render_template("index.html", loginmsg=loginmsg)
    
    # by default show the user the index page - which has the game in guest mode
    # plus as options to sign up 
    return render_template("index.html")

# get user scores
def getUserScores(userID):
    userScores = requests.get(rootUrl + "/scores?userID="+str(userID))
    print(userScores.text)
    user_scores_json = json.loads(userScores.text)
    return user_scores_json

# shows login dialog
# add username in session and routes to index page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # the method is POST - perform the login request
        username = request.form['username']
        password = request.form['password']
        url = rootUrl + '/gamers/login?uid='+username+'&password='+password
        userdetails = requests.get(url)
        print(userdetails.text)
        user_json_object = json.loads(userdetails.text)

        print(user_json_object["valid"])
        
        # if the login is successful populate the session attributes
        if (user_json_object["valid"]):
            session['username'] = username
            session['loginuser'] = user_json_object
            id = user_json_object['id']
            user_scores_json = getUserScores(id)
            return render_template('index.html', user_json_object=user_json_object, user_scores_json=user_scores_json)
        else:
            # login has failed - show the user the failure message
            loginmsg =  user_json_object["message"]
            return render_template('login.html', login_msg=loginmsg)

    # show the user the login dialog    
    return render_template('login.html')

# perform the admin login action - this is simiar to login method above
@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    # if the request method is POST - perform the authentication
    if request.method == 'POST':
        # perform authentication
        username = request.form['username']
        password = request.form['password']
        url = rootUrl + '/admin/login?uid='+username+'&password='+password
        adminUserDetails = requests.get(url)
        print(adminUserDetails.text)
        admin_user_json_object = json.loads(adminUserDetails.text)

        print(admin_user_json_object["valid"])
        
        if (admin_user_json_object["valid"]):
            # successful authentication
            #session['username'] = username
            session['adminuser'] = admin_user_json_object
            
            return redirect(url_for("user_admin"))
        else:
            # failed login
            loginmsg =  admin_user_json_object["message"]
            return render_template('login.html', login_msg=loginmsg)
    
    # show the login page    
    return render_template('login.html')

# performs logout
# clears the session
@app.route('/logout')
def logout():
    # remove the userfrom the session if it's there
    session.pop('username', None)
    session.pop('loginuser', None)
    session.pop('adminuser', None)
    return redirect(url_for('index'))

# shows user profile 
# shows user's scores
@app.route('/profile')
def profile():
    # fetch user profile data and render profile template
    loginuser = session["loginuser"]
    print(loginuser)
    id = loginuser['id']
    user_scores_json = getUserScores(id)
    msg = request.args.get("profile_message")
    return render_template("profile.html", user_json_object=loginuser, user_scores_json=user_scores_json, msg=msg)

# saves gamer's score
@app.route('/savescore', methods=['POST','OPTIONS'])
def save_score():
    score_data = request.get_json(force=True)
    score = score_data.get('score')
    uid = score_data.get('uid')
    url = rootUrl+"/scores/create"
    score_response = requests.post(url, json=score_data)
    print(score_response.text)
    print("Refreshing user score table")
    user_scores_json = getUserScores(uid)
    loginuser = session["loginuser"]
    
    # if its a new highscore, update the highscore in session
    if int(score) > int(loginuser["highscore"]):
        loginuser["highscore"] = score
        session["loginuser"] = loginuser
    return render_template("user-scores.html", user_scores_json=user_scores_json)

# User scores  populate the user scores table
@app.route('/user-scores')  
def user_scores():
    if 'loginuser' in session:
        loginuser = session["loginuser"]
        id = loginuser['id']
        user_scores_json = getUserScores(id)
        return render_template("user-scores.html", user_scores_json=user_scores_json)
    return render_template("user-scores.html")

# deletes a gamer scores
@app.route('/scores/delete')  
def delete_scores():
    if 'loginuser' in session:
        loginuser = session["loginuser"]
        userID = loginuser['id']
        print("Deleting scores")
        print(userID)
        url = rootUrl + '/scores/delete?userID='+str(userID)

        scoreDeletedResponse = requests.delete(url)
        print(scoreDeletedResponse.text)
        loginuser["highscore"] = 0
        session["loginuser"] = loginuser
        return redirect(url_for("index"))

# deletes a gamer account
@app.route('/gamers/delete')  
def delete_gamer():
    id = request.args.get('id')
    url = rootUrl + '/gamers/delete?id='+id
    print(id)
    print(request.args.get('name'))
    deleteGamerResults = requests.delete(url)
    print(deleteGamerResults.text)
    return redirect(url_for("user_admin"))

# creates a gamer account
@app.route('/gamers/create', methods=['POST'])  
def create_gamer():
    data = request.form.to_dict(flat=True)
    print(data)
    headers = {'Content-type': 'application/json'}
    url = rootUrl + '/gamers/create'
    userCreateResponse = requests.post(url, json=data, headers=headers)
    print (userCreateResponse.text)
    return redirect(url_for("login"))

# updates a gamer account
@app.route('/gamers/update', methods=['POST'])  
def update_gamer():
    print("update gamer. Request data: ")
    data = request.form.to_dict(flat=True)
    print(data)
    headers = {'Content-type': 'application/json'}
    url = rootUrl + '/gamers/update'
    updatedGamerData = requests.put(url, json=data, headers=headers)
    print("Update Gamer Response")
    print (updatedGamerData.text)
    update_gamer_data_json = json.loads(updatedGamerData.text)
    
    user_json_object = session['loginuser']
    user_json_object["dob"] = update_gamer_data_json["dob"]
    user_json_object["id"] = update_gamer_data_json["id"]
    user_json_object["level"] = update_gamer_data_json["level"]
    user_json_object["name"] = update_gamer_data_json["name"]
    user_json_object["uid"] = update_gamer_data_json["uid"]
    session['loginuser'] = user_json_object
    
    return redirect(url_for("profile", profile_message="Profile updated successfully"))

# shows leaderboards
@app.route('/leaderboards')  
def leaderboards():
    url = rootUrl + '/gamers/scores'
    scoresResponse = requests.get(url)
    #print(scoresResponse.text)
    scores_json_data = json.loads(scoresResponse.text)
    if 'loginuser' in session:
        loginuser = session["loginuser"]
        return render_template("leaderboards.html", scores=scores_json_data, user_json_object=loginuser)
    else :
        return render_template("leaderboards.html", scores=scores_json_data)

# shows sign up page
@app.route('/signup')  
def signup():
    return render_template("signup.html")

# loads snake game in the browser
# not used anymore
@app.route('/snake_game/')
def snake_game():
    return render_template('snake_game.html')

# gets logged in user details
@app.route('/getloginuser/', methods=['POST', 'GET','OPTIONS'])
def getloginuser():
    print("Getting logged in user detals")

    if 'loginuser' in session:
        loginuser = session["loginuser"]
        print(loginuser)
    else:
        loginuser = {"valid": False}
    
    response = make_response(loginuser, 200)
    # this is probably not needed 
    # was added during some CORS troubleshooting
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers']= "*"
    header['Access-Control-Allow-Methods'] ="*"
    return response

# loads users admin
@app.route('/administration')
def user_admin():
    url = rootUrl + '/gamers'
    gamersResponse = requests.get(url)
    #print(x.text)
    gamers_json_data = json.loads(gamersResponse.text)
    
    if 'adminuser' in session:
        admin_user_json_object = session["adminuser"]
        return render_template("user_administration.html", gamers=gamers_json_data, user_json_object=admin_user_json_object, admin=True)
    else :
        return render_template("user_administration.html", gamers=gamers_json_data)
    
# this runs the application on the development server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8097")
