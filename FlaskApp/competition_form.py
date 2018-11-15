from wtforms import Form, StringField, validators
from wtforms.fields.html5 import DateTimeField


class CompetitionForm(Form):
    name = StringField('Name', [validators.length(min=4, max=50)])
    description = StringField('Description', [validators.length(min=10)])
    start_date = DateTimeField('Start Date', [validators.DataRequired()])
    end_date = DateTimeField('End Date', [validators.DataRequired()])
    status = StringField('Status', [validators.DataRequired()])


