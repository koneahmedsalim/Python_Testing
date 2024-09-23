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

reservations_by_club = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    
    club = [club for club in clubs if club['email'] == request.form['email']]
    
    if not club:
        flash("L'adresse e-mail est incorrecte. Veuillez réessayer.")
        return redirect(url_for('index'))  
    
    club = club[0]
    
    return render_template('welcome.html', club=club, competitions=competitions)



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
    
    # Initialiser le dictionnaire si nécessaire
    if club['name'] not in reservations_by_club:
        reservations_by_club[club['name']] = {}

    if competition['name'] not in reservations_by_club[club['name']]:
        reservations_by_club[club['name']][competition['name']] = 0

    # Calculer le total des réservations existantes pour ce club dans cette compétition
    total_reserved_by_club = reservations_by_club[club['name']][competition['name']]

    # Vérification : le club ne peut pas réserver plus de 12 places au total
    if total_reserved_by_club + placesRequired > 12:
        flash(f"Vous ne pouvez pas réserver plus de 12 places au total pour cette compétition.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérification du nombre de places disponibles
    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Il ne reste que {competition['numberOfPlaces']} places disponibles.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérification que le club a assez de points pour réserver
    total_points_needed = placesRequired
    if int(club['points']) >= total_points_needed:
        # Mettre à jour les points et les places disponibles
        club['points'] = int(club['points']) - total_points_needed
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired

        # Mettre à jour le nombre total de places réservées par le club
        reservations_by_club[club['name']][competition['name']] += placesRequired

        flash(f"Réservation réussie ! Vous avez réservé {placesRequired} places.")
    else:
        flash("Vous n'avez pas assez de points pour réserver ces places.")

    return render_template('welcome.html', club=club, competitions=competitions)


# // TODO: Add route for points display

@app.route('/clubsPoints')
def clubsPoints():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))