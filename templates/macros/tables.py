{% macro move_table(moves) %}
    <table class="movelist tablelist">
        <thead>
            <tr>
                <th onclick="onColumnHeaderClicked(event)">Move</th>
                <th onclick="onColumnHeaderClicked(event)">Type</th>
                <th onclick="onColumnHeaderClicked(event)">Class</th>
                <th onclick="onColumnHeaderClicked(event)"><span>Power</span><span>Pwr</span></th>
                <th onclick="onColumnHeaderClicked(event)">Acc</th>
                <th onclick="onColumnHeaderClicked(event)">PP</th>
                <th onclick="onColumnHeaderClicked(event)">Pri</th>
            </tr>
        </thead>
        <tbody>
        {% for move in moves %}
            <tr>
                <td><a href="/moves/{{move.identifier}}">{{move.name}}</a></td>
                <td><a href="/types/{{move.type}}"><span class="type-dynamic {{move.type}}" alt="{{move.type|title}}-type move" title="{{move.type|title}}-type move"></span></a></td>
                <td><span class="damage-icon {{move.damage_class}}" alt="{{move.damage_class|title}} move" title="{{move.damage_class|title}} move"></span></td>
                <td>{%if move.power%}{{move.power}}{%else%}—{%endif%}</td>
                <td>{%if move.accuracy%}{{move.accuracy}}%{%else%}—{%endif%}</td>
                <td>{{move.pp}}</td>
                <td>{{move.priority}}</td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
{% endmacro %}

{% macro levelup_table(moves) %}
    <table class="movelist tablelist leveluplist">
        <thead>
            <tr>
                <th onclick="onColumnHeaderClicked(event)">Lvl.</th>
                <th onclick="onColumnHeaderClicked(event)">Move</th>
                <th onclick="onColumnHeaderClicked(event)">Type</th>
                <th onclick="onColumnHeaderClicked(event)">Class</th>
                <th onclick="onColumnHeaderClicked(event)"><span>Power</span><span>Pwr</span></th>
                <th onclick="onColumnHeaderClicked(event)">Acc</th>
                <th onclick="onColumnHeaderClicked(event)">PP</th>
                <th onclick="onColumnHeaderClicked(event)">Pri</th>
            </tr>
        </thead>
        <tbody>
        {% for level in moves %}{% for move in moves[level] %}
            <tr>
                <td>{{ level }}</td>
                <td><a href="/moves/{{move.identifier}}">{{move.name}}</a></td>
                <td><a href="/types/{{move.type}}"><span class="type-dynamic {{move.type}}" alt="{{move.type|title}}-type move" title="{{move.type|title}}-type move"></span></a></td>
                <td><span class="damage-icon {{move.damage_class}}" alt="{{move.damage_class|title}} move" title="{{move.damage_class|title}} move"></span></td>
                <td>{%if move.power%}{{move.power}}{%else%}—{%endif%}</td>
                <td>{%if move.accuracy%}{{move.accuracy}}%{%else%}—{%endif%}</td>
                <td>{{move.pp}}</td>
                <td>{{move.priority}}</td>
            </tr>
        {% endfor %}{% endfor %}
        </tbody>
    </table>
{% endmacro %}

{% macro pokemon_level_table(pokemon) %}
<span class="poketable-wrapper">
    <table class="pokemonlist tablelist">
        <thead>
            <tr>
                <th class="level-cell" onclick="onColumnHeaderClicked(event)">Lvl.</th>
                <th class="party-sprite-cell">&nbsp;</th>
                <th class="pokemon-name-cell" onclick="onColumnHeaderClicked(event)">Pokémon</th>
                <th class="pokemon-type-cell" onclick="onColumnHeaderClicked(event)">Type</th>
                <th class="abilities-cell" onclick="onColumnHeaderClicked(event)">Abilities</th>
                <th class="hidden-ability-cell" onclick="onColumnHeaderClicked(event)">Hidden Ability</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">HP</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">Atk</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">Def</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">SpA</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">SpD</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">Spe</th>
            </tr>
        </thead>
        {% for mon in pokemon %}{% if not mon[0].form or mon[0].form.display_separately==True %}
            <tr>
                <td class="level-cell">{{ mon[1] }}
                <td class="party-sprite-cell"><span class="party-sprite {{ mon[0].identifier }}"></span></td>
                <td class="pokemon-name-cell"><a href="/pokemon/{{mon[0].identifier}}">{{ mon[0].name }}
                    {% if mon[0].form and mon[0].form.name %}<br /><small>{{ mon[0].form.name }} Form</small>{% endif %}
                </a></td>
                <td class="pokemon-type-cell">{% for type in mon[0].types %}{% if type %}
                    <a href="/types/{{ type }}">
                        <span class="type-dynamic {{ type }}" alt="{{ type|title }} type" title="{{ type|title }} type"></span>
                    </a>{% endif %}{% endfor %}
                </td>
                <td class="abilities-cell">
                    <ul>
                        {% for slot in mon[0].abilities %}{% if slot != "hidden_ability" %}{% for ability in mon[0].abilities[slot] %}
                        <li><a href="/abilities/{{ability.identifier}}">{{ ability.name }}</a></li>
                        {% endfor %}{% endif %}{% endfor %}
                    </ul>
                </td>
                <td class="hidden-ability-cell">{% if mon[0].abilities["hidden_ability"] %}
                    <ul>
                        <li><a href="/abilities/{{mon[0].abilities['hidden_ability'][0].identifier}}"><em>{{ mon[0].abilities["hidden_ability"][0].name }}</em></a></li>
                    </ul>
                {% endif %}</td>
                {% for stat in mon[0].stats %}<td class="pokemon-stat-cell {{ stat|lower }}">{{ mon[0].stats[stat].base_stat }}</td>{% endfor %}
            </tr>
        {% endif %}{% endfor %}
    </table>
