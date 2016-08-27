import jsl
import json

iso_dates = ['YYYYMMDD', 'YYYY-MM-DD', 'YYYY-MM']
iso_times = ['hh:mm', 'hhmm']

all_iso = iso_dates + iso_times + ['{d}T{t}'.format(d=d, t=t)
                                   for d in iso_dates[:2]
                                   for t in iso_times]


class MOBaseField(jsl.Document):
    name = jsl.StringField(required=True, description='Title of the header row of this field')
    description = jsl.StringField(description='Data dictionary entry for this field')
    nullable = jsl.BooleanField(description='Must be present and set to False for this field to be blank')


class MOStringField(MOBaseField):
    type = jsl.StringField(enum=['string'], required=True, description='Data type identifier')
    size = jsl.IntField(minimum=1, required=True, description='Maximum number of code points in string')


class MODateField(MOBaseField):
    type = jsl.StringField(enum=['date'], required=True, description='Data type identifier')
    pattern = jsl.StringField(enum=all_iso,
                              description="subset of ISO 8601 allowed formats date format")


class MOIntegerField(MOBaseField):
    type = jsl.StringField(enum=['integer'], required=True, description='Data type identifier')
    bytes = jsl.IntField(minimum=1, maximum=8,
                         required=True,
                         description='Number of bytes needed to store value. Not the number of bytes/characters of text')


class MOBooleanField(MOBaseField):
    type = jsl.StringField(enum=['boolean'], required=True, description='Data type identifier')
    size = jsl.IntField(minimum=1, required=True, description='Number of code points represented in text')
    true_value = jsl.StringField(required=True, description='The textual representation of TRUE')
    false_value = jsl.StringField(required=True, description='The textual representation of FALSE')


class MODecimalField(MOBaseField):
    type = jsl.StringField(enum=['boolean'], required=True, description='Data type identifier')
    precision = jsl.IntField(minimum=1, required=True,
                             description='Total number of digits. E.g. 123.45 has a precision of 5')
    scale = jsl.IntField(minimum=1, required=True,
                         description='Total number of digits representing numbers less than one. '
                                     'E.g. 123.45 has a scale of 2')


class MOForeignKeyMetaData(jsl.Document):
    schema = jsl.StringField(description='If a field is described in a different schema document, '
                                         'the name of that schema')
    table = jsl.StringField(required=True, description='The name of a table where the key is found')
    type = jsl.StringField(enum=['foreign_key'], required=True, description='Data type identifier')
    field = jsl.StringField(required=True, description='The name of the field in the foreign table')


class MOForeignKeyField(jsl.Document):
    name = jsl.StringField(required=True, description='Title of the header row of this field')
    foreign_key = jsl.DocumentField(MOForeignKeyMetaData)


class MOTable(jsl.Document):
    name = jsl.StringField(required=True, description='Name of the table')
    file_name_prefix = jsl.StringField(required=True, description='The file name prefix used for this table.')
    description = jsl.StringField(description='Data dictionary entry for this table')
    primary_key = jsl.OneOfField([jsl.StringField(), jsl.BooleanField(enum=[False])],
                                 description='The name of the primary key of this table '
                                             'or false if the table fails to have one')
    fields = jsl.ArrayField(jsl.OneOfField([jsl.DocumentField(MOStringField, as_ref=True),
                                            jsl.DocumentField(MODateField, as_ref=True),
                                            jsl.DocumentField(MOIntegerField, as_ref=True),
                                            jsl.DocumentField(MOBooleanField, as_ref=True),
                                            jsl.DocumentField(MODecimalField, as_ref=True),
                                            jsl.DocumentField(MOForeignKeyField, as_ref=True)]),
                            required=True,
                            min_items=1,
                            description='The ordered list of fields as they will appear in the file')


class MediaOceanFileExtractSchema(jsl.Document):
    schema = jsl.StringField(required=True, description='The name of the schema')
    description = jsl.StringField(description='Data dictionary entry for this schema')
    tables = jsl.ArrayField(jsl.DocumentField(MOTable), min_items=1, required=True,
                            description='A list of files and the associated tables within this schema')


with open("mediaocean_fileschemas.json", mode='wt') as fout:
    json.dump(MediaOceanFileExtractSchema.get_schema(), fout)