import mongoengine
import datetime

from data.bookings import Booking

class Cage(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    price = mongoengine.FloatField(required=True)
    square_meters = mongoengine.FloatField(required=True)
    is_carpeted = mongoengine.BooleanField(required=True)
    has_toys = mongoengine.BooleanField(required=True)
    allow_dangerous_snake = mongoengine.BooleanField(default=False)

    # Need to import Booking class after it is created
    bookings = mongoengine.EmbeddedDocumentListField(Booking)

    meta = {
        'db_alias': 'core',
        'collection': 'cages'
    }
