from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DateTimeLocalField, EmailField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, URL


class LoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign In")


class LogoutForm(FlaskForm):
    submit = SubmitField("Log Out")


class ForgotPasswordForm(FlaskForm):
    email = EmailField("Student email", validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField("Send Reset Instructions")


class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=80)])
    uwa_id = StringField("UWA ID", validators=[DataRequired(), Length(max=20)])
    email = EmailField("Student email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create Account")


class ProfileForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=80)])
    uwa_id = StringField("UWA ID", validators=[DataRequired(), Length(max=20)])
    program = StringField("Program / degree", validators=[Optional(), Length(max=120)])
    year_level = SelectField(
        "Year level",
        choices=[
            ("Undergraduate Year 1", "Undergraduate Year 1"),
            ("Undergraduate Year 2", "Undergraduate Year 2"),
            ("Undergraduate Year 3", "Undergraduate Year 3"),
            ("Postgraduate", "Postgraduate"),
            ("Exchange", "Exchange"),
            ("Other", "Other"),
        ],
    )
    bio = TextAreaField("About me", validators=[Optional(), Length(max=500)])
    skills = StringField("Skills / interests", validators=[Optional(), Length(max=255)])
    study_goal = StringField("Study goal", validators=[Optional(), Length(max=255)])
    availability = StringField("Availability", validators=[Optional(), Length(max=255)])
    preferred_contact = StringField("Preferred contact", validators=[Optional(), Length(max=120)])
    avatar_color = SelectField(
        "Avatar colour",
        choices=[
            ("primary", "Blue / purple"),
            ("warning", "Orange"),
            ("purple", "Purple"),
            ("success", "Green"),
            ("danger", "Red"),
        ],
    )
    show_email = BooleanField("Show my email to group members")
    submit = SubmitField("Save Profile")


class EventForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    event_type = SelectField(
        "Type",
        choices=[("Lecture", "Lecture"), ("Laboratory", "Laboratory"), ("Tutorial", "Tutorial"), ("Exam", "Exam"), ("Assignment", "Assignment"), ("Workshop", "Workshop")],
    )
    location = StringField("Location", validators=[Optional(), Length(max=100)])
    starts_at = DateTimeLocalField("Start", validators=[DataRequired()], format="%Y-%m-%dT%H:%M")
    ends_at = DateTimeLocalField("End", validators=[DataRequired()], format="%Y-%m-%dT%H:%M")
    group_visible = BooleanField("Share with group", default=True)
    submit = SubmitField("Create Event")


class ExamForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    room = StringField("Room", validators=[Optional(), Length(max=80)])
    weight = IntegerField("Weight %", validators=[Optional(), NumberRange(min=0, max=100)])
    starts_at = DateTimeLocalField("Start", validators=[DataRequired()], format="%Y-%m-%dT%H:%M")
    ends_at = DateTimeLocalField("End", validators=[DataRequired()], format="%Y-%m-%dT%H:%M")
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Save Exam")


class TopicForm(FlaskForm):
    title = StringField("Topic", validators=[DataRequired(), Length(max=180)])
    area = StringField("Area", validators=[Optional(), Length(max=80)])
    status = SelectField("Status", choices=[("Not Started", "Not Started"), ("In Progress", "In Progress"), ("Done", "Done")])
    confidence = IntegerField("Confidence", validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    submit = SubmitField("Add Topic")


class ResourceForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    kind = SelectField("Kind", choices=[("PDF", "PDF"), ("Video", "Video"), ("Docs", "Docs"), ("Link", "Link")])
    url = StringField("URL", validators=[Optional(), URL(), Length(max=255)])
    submit = SubmitField("Add Resource")


class TaskForm(FlaskForm):
    title = StringField("Task", validators=[DataRequired(), Length(max=160)])
    due_date = DateField("Due date", validators=[Optional()])
    submit = SubmitField("Add Task")


class ReminderForm(FlaskForm):
    title = StringField("Reminder", validators=[DataRequired(), Length(max=160)])
    due_at = DateTimeLocalField("Due", validators=[DataRequired()], format="%Y-%m-%dT%H:%M")
    submit = SubmitField("Save Reminder")


class CreateGroupForm(FlaskForm):
    name = StringField("Group name", validators=[DataRequired(), Length(max=120)])
    submit = SubmitField("Create Group")


class JoinGroupForm(FlaskForm):
    code = StringField("Group code", validators=[DataRequired(), Length(max=40)])
    submit = SubmitField("Join Group")
