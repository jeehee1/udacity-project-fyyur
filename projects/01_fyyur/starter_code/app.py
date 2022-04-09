#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from html.entities import name2codepoint
import json
from re import A
import dateutil.parser
from models import db, Venue, Artist, Show
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate, show
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from sqlalchemy.sql.sqltypes import ARRAY
from werkzeug.wrappers import response
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()

  for place in places:
    data.append({
      'city' : place.city,
      'state' : place.state,
      'venues' : [{
        'id' : venue.id,
        'name' : venue.name,
        'num_upcomming_shows' : len([show for show in venue.show if show.start_time>datetime.now()])
      } for venue in venues if place.city == venue.city and place.state == venue.state]
    })

  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike("%"+search_term+"%")).all()

  response={
    'count' : len(venues),
    'data' : venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get_or_404(venue_id)
  # past_shows = db.session.query(Show, Artist).filter(Show.venue_id == venue_id).filter(Show.artist_id == Artist.id).filter(Show.start_time<datetime.now()).all()
  # upcoming_shows = db.session.query(Show, Artist).filter(Show.venue_id==venue_id).filter(Show.artist_id == Artist.id).filter(Show.start_time>datetime.now()).all()
  past_shows = []
  upcoming_shows = []

  for venue_show in venue.show:
    temp_show = {
      'artist_id' : venue_show.artist_id,
      'artist_name' : venue_show.artist.name,
      'artist_image_link' : venue_show.artist.image_link,
      'start_time' : venue_show.start_time.strftime('%y-%m-%d %H-%M')
    }
    if venue_show.start_time > datetime.now():
      upcoming_shows.append(temp_show)
    else:
      past_shows.append(temp_show)

  #object class to dic
  data = vars(venue)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  #set csrf as false to enable for.validate, in a production application CSRF must be activated
  form = VenueForm(request.form, meta={'csrf':False}) 
  if form.validate():
    try:
      venue = Venue()
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    # TODO: modify data to be the data object returned from db insertion

    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    
    finally:
      db.session.close()
    
  else:
    message=[]
    for field, err in form.errors.items():
      message.append(field+' '+'|'.join(err))
      flash('Errors ' + str(message))


  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
      
    db.session.commit()
    flash(venue.name+' is succefully deleted')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('Error is occured.'+venue.name+'could not be deleted.')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      'id' : artist.id,
      'name' : artist.name, 
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%"+ search_term +"%")).all()
  response = {
    'count' : len(artists),
    'data' : artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get_or_404(artist_id)

  past_shows = []
  upcoming_shows = []
  # past_shows = db.session.query(Show, Venue).filter(Show.artist_id==artist_id).filter(Show.venue_id==Venue.id).filter(Show.start_time<datetime.now()).all()
  # upcoming_shows = db.session.query(Show, Venue).filter(Show.artist_id==artist_id).filter(Show.venue_id==Venue.id).filter(Show.start_time>datetime.now()).all()

  for artist_show in artist.show:
    temp_show = {
      'venue_id' : artist_show.venue_id,
      'venue_name' : artist_show.venue.name,
      'venue_image_link' : artist_show.venue.image_link,
      'start_time' : artist_show.start_time.strftime('%y-%m-%d %H:%M')
    }
    if artist_show.start_time > datetime.now():
      upcoming_shows.append(temp_show)
    else:
      past_shows.append(temp_show)
    
  data = vars(artist)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj = artist)
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    flash(artist.name + ' is succefully edited!')

  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('edit failed. Please try again.')

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj = venue)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    
    db.session.commit()
  except ValueError as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()

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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form, meta={'csrf' : False})
  if form.validate():
    try:
      artist = Artist()
      form.populate_obj(artist)
      db.session.add(artist)
      db.session.commit()

      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Artist ' + form.name + ' could not be listed.')
    
    finally:
      db.session.close()

  else:
    message=[]
    for field, err in form.errors.items():
      message.append(field+' '+'|'.join(err))
      flash('Errors '+str(message))

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  results = db.session.query(Show, Venue, Artist)\
    .join(Venue, Show.venue_id==Venue.id)\
    .join(Artist, Show.artist_id==Artist.id)\
    .order_by(Show.start_time.desc())\
    .all()

  for show, venue, artist in results:
    data.append({
      'venue_id' : venue.id,
      'venue_name' : venue.name,
      'artist_id' : artist.id,
      'artist_name' : artist.name,
      'artist_image_link' : artist.image_link,
      'start_time' : show.start_time.strftime('%y-%m-%d %H:%M')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  venues = Venue.query.all()
  artists = Artist.query.all()
  form = ShowForm(venues=venues, artists=artists)
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  try:
    venues = Venue.query.all()
    artists = Artist.query.all()
    form = ShowForm(request.form, venues=venues, artists=artists)
    
    show = Show()
    form.populate_obj(show)
    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')

  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Show could not be listed')

  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
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
