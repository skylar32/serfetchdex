import mohacdex.db
from mohacdex.db.base import Base

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

import re
import itertools

cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 0
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mohacdex.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
cache = Cache()
db = SQLAlchemy(app, model_class=Base)

def get_type_efficiencies(types, sides=["Damage dealt", "Damage taken"]):
    matchups = {side: {} for side in sides}
    sides_map = {
        "Damage dealt": mohacdex.db.TypeMatchup.attacking_type_identifier,
        "Damage taken": mohacdex.db.TypeMatchup.defending_type_identifier
    }

    for side in sides:
        for type in types:
            type_matchups = db.session.query(mohacdex.db.TypeMatchup).filter(sides_map[side]==type).all()
            for matchup in type_matchups:
                if side == "Damage dealt":
                    matchup_type = matchup.defending_type_identifier
                elif side == "Damage taken":
                    matchup_type = matchup.attacking_type_identifier
                if matchup_type not in matchups[side]:
                    matchups[side][matchup_type] = matchup.matchup
                else:
                    matchups[side][matchup_type] *= matchup.matchup

    matchup_name_map = {4.0: "4x", 2.0: "2x", 0.5: "½x", 0.25: "¼x", 0.0: "0x"}
    reversed_matchups = {side: {matchup_name_map[key]: [] for key in matchup_name_map.keys()} for side in sides}
    for side in sides:
        for key, value in matchups[side].items():
            if value != 1.0:
                reversed_matchups[side][matchup_name_map[value]].append(key)
        if len(types) == 1 or None in types:
            del reversed_matchups[side]["4x"]
            del reversed_matchups[side]["¼x"]
  
    return reversed_matchups

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

@app.template_filter()
def m_to_feet(m):
    import decimal
    feet = m // decimal.Decimal(".3048")
    inches = m / decimal.Decimal(".3048") % 1 * 12
    return "{}'{}\"".format(feet, round(inches))

@app.template_filter()
def kg_to_lbs(kg):
    import decimal
    return (kg * decimal.Decimal("2.20462")).quantize(kg)

@app.route('/')
def index():
    return render_template("index.html.j2")

@app.route('/pokemon')
def get_pokemon_index():
    pokemon = db.session.query(mohacdex.db.Pokemon).order_by(mohacdex.db.Pokemon.order).all()
    return render_template("pokemon-index.html.j2", pokemon=pokemon)

@app.route('/moves')
def get_move_index():
    moves = db.session.query(mohacdex.db.Move).all()
    return render_template("moves-index.html.j2", moves=moves)

@app.route('/abilities')
def get_ability_index():
    abilities = db.session.query(mohacdex.db.Ability).all()
    return render_template("abilities-index.html.j2", abilities=abilities)

@app.route('/pokemon/<identifier>')
def get_pokemon(identifier):
    pokemon = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon.identifier==identifier).one()
    matchups = get_type_efficiencies(pokemon.types, sides=["Damage taken"])
    other_forms = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon.number==pokemon.number).all()
    other_forms = [form for form in other_forms if form != pokemon]
    print(pokemon.effort_yield)
    return render_template("pokemon.html.j2", pokemon=pokemon, efficiencies=matchups, other_forms=other_forms)

@app.route('/moves/<identifier>')
def get_move(identifier):
    move = db.session.query(mohacdex.db.Move).filter(mohacdex.db.Move.identifier==identifier).one()
    flags = db.session.query(mohacdex.db.Flag).all()
    move_flags = [flag.flag.name for flag in db.session.query(mohacdex.db.MoveFlag).filter(mohacdex.db.MoveFlag.move==move.identifier).all()]
    matchups = get_type_efficiencies([move.type], sides=["Damage dealt"])
    levelup = [(move.pokemon, move.level) for move in db.session.query(
        mohacdex.db.LevelUpMove).filter(mohacdex.db.LevelUpMove.move==move).order_by(mohacdex.db.LevelUpMove.level).all()
        ]
    levelup = [next(level) for move, level in itertools.groupby(levelup, lambda y: y[0])]
    machine = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon.machine_moves.any(mohacdex.db.Move.identifier==identifier)).all()
    tutor = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon.tutor_moves.any(mohacdex.db.Move.identifier==identifier)).all()
    egg = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon.egg_moves.any(mohacdex.db.Move.identifier==identifier)).all()
    return render_template("move.html.j2", move=move, all_flags=flags, move_flags=move_flags, efficiencies=matchups, levelup=levelup, machine=machine, tutor=tutor, egg=egg)

@app.route('/abilities/<identifier>')
def get_ability(identifier):
    ability = db.session.query(mohacdex.db.Ability).filter(mohacdex.db.Ability.identifier==identifier).one()
    ordinary = [a.pokemon for a in db.session.query(mohacdex.db.PokemonAbility).filter(mohacdex.db.PokemonAbility.ability==ability, mohacdex.db.PokemonAbility.slot.in_(("ability_1", "ability_2"))).all()]
    hidden = [a.pokemon for a in db.session.query(mohacdex.db.PokemonAbility).filter(mohacdex.db.PokemonAbility.ability==ability, mohacdex.db.PokemonAbility.slot=="hidden_ability").all()]
    unique = [a.pokemon for a in db.session.query(mohacdex.db.PokemonAbility).filter(mohacdex.db.PokemonAbility.ability==ability, mohacdex.db.PokemonAbility.slot=="unique_ability").all()]
    pokemon = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon._ability_table.any(mohacdex.db.PokemonAbility.ability_identifier==identifier)).all()
    for item in [ordinary, hidden, unique]:
        print([mon.identifier for mon in item])
    return render_template("ability.html.j2", ability=ability, ordinary=ordinary, hidden=hidden, unique=unique)

@app.route('/types/<type_name>')
def get_type(type_name):
    moves  = db.session.query(mohacdex.db.Move).filter(mohacdex.db.Move.type==type_name).all()
    matchups = get_type_efficiencies([type_name], sides=["Damage dealt", "Damage taken"])
    return render_template("type.html.j2", type_name=type_name.title(), moves=moves, efficiencies=matchups)

if __name__ == "__main__":
    cache.init_app(app, config=cache_config)
    with app.app_context():
        cache.clear()
    app.run(debug=True)
