import mohacdex.db
import sqlalchemy
from mohacdex.db.base import Base

engine = sqlalchemy.create_engine("sqlite:////home/kyeugh/code/serfetchdex/mohacdex.db")
Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()

item = session.query(mohacdex.db.Item).filter(mohacdex.db.Item.identifier=="tm00").one()
print(item.move_associations)