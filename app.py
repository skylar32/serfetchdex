import mohacdex.db
from mohacdex.db.base import Base

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mohacdex.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, model_class=Base)

def get_type_efficiencies(type_name, both_sides=False):
    efficiencies = {"Damage dealt": {}}

    efficiencies["Damage dealt"]["2x"] = [
        type.defending_type.identifier for type in
        db.session.query(mohacdex.db.TypeMatchup).filter(
            mohacdex.db.TypeMatchup.attacking_type_identifier==type_name,
            mohacdex.db.TypeMatchup.matchup == 2
        ).all()
    ]
    efficiencies["Damage dealt"]["½x"] = [
        type.defending_type.identifier for type in
        db.session.query(mohacdex.db.TypeMatchup).filter(
            mohacdex.db.TypeMatchup.attacking_type_identifier==type_name,
            mohacdex.db.TypeMatchup.matchup == .5
        ).all()
    ]
    efficiencies["Damage dealt"]["0x"] = [
        type.defending_type.identifier for type in
        db.session.query(mohacdex.db.TypeMatchup).filter(
            mohacdex.db.TypeMatchup.attacking_type_identifier==type_name,
            mohacdex.db.TypeMatchup.matchup == 0
        ).all()
    ]
    if both_sides:
        efficiencies["Damage taken"] = {}
        efficiencies["Damage taken"]["2x"] = [
            type.attacking_type.identifier for type in
            db.session.query(mohacdex.db.TypeMatchup).filter(
                mohacdex.db.TypeMatchup.defending_type_identifier==type_name,
                mohacdex.db.TypeMatchup.matchup == 2
            ).all()
        ]
        efficiencies["Damage taken"]["½x"] = [
            type.attacking_type.identifier for type in
            db.session.query(mohacdex.db.TypeMatchup).filter(
                mohacdex.db.TypeMatchup.defending_type_identifier==type_name,
                mohacdex.db.TypeMatchup.matchup == .5
            ).all()
        ]
        efficiencies["Damage taken"]["0x"] = [
            type.attacking_type.identifier for type in
            db.session.query(mohacdex.db.TypeMatchup).filter(
                mohacdex.db.TypeMatchup.defending_type_identifier==type_name,
                mohacdex.db.TypeMatchup.matchup == 0
            ).all()
        ]

    return efficiencies

@app.before_request
def clear_trailing():
    from flask import redirect, request

    rp = request.path 
    if rp != '/' and rp.endswith('/'):
        return redirect(rp[:-1])

@app.template_filter()
def parse_links(string):
    tags = re.findall(r"\[\[([^]]+)\]\]", string)
    template = '<a href="/{}/{}">{}</a>'
    links = {}
    
    for item in tags:
        components = item.split(":")
        appear_as = components[1].split("|")
        identifier = appear_as[0].lower().replace(' ', '-')
        link = template.format(components[0], identifier, appear_as[1] if len(appear_as) == 2 else components[1])
        links["[[" + item + "]]"] = link
    for find, replace in links.items():
        string = string.replace(find, replace)
    
    return string

@app.route('/')
def index():
    return render_template("index.html.j2")

@app.route('/moves')
def get_move_index():
    moves = db.session.query(mohacdex.db.Move).all()
    return render_template("moves-index.html.j2", moves=moves)

@app.route('/abilities')
def get_ability_index():
    abilities = db.session.query(mohacdex.db.Ability).all()
    return render_template("abilities-index.html.j2", abilities=abilities)

@app.route('/moves/<identifier>')
def get_move(identifier):
    move = db.session.query(mohacdex.db.Move).filter(mohacdex.db.Move.identifier==identifier).one()
    flags = db.session.query(mohacdex.db.Flag).all()
    move_flags = [flag.flag.name for flag in db.session.query(mohacdex.db.MoveFlag).filter(mohacdex.db.MoveFlag.move==move.identifier).all()]
    efficiencies = get_type_efficiencies(move.type)
    return render_template("move.html.j2", move=move, all_flags=flags, move_flags=move_flags, efficiencies=efficiencies)

@app.route('/abilities/<identifier>')
def get_ability(identifier):
    ability = db.session.query(mohacdex.db.Ability).filter(mohacdex.db.Ability.identifier==identifier).one()
    return render_template("ability.html.j2", ability=ability)

@app.route('/types/<type_name>')
def get_type(type_name):
    moves  = db.session.query(mohacdex.db.Move).filter(mohacdex.db.Move.type==type_name).all()
    efficiencies = get_type_efficiencies(type_name, both_sides=True)
    return render_template("type.html.j2", type_name=type_name.title(), moves=moves, efficiencies=efficiencies)

if __name__ == "__main__":
    app.run(debug=True)
