# serfetchdex
a responsive flask front-end for the mohacdex.
## usage
### set up virtualenv
```sh
$ pip install virtualenv
$ virtualenv venv
$ venv/bin/activate
$ pip install -r requirements.txt
```

### install mohacdex
in a separate directory:
```sh
$ gh clone skylar32/mohacdex
$ pip install mohacdex
$ cd /path/to/serfetchdex
$ mohacdex sqlite:///mohacdex.db load
```

### running
```sh
$ python -m flask run
```
tada! this will create a local web server to run the website on. for deployment, check out [Flask's deployment options](https://flask.palletsprojects.com/en/2.0.x/deploying/index.html).

## customization
serfetchdex uses Flask's built-in [Jinja 2](https://jinja2docs.readthedocs.io/en/stable/) templating system. modify the [templates](templates) to customize the HTML. there is only a [single CSS file](static/style.css).
the logic for getting information out of the database to actually send to the template is contained in [app.py](app.py) (a little messy, sorry). i've tried to make the database usage as intuitive if possible, but if not, try poking around the [mohacdex](https://github.com/skylar32/mohacdex). in principal, the templates should not be too hard to adapt to another data source, such as [veekun](https://github.com/veekun/pokedex) or [pokéapi](https://pokeapi.co/), if that's your wish.
