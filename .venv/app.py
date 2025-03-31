from flask import Flask, request, jsonify
from flask_migrate import Migrate
import requests
import logging
from models import db, Person
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

@app.route('/people', methods=['POST'])
def add_person():
    data = request.json
    name = data.get('name')
    surname = data.get('surname')
    patronymic = data.get('patronymic')

    # Обогащение данных
    age = requests.get(f'https://api.agify.io/?name={name}').json().get('age')
    gender = requests.get(f'https://api.genderize.io/?name={name}').json().get('gender')
    nationality = requests.get(f'https://api.nationalize.io/?name={name}').json().get('country')[0]['country_id']

    person = Person(name=name, surname=surname, patronymic=patronymic, age=age, gender=gender, nationality=nationality)
    db.session.add(person)
    db.session.commit()

    logging.info(f'Added person: {person}')
    return jsonify({'id': person.id}), 201

@app.route('/people', methods=['GET'])
def get_people():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    people = Person.query.paginate(page, per_page, error_out=False)
    return jsonify([{'id': p.id, 'name': p.name, 'surname': p.surname, 'patronymic': p.patronymic, 'age': p.age, 'gender': p.gender, 'nationality': p.nationality} for p in people.items])

@app.route('/people/<int:id>', methods=['DELETE'])
def delete_person(id):
    person = Person.query.get_or_404(id)
    db.session.delete(person)
    db.session.commit()
    logging.info(f'Deleted person: {person}')
    return '', 204

@app.route('/people/<int:id>', methods=['PUT'])
def update_person(id):
    data = request.json
    person = Person.query.get_or_404(id)

    person.name = data.get('name', person.name)
    person.surname = data.get('surname', person.surname)
    person.patronymic = data.get('patronymic', person.patronymic)

    db.session.commit()
    logging.info(f'Updated person: {person}')
    return jsonify({'id': person.id}), 200

if __name__ == '__main__':
    app.run(debug=True)
