import mongoengine as me


class User(me.Document):
    email = me.EmailField(required=True, unique=True)
    password_hash = me.StringField(required=True)
    name = me.StringField(max_length=120, default='')
    is_active = me.BooleanField(default=True)
    created_at = me.DateTimeField()

    meta = {
        'collection': 'users',
        'indexes': [{'fields': ['email'], 'unique': True}],
    }

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.email
