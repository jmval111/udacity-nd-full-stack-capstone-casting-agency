from flask import Blueprint, request, jsonify
from models import db, Movie, Actor
import datetime
import utils
import auth
import errors


actor_blueprint = Blueprint('actor', __name__)


@actor_blueprint.route('/actors', methods=['POST'])
@auth.requires_auth('create:actor')
def create_actor(jwt_payload):
    actor = Actor()
    data = request.json
    actor.name = data['name']
    actor.age = data['age']
    actor.gender = data['gender'].lower()
    db.session.add(actor)
    db.session.flush()
    if 'movies' in data:
        movies = Movie.query.filter(Movie.id.in_(data['movies'])).all()
        for movie in movies:
            actor.movies.append(movie)
    db.session.commit()
    return jsonify(actor.long()), 201


@actor_blueprint.route('/actors')
@auth.requires_auth('read:actor')
def get_actors(jwt_payload):
    max_per_page = 50
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    q = Actor.query
    search_term = request.args.get('search_term', None, str)
    if search_term:
        q = q.filter(Actor.name.ilike(search_term))
    pagination = q.paginate(page, per_page, max_per_page)
    returned_actors = []
    for actor in pagination.items:
        returned_actors.append(actor.short())
    returned_data = {
        'items': returned_actors,
        'total_items': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }
    return jsonify(returned_data)


@actor_blueprint.route('/actors/<int:actor_id>')
@auth.requires_auth('read:actor')
def get_actor(jwt_payload, actor_id):
    actor = Actor.query.filter(Actor.id == actor_id).first()
    if not actor:
        return errors.not_found_error('Actor not found')
    return jsonify(actor.long())


@actor_blueprint.route('/actors/<int:actor_id>', methods=['PATCH'])
@auth.requires_auth('update:actor')
def patch_actor(jwt_payload, actor_id):
    actor = Actor.query.filter(Actor.id == actor_id).first()
    if not actor:
        return errors.not_found_error('Actor not found')
    data = request.json
    if 'name' in data:
        actor.name = data['name']
    if 'age' in data:
        actor.age = data['age']
    if 'gender' in data and data['gender'].lower() in Actor.get_available_genders():
        actor.gender = data['gender'].lower()
    if 'movies' in data:
        movies = Movie.query.filter(Movie.id.in_(data['movies'])).all()
        actor.movies = []
        for movie in movies:
            actor.movies.append(movie)
    db.session.commit()
    return jsonify(actor.long())


@actor_blueprint.route('/actors/<int:actor_id>', methods=['DELETE'])
@auth.requires_auth('delete:actor')
def delete_actor(jwt_payload, actor_id):
    actor = Actor.query.filter(Actor.id == actor_id).first()
    if not actor:
        return errors.not_found_error('Actor not found')
    actor.delete()
    return '', 204
