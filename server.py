import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    total_points_needed = placesRequired * 1
    
    if placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places pour une compétition.")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Il ne reste que {competition['numberOfPlaces']} places disponibles.")
        return render_template('welcome.html', club=club, competitions=competitions)
    if int(club['points']) >= total_points_needed:  
        # Vérifier s'il y a assez de places disponibles dans la compétition
        if int(competition['numberOfPlaces']) >= placesRequired:
            # Deduct points and update places
            club['points'] = int(club['points']) - total_points_needed  
        else:
            flash('Il n\'y a pas assez de places disponibles pour cette compétition.')
    else:
        flash('Vous n\'avez pas assez de points pour réserver ces places.')
    
    
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))