</span>
{% endmacro %}

{% macro pokemon_table(pokemon) %}
<span class="poketable-wrapper">
    <table class="pokemonlist tablelist">
        <thead>
            <tr>
                <th class="party-sprite-cell">&nbsp;</th>
                <th class="pokemon-name-cell" onclick="onColumnHeaderClicked(event)">Pokémon</th>
                <th class="pokemon-type-cell" onclick="onColumnHeaderClicked(event)">Type</th>
                <th class="abilities-cell" onclick="onColumnHeaderClicked(event)">Abilities</th>
                <th class="hidden-ability-cell" onclick="onColumnHeaderClicked(event)">Hidden Ability</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">HP</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">Atk</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">Def</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">SpA</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">SpD</th>
                <th class="pokemon-stat-cell" onclick="onColumnHeaderClicked(event)">Spe</th>
            </tr>
        </thead>
        {% for mon in pokemon %}{% if not mon.form or mon.form.display_separately==True %}
            <tr>
                <td class="party-sprite-cell"><span class="party-sprite {{ mon.identifier }}"></span></td>
                <td class="pokemon-name-cell"><a href="/pokemon/{{mon.identifier}}">{{ mon.name }}
                    {% if mon.form and mon.form.name %}<br /><small>{{ mon.form.name }} Form</small>{% endif %}
                </a></td>
                <td class="pokemon-type-cell">{% for type in mon.types %}{% if type %}
                    <a href="/types/{{ type }}">
                        <span class="type-dynamic {{ type }}" alt="{{ type|title }} type" title="{{ type|title }} type"></span>
                    </a>{% endif %}{% endfor %}
                </td>
                <td class="abilities-cell">
                    <ul>
                        {% for slot in mon.abilities %}{% if slot != "hidden_ability" %}{% for ability in mon.abilities[slot] %}
                        <li><a href="/abilities/{{ability.identifier}}">{{ ability.name }}</a></li>
                        {% endfor %}{% endif %}{% endfor %}
                    </ul>
                </td>
                <td class="hidden-ability-cell">{% if mon.abilities["hidden_ability"] %}
                   <ul>
                        <li><a href="/abilities/{{mon.abilities['hidden_ability'][0].identifier}}"><em>{{ mon.abilities["hidden_ability"][0].name }}</em></a></li>
                    </ul>
                {% endif %}</td>
                {% for stat in mon.stats %}<td class="pokemon-stat-cell {{ stat|lower }}">{{ mon.stats[stat].base_stat }}</td>{% endfor %}
            </tr>
        {% endif %}{% endfor %}
    </table>
</span>
{% endmacro %}

{% macro type_chart(efficiencies) %}
<section class="type-efficiencies">
    {% for side in efficiencies %}
    <span class="side">
            <table>
                <thead>
                    <th colspan="2"><h3>{{ side }}</h3></th>
                </thead>
                {% for efficiency in efficiencies[side] %}
                <tr>
                    <th>{{ efficiency }}:</th>
                    <td>
                        <ul>
                            {% if efficiencies[side][efficiency] %}
                            {% for type in efficiencies[side][efficiency] %}
                            <li><a href="/types/{{type}}"><span class="type-bar-small {{type}}" alt="{{type|title}}" title="{{type|title}}" /></span></a></li>
                            {% endfor %}
                            {% else %}<li style="color: #cccbc3">N/A</li>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
    </span>
    {% endfor %}
</section>
{% endmacro %}