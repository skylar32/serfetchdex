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

{% macro type_chart(efficiencies) %}
<span class="type-efficiencies">
    {% for side in efficiencies %}
    <span class="side">
        <h3>{{ side }}</h3>
            <table>
                {% for efficiency in efficiencies[side] %}
                <tr>
                    <th>{{ efficiency }}:</th>
                    <td>
                        <ul>
                            {% if efficiencies[side][efficiency] %}
                            {% for type in efficiencies[side][efficiency] %}
                            <li><a href="/types/{{type}}"><span class="type-bar-small {{type}}" alt="{{type|title}}" title="{{type|title}}" /></span></a></li>
                            {% endfor %}
                            {% else %}<li>N/A</li>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
    </span>
    {% endfor %}
</span>
{% endmacro %}