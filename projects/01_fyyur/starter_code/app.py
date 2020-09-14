#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(200))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200))
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(200))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200))
    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    venue_id= db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id= db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_time= db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  areasQuery = db.session.query(Venue.city, Venue.state).distinct().all()
  data=[]
  for area in areasQuery:
    areas = {}
    areas['city'] = area.city
    areas['state'] = area.state
    venues = []
    venuesQuery = db.session.query(Venue.id, Venue.name).filter(Venue.city == area.city and Venue.state == area.state).all()
    for venue in venuesQuery:
      a_venue = {}
      a_venue['id'] = venue.id
      a_venue['name'] = venue.name
      a_venue['num_upcoming_shows'] = Show.query.filter(Show.venue_id == venue.id and Show.start_time > datetime.now()).count()
      venues.append(a_venue)
    areas['venues'] = venues
    data.append(areas)  
    print(data)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  searchQuery = Venue.query.filter(Venue.name.ilike('%'+ request.form.get('search_term') +'%'))
  data = []
  venues = searchQuery.all()
  for venue in venues:
    venue_data = {}
    venue_data["id"] = venue.id
    venue_data["name"] = venue.name
    upcoming_shows_query = Show.query.filter(
      Show.venue_id == venue.id
    ).filter(Show.start_time > datetime.now())
    venue_data["num_upcoming_shows"] = upcoming_shows_query.count()
    data.append(venue_data)

  response={
    "count": searchQuery.count(),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  venue_data = {}
  venue_data["id"] = venue.id
  venue_data["name"] = venue.name
  venue_data["genres"] = venue.genres.split(',')
  venue_data["address"] = venue.address
  venue_data["city"] = venue.city
  venue_data["state"] = venue.state
  venue_data["phone"] = venue.phone
  venue_data["website"] = venue.website
  venue_data["facebook_link"] =  venue.facebook_link
  venue_data["seeking_talent"] = venue.seeking_talent
  venue_data["seeking_description"] = venue.seeking_description
  venue_data["image_link"] = venue.image_link

  showsQuery = db.session.query(Artist, Show).filter(
    Artist.id == Show.artist_id 
  ).filter(
    Show.venue_id==venue_id
  )

  #"past_shows"
  pastshows = showsQuery.filter(
    Show.start_time < datetime.now()
  ).all()
  
  pastshowsList = []
  for (artist,show) in pastshows:
    past_show_data = {}
    past_show_data["artist_id"] = artist.id
    past_show_data["artist_name"] = artist.name
    past_show_data["artist_image_link"] = artist.image_link
    past_show_data["start_time"] = str(show.start_time)
    pastshowsList.append(past_show_data)

  #"upcoming_shows"
  upcomingshows = showsQuery.filter(
    Show.start_time > datetime.now()
  ).all()

  upcomingshowsList = []
  for (artist,show) in upcomingshows:
    upcoming_show_data = {}
    upcoming_show_data["artist_id"] = artist.id
    upcoming_show_data["artist_name"] = artist.name
    upcoming_show_data["artist_image_link"] = artist.image_link
    upcoming_show_data["start_time"] = str(show.start_time)
    upcomingshowsList.append(upcoming_show_data)

  venue_data["past_shows"] = pastshowsList
  venue_data['upcoming_shows'] = upcomingshowsList
  venue_data["past_shows_count"] = len(pastshows)
  venue_data["upcoming_shows_count"] = len(upcomingshows)

  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    genresList = request.form.getlist('genres')
    seeking_description = request.form['seeking_description']
    if 'seeking_talent' in request.form:
      seeking_talent = bool(request.form['seeking_talent'])
    else:
      seeking_talent = False
    
    genres= ''
    for genre in genresList:
      if len(genres)>0:
        genres+=","+genre
      else:
        genres+= genre
    # TODO: insert form data as a new Venue record in the db, instead
    venue = Venue(
      name = name,
      city = city,
      state = state,
      address = address,
      phone = phone,
      image_link = image_link,
      facebook_link = facebook_link,
      website = website,
      genres = genres,
      seeking_description = seeking_description,
      seeking_talent = seeking_talent
      )  
    # TODO: modify data to be the data object returned from db insertion
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for artist in artists:
    artist_data = {}
    artist_data["id"] = artist.id
    artist_data["name"] = artist.name
    data.append(artist_data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searchQuery = Artist.query.filter(Artist.name.ilike('%'+ request.form.get('search_term') +'%'))
  data = []
  artists = searchQuery.all()
  for artist in artists:
    artist_data = {}
    artist_data["id"] = artist.id
    artist_data["name"] = artist.name
    upcoming_shows_query = Show.query.filter(
      Show.artist_id == artist.id
    ).filter(Show.start_time > datetime.now())
    artist_data["num_upcoming_shows"] = upcoming_shows_query.count()
    data.append(artist_data)

  response={
    "count": searchQuery.count(),
    "data": data
  }  

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artists page with the given artist_id
  # TODO: replace with real artist data from the venues table, using artist_id
  artist = Artist.query.get(artist_id)
  artist_data = {}
  artist_data["id"] = artist.id
  artist_data["name"] = artist.name
  artist_data["genres"] = artist.genres.split(',')
  artist_data["city"] = artist.city
  artist_data["state"] = artist.state
  artist_data["phone"] = artist.phone
  artist_data["website"] = artist.website
  artist_data["facebook_link"] =  artist.facebook_link
  artist_data["seeking_venue"] = artist.seeking_venue
  artist_data["seeking_description"] = artist.seeking_description
  artist_data["image_link"] = artist.image_link

  showsQuery = db.session.query(Venue, Show).filter(
    Venue.id == Show.venue_id 
  ).filter(
    Show.artist_id==artist_id
  )

  #"past_shows"
  pastshows = showsQuery.filter(
    Show.start_time < datetime.now()
  ).all()
  
  pastshowsList = []
  for (venue,show) in pastshows:
    past_show_data = {}
    past_show_data["venue_id"] = venue.id
    past_show_data["venue_name"] = venue.name
    past_show_data["venue_image_link"] = venue.image_link
    past_show_data["start_time"] = str(show.start_time)
    pastshowsList.append(past_show_data)

  #"upcoming_shows"
  upcomingshows = showsQuery.filter(
    Show.start_time > datetime.now()
  ).all()

  upcomingshowsList = []
  for (venue,show) in upcomingshows:
    upcoming_show_data = {}
    upcoming_show_data["venue_id"] = venue.id
    upcoming_show_data["venue_name"] = venue.name
    upcoming_show_data["venue_image_link"] = venue.image_link
    upcoming_show_data["start_time"] = str(show.start_time)
    upcomingshowsList.append(upcoming_show_data)

  artist_data["past_shows"] = pastshowsList
  artist_data['upcoming_shows'] = upcomingshowsList
  artist_data["past_shows_count"] = len(pastshows)
  artist_data["upcoming_shows_count"] = len(upcomingshows)

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    genresList = request.form.getlist('genres')
    seeking_description = request.form['seeking_description']
    if 'seeking_venue' in request.form:
      seeking_venue = bool(request.form['seeking_venue'])
    else:
      seeking_venue = False

    genres= ''
    for genre in genresList:
      if len(genres)>0:
        genres+=","+genre
      else:
        genres+= genre
    # TODO: insert form data as a new Artist record in the db, instead
    artist = Artist(
      name = name,
      city = city,
      state = state,
      phone = phone,
      image_link = image_link,
      facebook_link = facebook_link,
      website = website,
      genres = genres,
      seeking_description = seeking_description,
      seeking_venue = seeking_venue
      )  
    # TODO: modify data to be the data object returned from db insertion
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    # TODO: on unsuccessful db insert, flash an error instead.
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real shows data.
  data = []
  shows = db.session.query(Artist, Venue, Show).filter(
    Artist.id == Show.artist_id
    ).filter(
      Venue.id == Show.venue_id
    ).all()

  for (artist, venue, show) in shows:
    shows_data = {}
    shows_data["venue_id"] = show.venue_id
    shows_data["venue_name"] = venue.name
    shows_data["artist_id"] = show.artist_id
    shows_data["artist_name"] = artist.name
    shows_data["artist_image_link"] = artist.image_link
    shows_data["start_time"] = str(show.start_time)
    data.append(shows_data)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    # called to create new shows in the db, upon submitting new show listing form
    # # TODO: insert form data as a new Show record in the db, instead
    artist_id = int(request.form['artist_id'])
    venue_id = int(request.form['venue_id'])
    start_timeInput = format_datetime(request.form['start_time'])
    print(start_timeInput)
    fmt = '%a %m, %d, %Y %I:%M%p'
    start_time = datetime.strptime(start_timeInput, fmt)
    print(start_time)
    show = Show(artist_id = artist_id, venue_id=venue_id, start_time=start_time)
    print(show)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
