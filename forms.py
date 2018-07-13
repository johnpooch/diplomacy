from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, HiddenField, TextField, FieldList, FormField
from wtforms.validators import DataRequired

class OrderForm(FlaskForm):
    origin = HiddenField('hello')
    command = SelectField('Command', choices=[("hold", "hold"), ("move", "move"), ("support", "support"), ("convoy", "convoy")], validators=[DataRequired()])
    target = SelectField('Target', validators=[DataRequired()], choices=[])
    object = SelectField('Object', validators=[DataRequired()], choices=[])
    # submit = SubmitField('Finalise Orders', validators=[DataRequired()])
    