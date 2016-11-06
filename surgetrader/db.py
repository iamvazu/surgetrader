from pydal import DAL, Field
from datetime import datetime

db = DAL('sqlite://download.db')

market = db.define_table(
    'market',
    Field('name'),
    Field('ask', type='double'),
    Field('timestamp', type='datetime', default=datetime.now)
    )

buy = db.define_table(
    'buy',
    Field('market'),
    Field('purchase_price', type='double'),
    Field('selling_price', type='double'),
    Field('amount', type='double'),
    )
