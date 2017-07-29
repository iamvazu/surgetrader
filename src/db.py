from pydal import DAL, Field
from datetime import datetime

db = DAL('sqlite://download.db')

market = db.define_table(
    'market',
    Field('name'),
    Field('ask', type='double'),
    Field('timestamp', type='datetime', default=datetime.now)
    )
db.executesql('CREATE INDEX IF NOT EXISTS tidx ON market (timestamp);')
db.executesql('CREATE INDEX IF NOT EXISTS m_n_idx ON market (name);')

buy = db.define_table(
    'buy',
    Field('market'),
    Field('purchase_price', type='double'),
    Field('selling_price', type='double'),
    Field('amount', type='double'),
    )
db.executesql('CREATE INDEX IF NOT EXISTS sidx ON buy (selling_price);')

picks = db.define_table(
    'picks',
    Field('market'),
    Field('old_price', type='double'),
    Field('new_price', type='double'),
    Field('gain', type='double'),
    Field('timestamp', type='datetime', default=datetime.now)
    )
