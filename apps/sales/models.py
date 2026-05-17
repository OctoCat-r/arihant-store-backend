import mongoengine as me


class Sale(me.Document):
    id = me.StringField(primary_key=True)
    date = me.StringField(max_length=10, required=True)   # ISO date YYYY-MM-DD
    product_id = me.StringField(required=True)
    product_name = me.StringField(required=True)
    category = me.StringField(required=True)
    qty = me.IntField(default=1)
    revenue = me.IntField(default=0)
    cost = me.IntField(default=0)
    profit = me.IntField(default=0)
    customer = me.StringField(max_length=120, default='Walk-in')
    payment_method = me.StringField(max_length=20, default='UPI')

    meta = {
        'collection': 'sales',
        'indexes': [
            [('date', -1), ('category', 1)],  # covers date-range + category filter together
            'product_id',
        ],
    }

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'productId': self.product_id,
            'productName': self.product_name,
            'category': self.category,
            'qty': self.qty,
            'revenue': self.revenue,
            'cost': self.cost,
            'profit': self.profit,
            'customer': self.customer,
            'paymentMethod': self.payment_method,
        }
