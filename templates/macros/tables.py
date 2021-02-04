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
                <td><a href="/types/{{move.type}}"><span class="type-badge {{move.type}}" alt="{{move.type|title}}-type move" title="{{move.type|title}}-type move"></span></a></td>
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

{% macro pokemon_table(pokemon) %}
    <table class="pokemonlist tablelist">
        <thead>
            <tr>
                <th>&nbsp;</th>
                <th onclick="onColumnHeaderClicked(event)">Pokémon</th>
                <th onclick="onColumnHeaderClicked(event)">Type</th>
                <th onclick="onColumnHeaderClicked(event)">Abilities</th>
                <th onclick="onColumnHeaderClicked(event)">Hidden Ability</th>
                <th onclick="onColumnHeaderClicked(event)">HP</th>
                <th onclick="onColumnHeaderClicked(event)">Atk</th>
                <th onclick="onColumnHeaderClicked(event)">Def</th>
                <th onclick="onColumnHeaderClicked(event)">Sp.Atk</th>
                <th onclick="onColumnHeaderClicked(event)">Sp.Def</th>
                <th onclick="onColumnHeaderClicked(event)">Spe</th>
            </tr>
        </thead>
        {% for mon in pokemon %}{% if not mon.form or mon.form.display_separately==True %}
            <tr>
                <td><span class="party-sprite {{ mon.identifier }}"></span></td>
                <td><a href="/pokemon/{{mon.identifier}}">{{ mon.name }}
                    {% if mon.form and mon.form.name %}<br /><small>{{ mon.form.name }} Form</small>{% endif %}
                </a></td>
                <td>{% for type in mon.types %}{% if type %}
                    <a href="/types/{{ type }}">
                        <span class="type-bar-small {{ type }}" alt="{{ type|title }} type" title="{{ type|title }} type"></span>
                    </a>{% endif %}{% endfor %}
                </td>
                <td>
                    <ul>
                        {% for slot in mon.abilities %}{% if slot != "hidden_ability" %}{% for ability in mon.abilities[slot] %}
                        <li><a href="/abilitles/{{ability.identifier}}">{{ ability.name }}</a></li>
                        {% endfor %}{% endif %}{% endfor %}
                    </ul>
                </td>
                <td>{% if mon.abilities["hidden_ability"] %}
                    <a href="/abilities/{{mon.abilities['hidden_ability'][0].identifier}}"><em>{{ mon.abilities["hidden_ability"][0].name }}</em></a>
                {% endif %}</td>
                {% for stat in mon.stats %}<td>{{ mon.stats[stat] }}</td>{% endfor %}
            </tr>
        {% endif %}{% endfor %}
    </table>
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