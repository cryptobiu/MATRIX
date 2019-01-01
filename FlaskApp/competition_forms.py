from wtforms import Form, StringField, validators
from wtforms.fields.html5 import DateTimeField


class CompetitionForm(Form):
    name = StringField('Name', [validators.length(min=4, max=50)])
    description = StringField('Description', [validators.length(min=10)])
    start_date = DateTimeField('Start Date', [validators.DataRequired()])
    end_date = DateTimeField('End Date', [validators.DataRequired()])
    status = StringField('Status', [validators.DataRequired()])


class CompetitionRegistrationForm(Form):
    address = StringField('Git Address', [validators.DataRequired('Please supply address to your public repository')])
    sanity_file = StringField('Sanity file', [validators.DataRequired('Please supply address to your sanity file')])