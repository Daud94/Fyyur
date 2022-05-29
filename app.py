# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import babel.dates
import dateutil.parser
from flask import render_template, request, flash, redirect, url_for

import logging
from logging import Formatter, FileHandler
from forms import *
from Models import *


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # venues = Venue.query.join(Show).filter_by(id=Show.venue_id).all()
    venues = db.session.query(Venue).join(Show).filter(Venue.id == Show.venue_id).all()
    data = []
    for venue in venues:
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": [
                {"id": venue.id,
                 "name": venue.name,
                 }
            ]
        }
        )
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seacrh for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_result = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.contains(search_result)).all()
    count = len(venues)
    data = []
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,
        })

    response = {
        "count": str(count),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).all()
    datas = []
    past_shows = []
    upcoming_shows = []
    past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
        Show.date < datetime.now()).all()
    for past in past_shows_query:
        past_shows.append({
            "artist_id": past.artist_id,
            "artist_name": past.artist.name,
            "artist_image_link": past.artist.image_link,
            "start_time": str(past.date)
        }
        )
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
        Show.date > datetime.now()).all()
    for upcoming in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": upcoming.artist_id,
            "artist_name": upcoming.artist.name,
            "artist_image_link": upcoming.artist.image_link,
            "start_time": str(upcoming.date)
        }
        )
    for show in shows:
        print(type(show.venue.genres))
        datas.append({
            "id": show.venue_id,
            "name": show.venue.name,
            "genres": show.venue.genres,
            "address": show.venue.address,
            "city": show.venue.city,
            "state": show.venue.state,
            "phone": show.venue.phone,
            "website": show.venue.website_link,
            "facebook_link": show.venue.facebook_link,
            "seeking_talent": show.venue.looking_for_talent,
            "seeking_description": show.venue.seeking_description,
            "image_link": show.venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows_query),
        })
    data = list(filter(lambda d: d['id'] == venue_id, datas))[0]
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    try:
        artist = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            genres=request.form.getlist('genres'),
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            looking_for_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(artist)
        db.session.commit()
        db.session.close()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        for field, message in form.errors.items():
            flash(field + '-' + str(message), 'danger')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/<int:venue_id>/delete/', methods=['POST'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue with ID' + venue.id + 'has been deleted')
    except:
        db.session.rollback()
        flash('Deletion unsuccessful')
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append(
            {
                "id": artist.id,
                "name": artist.name
            }
        )
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_result = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.contains(search_result)).all()
    count = len(artists)
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
        })

    response = {
        "count": str(count),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    shows = Show.query.join(Artist).filter(Show.artist_id == artist_id).all()
    # shows = Show.query.filter_by(artist_id=artist_id).all()
    datas = []
    past_shows = []
    upcoming_shows = []

    past_shows_query = Show.query.join(Artist).filter(Show.artist_id == artist_id).filter(
        Show.date < datetime.now()).all()
    for past in past_shows_query:
        past_shows.append({
            "venue_id": past.venue_id,
            "venue_name": past.venue.name,
            "venue_image_link": past.venue.image_link,
            "start_time": str(past.date)
        }
        )
    upcoming_shows_query = Show.query.join(Artist).filter(Show.artist_id == artist_id).filter(
        Show.date > datetime.now()).all()
    for upcoming in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": upcoming.venue_id,
            "venue_name": upcoming.venue.name,
            "venue_image_link": upcoming.venue.image_link,
            "start_time": str(upcoming.date)
        }
        )
    for show in shows:
        datas.append({
            "id": show.artist_id,
            "name": show.artist.name,
            "genres": show.artist.genres,
            "city": show.artist.city,
            "state": show.artist.state,
            "phone": show.artist.phone,
            "website": show.artist.website_link,
            "facebook_link": show.artist.facebook_link,
            "seeking_venue": show.artist.looking_for_venues,
            "seeking_description": show.artist.seeking_description,
            "image_link": show.artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows_query),
        })

    data = list(filter(lambda d: d['id'] == artist_id, datas))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artists = Artist.query.get(artist_id)
    form = ArtistForm(obj=artists)
    artist = {
        "id": artists.id,
        "name": artists.name,
        "genres": artists.genres,
        "city": artists.city,
        "state": artists.state,
        "phone": artists.phone,
        "website": artists.website_link,
        "facebook_link": artists.facebook_link,
        "seeking_venue": artists.looking_for_venues,
        "seeking_description": artists.seeking_description,
        "image_link": artists.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    artists = Artist.query.get(artist_id)
    try:
        artists.name = form.name.data
        artists.genres = request.form.getlist('genres')
        artists.city = form.city.data
        artists.state = form.state.data
        artists.phone = form.phone.data
        artists.website_link = form.website_link.data
        artists.facebook_link = form.facebook_link.data
        artists.looking_for_venues = form.seeking_venue.data
        artists.seeking_description = form.seeking_description.data
        artists.image_link = form.image_link.data

        # db.session.add(artists)
        db.session.commit()
        flash("Editing successful!")

    except Exception as error:
        print(error)
        db.session.rollback()
        flash("Editing unsuccessful!")

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venues = Venue.query.get(venue_id)
    form = VenueForm(obj=venues)
    venue = {
        "id": venues.id,
        "name": venues.name,
        "genres": request.form.getlist('genres'),
        "address": venues.address,
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "website": venues.website_link,
        "facebook_link": venues.facebook_link,
        "seeking_talent": venues.looking_for_talent,
        "seeking_description": venues.seeking_description,
        "image_link": venues.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()
    artists = Artist.query.get(venue_id)
    try:
        venues.name = form.name.data
        venues.genres = request.form.getlist('genres')
        venues.city = form.city.data
        venues.state = form.state.data
        venues.address = form.address.data
        venues.phone = form.phone.data
        venues.website_link = form.website_link.data
        venues.facebook_link = form.facebook_link.data
        venues.looking_for_talent = form.seeking_talent.data
        venues.seeking_description = form.seeking_description.data
        venues.image_link = form.image_link.data

        # db.session.add(artists)
        db.session.commit()
        flash("Editing successful!")

    except Exception as error:
        print(error)
        db.session.rollback()
        flash("Editing unsuccessful!")
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
    form = ArtistForm()
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            genres=request.form.getlist('genres'),
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            looking_for_venues=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        for field, message in form.errors.items():
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            flash(field + '-' + str(message), 'danger')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []
    venues = Show.query.all()
    for venue in venues:
        data.append(
            {
                "venue_id": venue.venue.id,
                "venue_name": venue.venue.name,
                "artist_id": venue.artist.id,
                "artist_name": venue.artist.name,
                "artist_image_link": venue.artist.image_link,
                "start_time": str(venue.date),
            }
        )

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm()

    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            date=form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
