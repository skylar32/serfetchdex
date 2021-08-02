import mohacdex.db
from mohacdex.db.base import Base

from flask import Flask, render_template, redirect, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_caching import Cache

import re
import itertools

from sqlalchemy.sql.functions import random

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

def get_evo_method_prose(evolution):
    def get_article(string):
        if string:
            return "an" if string[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
        else:
            return ''

    method_prose_map = {
        "level": f"Raise to level {evolution.quantity}" if evolution.quantity else "Level up",
        "happiness": f"Level up with {evolution.quantity} happiness",
        "use-item":  "Use " + get_article(evolution.item_identifier) + f" {evolution.item_identifier}",
        "trade": "Trade",
        "hitmonlee": "Raise to level 20 with Attack higher than Defense",
        "hitmonchan": "Raise to level 20 with Defense higher than Attack",
        "hitmontop": "Raise to level 20 with equal Attack and Defense",
        "sirfetchd": "Land three critical hits in one battle",
        "shedinja": "Raise to level 20 with an extra party space and a Poké Ball in the Bag",
        "runerigus": "Go to the stone bridge in Dusty Bowl after at least 49HP have been lost without fainting",
        "melmetal": "Use 400 Meltan Candy in Pokémon Go",
        "toxtricity-amped": "Raise to level 30 with Hardy, Brave, Adamant, Naughty, Docile, Impish, Lax, Hasty, Jolly, Naive, Rash, Sassy, or Quirky nature",
        "toxtricity-low-key": "Raise to level 30 with Lonely, Bold, Relaxed, Timid, Serious, Modest, Quiet, Bashful, Calm, Gentle, or Careful nature",
        "spin": "Spin",
        "urshifu-single": "Train in the Tower of Darkness",
        "urshifu-rapid": "Train in the Tower of Waters"
    }
    method = method_prose_map[evolution.method]
    conditions = []
    if evolution.method == "spin":
        length = "less than 5" if evolution.quantity == 4 else str(evolution.quantity)
        time = "between 7:00pm and 7:59pm" if evolution.time == "7" else "during the " + evolution.time
        method += f" {evolution.direction} for {length} seconds {time}"
    if evolution.method not in ["level", "happiness", "trade", "use-item"]:
        return method
    if evolution.region:
        conditions.append(f"in {evolution.region}")
    if evolution.location:
        conditions.append(f"at {evolution.location}")
    if evolution.ability:
        conditions.append(f"with the ability [[abilities:{evolution.ability.name}]]")
    if evolution.item_identifier and evolution.method != "use-item":
        conditions.append("while holding " + get_article(evolution.item_identifier) + f" {evolution.item_identifier}")
    if evolution.move:
        conditions.append(f"while knowing [[moves:{evolution.move.name}]]")
    if evolution.knows_move_type:
        conditions.append(f"while knowing a [[types:{evolution.knows_move_type.title()}]]-type move")
    if evolution.party_type_identifier:
        conditions.append(" while " + get_article(evolution.party_type_identifier) + f" [[types:{evolution.party_type_identifier.title()}]]-type is in the party")
    if evolution.needed_pokemon:
        if evolution.method == "level":
            conditions.append("while " + get_article(evolution.needed_pokemon.name) + f" [[pokemon:{evolution.needed_pokemon.name}]] is in the party")
        elif evolution.method == "trade":
            conditions.append("for " + get_article(evolution.needed_pokemon.name) + f" [[pokemon:{evolution.needed_pokemon.name}]]")
    if evolution.direction == "upside-down":
        conditions.append("while the system is held upside-down")
    if evolution.weather:
        conditions.append(f"while the weather is {evolution.weather}")
    if evolution.time:
        conditions.append("at " + evolution.time if evolution.time != "day" else "during the day")
    if len(conditions) > 2:
        cond_string = ", ".join(conditions[:-1]) + f", and {conditions[1]}"
    else:
        cond_string = " ".join(conditions)
    if evolution.gender:
        cond_string += f"({evolution.gender}s only)"
    return parse_links(method + ' ' + cond_string)

def get_evolution_table(evolution_chain):
    def get_mon_dict(evo, x, y):
        return {
            "mon": evo if x == 1 and y == 1 else evo.evolution,
            "prose": '' if x == 1 and y == 1 else get_evo_method_prose(evo),
            "coords": (x, y),
            "is_tall": isinstance(y, str)
        }
    evolution_table = []
    y = 1
    stages =1
    stage_2_height = 0

    base_form = evolution_chain.base_form
    evolution_table.append(get_mon_dict(base_form, 1, 1))
    stage_1_mons = base_form.evolutions
    for evo_1 in stage_1_mons:
        stages = max(stages, 2)
        stage_2_mons = evo_1.evolution.evolutions
        height = len(stage_2_mons)
        stage_2_height += height
        evolution_table.append(get_mon_dict(evo_1, 2, f"span {height}" if height > 1 else y))
        z = y
        for evo_2 in stage_2_mons:
            stages = max(stages, 3)
            evolution_table.append(get_mon_dict(evo_2, 3, z))
            z += 1
        y += 1

    if len(stage_1_mons) > 1 or stage_2_height > 1:
        evolution_table[0]["coords"] = (1, f"span {max(len(stage_1_mons), stage_2_height)}")
        evolution_table[0]["is_tall"] = True
    else:
        evolution_table[0]["is_tall"] = False
    return (stages, evolution_table)

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
    random_pokemon = (
        db.session.query(mohacdex.db.Pokemon)
        .order_by(func.random())
        .limit(1)
        .first()
    )
    random_move = (
        db.session.query(mohacdex.db.Move)
        .order_by(func.random())
        .limit(1)
        .first()
    )
    random_ability = (
        db.session.query(mohacdex.db.Ability)
        .order_by(func.random())
        .limit(1)
        .first()
    )
    return render_template("index.html.j2", pokemon=random_pokemon, move=random_move, ability=random_ability)

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
    if pokemon.evolution_chain:
        evos = get_evolution_table(pokemon.evolution_chain)
    elif pokemon.form and pokemon.form.evolution_chain:
        evos = get_evolution_table(pokemon.form.evolution_chain)
    else:
        evos = None
    return render_template("pokemon.html.j2", pokemon=pokemon, efficiencies=matchups, other_forms=other_forms, evos=evos)

@app.route('/moves/<identifier>')
def get_move(identifier):
    move = db.session.query(mohacdex.db.Move).filter(mohacdex.db.Move.identifier==identifier).one()
    flags = db.session.query(mohacdex.db.Flag).all()
    move_flags = [flag.flag.name for flag in db.session.query(mohacdex.db.MoveFlag).filter(mohacdex.db.MoveFlag.move==move.identifier).all()]
    matchups = get_type_efficiencies([move.type], sides=["Damage dealt"])
    levelup = [(move.pokemon, move.level) for move in db.session.query(
        mohacdex.db.LevelUpMove).filter(mohacdex.db.LevelUpMove.move==move).order_by(mohacdex.db.LevelUpMove.level).all()
        ]
    if move.damage_class == "max":
        levelup = machine = tutor = egg = None
        _max = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon.max_moves.any(mohacdex.db.Move.identifier==identifier)).all()
    else:
        levelup = [next(level) for move, level in itertools.groupby(levelup, lambda y: y[0])]
        machine = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon.machine_moves.any(mohacdex.db.Move.identifier==identifier)).all()
        tutor = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon.tutor_moves.any(mohacdex.db.Move.identifier==identifier)).all()
        egg = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon.egg_moves.any(mohacdex.db.Move.identifier==identifier)).all()
        _max = None
    return render_template("move.html.j2", move=move, all_flags=flags, move_flags=move_flags, efficiencies=matchups, levelup=levelup, machine=machine, tutor=tutor, egg=egg, _max=_max)

