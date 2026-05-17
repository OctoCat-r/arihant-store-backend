import mongoengine as me


class Category(me.Document):
    id = me.StringField(primary_key=True)
    name = me.StringField(required=True, max_length=80)
    icon = me.StringField(max_length=10, default='')
    color = me.StringField(max_length=20, default='#7C3AED')

    meta = {'collection': 'categories', 'ordering': ['name'], 'indexes': ['name']}

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'icon': self.icon, 'color': self.color}


class Brand(me.Document):
    name = me.StringField(required=True, unique=True, max_length=80)

    meta = {'collection': 'brands', 'indexes': [{'fields': ['name'], 'unique': True}]}

    def to_dict(self):
        return self.name


class Product(me.Document):
    id = me.StringField(primary_key=True)
    name = me.StringField(required=True, max_length=200)
    category = me.StringField(required=True)          # references Category.id
    brand = me.StringField(required=True, max_length=80)
    stock = me.IntField(default=0, min_value=0)
    cost = me.IntField(required=True, min_value=0)
    price = me.IntField(required=True, min_value=0)
    compatible_with = me.ListField(me.StringField(), default=list)
    color = me.StringField(null=True)
    sku = me.StringField(max_length=80, default='')
    sold_30d = me.IntField(default=0)
    rating = me.FloatField(default=4.0)
    added_date = me.StringField(max_length=10, default='')  # ISO date string
    low_stock_threshold = me.IntField(default=5)
    image = me.StringField(null=True)

    meta = {
        'collection': 'products',
        'indexes': [
            'name',                              # default sort, unfiltered listing
            'category',
            'brand',
            'stock',
            'price',
            'sold_30d',                          # sales sort
            'compatible_with',
            {'fields': ['sku'], 'unique': True, 'sparse': True},
            {'fields': ['category', 'name']},    # category filter + name sort
            {'fields': ['category', 'price']},   # category filter + price sort
            {'fields': ['category', 'stock']},   # category filter + stock sort
        ],
    }

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'stock': self.stock,
            'cost': self.cost,
            'price': self.price,
            'compatibleWith': self.compatible_with,
            'color': self.color,
            'sku': self.sku,
            'sold30d': self.sold_30d,
            'rating': round(self.rating, 2),
            'addedDate': self.added_date,
            'lowStockThreshold': self.low_stock_threshold,
            'image': self.image,
        }
