import json

from django.db import models


class ModelIdArrayField(models.Field):
    def __init__(self, model_class, *args, **kwargs):
        self.model_class = model_class
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return []
        serialized_data = json.loads(value)
        return [self.model_class.deserialize(item) for item in serialized_data]

    def to_db_value(self, value, expression, connection):
        return json.dumps([item.serialize() for item in value])

    def get_prep_value(self, value):
        return self.to_db_value(value, None, None)

    def db_type(self, connection):
        return 'text'

    def value_from_object(self, obj):
        value = super().value_from_object(obj)
        return self.get_db_prep_value(value, connection=None)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['model_class'] = self.model_class
        return name, path, args, kwargs

    def last(self, obj):
        value = self.value_from_object(obj)
        return value[-1] if value else None