@app.route('/abilities/<identifier>')
def get_ability(identifier):
    ability = db.session.query(mohacdex.db.Ability).filter(mohacdex.db.Ability.identifier==identifier).one()
    ordinary = [a.pokemon for a in db.session.query(mohacdex.db.PokemonAbility).filter(mohacdex.db.PokemonAbility.ability==ability, mohacdex.db.PokemonAbility.slot.in_(("ability_1", "ability_2"))).all()]
    hidden = [a.pokemon for a in db.session.query(mohacdex.db.PokemonAbility).filter(mohacdex.db.PokemonAbility.ability==ability, mohacdex.db.PokemonAbility.slot=="hidden_ability").all()]
    unique = [a.pokemon for a in db.session.query(mohacdex.db.PokemonAbility).filter(mohacdex.db.PokemonAbility.ability==ability, mohacdex.db.PokemonAbility.slot=="unique_ability").all()]
    pokemon = db.session.query(mohacdex.db.Pokemon).filter(mohacdex.db.Pokemon._ability_table.any(mohacdex.db.PokemonAbility.ability_identifier==identifier)).all()
    return render_template("ability.html.j2", ability=ability, ordinary=ordinary, hidden=hidden, unique=unique)

@app.route('/types/<type_name>')
def get_type(type_name):
    moves  = db.session.query(mohacdex.db.Move).filter(mohacdex.db.Move.type==type_name).all()
    matchups = get_type_efficiencies([type_name], sides=["Damage dealt", "Damage taken"])
    return render_template("type.html.j2", type_name=type_name.title(), moves=moves, efficiencies=matchups)

def get_suggestions(search):
    results = []
    for table in [mohacdex.db.Pokemon, mohacdex.db.Move, mohacdex.db.Ability]:
        items = (
            db.session.query(table)
            .filter(table.name.like(f"%{search}%"))
            .limit(3)
        )
        for item in items:
            name = item.name
            if table == mohacdex.db.Pokemon and item.form and item.form.name:
                name += f" ({item.form.name} form)"
            results.append({"label": name, "value": item.identifier, "type": item.__tablename__})
    return results

@app.route('/suggest')
def suggest():
    query = request.args.get("q")
    return jsonify(get_suggestions(query))

@app.route('/search')
def search():
    query = request.args.get("q").lower()
    for table in [mohacdex.db.Pokemon, mohacdex.db.Move, mohacdex.db.Ability]:
        result = db.session.query(table).filter(table.name.ilike(query)).first()
        if result:
            return redirect(f"{table.__tablename__}/{result.identifier}")
    suggestions = get_suggestions(query)
    return render_template("search-results.html.j2", query=query, suggestions=suggestions)

if __name__ == "__main__":
    cache.init_app(app, config=cache_config)
    with app.app_context():
        cache.clear()
    app.run(debug=True)
