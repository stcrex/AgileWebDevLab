# StudySync

StudySync is a Flask web application for university students who need one place to manage timetables, exams, revision plans, reminders, and group project collaboration.

The design is based on a dark StudySync dashboard with:

- Login and registration
- Weekly timetable with event creation
- Exam and task tracker
- Revision progress dashboard
- Topic checklist with AJAX updates
- Resource links for each exam
- Personal notes
- Rule-based AI study planner chat
- Group page showing member progress, shared tasks, and common free slots
- Messenger for direct student-to-student messages
- Group chat room for project-wide discussion
- Student profile pages for each group member
- Student directory with search, skills, availability and profile actions
- Logout and profile/preferences page

## Group Members

These are demo names used in project not real names.

| UWA ID | Name | GitHub Username |
|---|---|---|
| 23456789 | Jane Smith | jane-demo |
| 23112233 | Tom Liu | tom-demo |
| 23888881 | Amy Kim | amy-demo |
| 23777774 | Ryan Zhang | ryan-demo |

## Technologies Used

- HTML5
- CSS3
- JavaScript with Fetch/AJAX
- Bootstrap 5
- Flask
- Jinja templates
- Flask-Login
- Flask-WTF CSRF protection
- Flask-SQLAlchemy
- SQLite
- Flask-Migrate
- Pytest
- Selenium

No React, Angular, MySQL, Sass, or disallowed core technologies are used.

## Main Features

### 1. Authentication
Users can create an account, log in, and log out. Passwords are stored as salted hashes using Werkzeug, not plain text.

### 2. Persistent User Data
Timetable events, exams, reminders, AI chat messages, direct messenger messages, group chat messages, profile details, topics, resources, and group tasks are stored in SQLite through SQLAlchemy models.

### 3. Timetable
The timetable page shows a weekly grid with lectures, labs, tutorials, exams, assignments, and workshops. It now uses 15-minute time slots so events line up correctly with their real start/end times. Users can move to previous/future weeks, click any timetable event to view full details, delete events from the detail modal, filter by event type, and create new events through a Bootstrap modal form. After a new event is saved, the timetable automatically opens the correct week so the event is visible immediately.

### 4. Exams & Revision Tracker
Each exam has a detail page with:

- Exam date, time, room, and weighting
- Countdown timer
- Revision progress by topic area
- Topic checklist
- Resources
- Personal notes
- AI study suggestion panel

### 5. AJAX Interactions
The application uses JavaScript Fetch/AJAX for:

- Marking revision topics as done/in progress
- Sending AI planner chat messages
- Updating group task status
- Toggling reminders
- Sending and refreshing student-to-student messenger messages
- Sending and refreshing project group chat messages
- Saving profile updates with AJAX
- Filtering the student directory in the browser

### 6. AI Planner With Paid API Keys
The AI planner is implemented as a rule-based backend recommender. It reads the student's weak topics from the database and generates a practical study plan. This needs paid Claude/OpenAI API credits while still demonstrating backend logic and personalised responses.

### 7. Group Collaboration
The group page lets users view other group members' progress, shared project tasks, and common free meeting slots. This satisfies the requirement that users can view data from other users.

### 8. Student Messenger

The Messenger page lets students send one-to-one messages to other members of their project group. Messages are saved in the database using the `DirectMessage` model and loaded through AJAX without refreshing the page. The backend checks that the receiver belongs to the same group before allowing a message to be sent.

### 9. Security
Security features include:

- Hashed passwords
- Login-required routes
- CSRF tokens for forms and AJAX requests
- Environment variables through `.env`
- Database access through SQLAlchemy models instead of raw SQL in routes

## User Stories

1. As a student, I want to register an account so that my timetable is saved.
2. As a student, I want to log in and log out so that my data is private.
3. As a student, I want to add timetable events so that I can track weekly classes.
4. As a student, I want to see upcoming exams so that I know what to prepare for.
5. As a student, I want to track revision topics so that I can identify weak areas.
6. As a student, I want to mark topics as complete without reloading the page so that the app feels fast.
7. As a student, I want a study plan generated from weak topics so that I can revise efficiently.
8. As a student, I want to save exam notes so that I can quickly review important points.
9. As a group member, I want to see my teammates' progress so that we can coordinate project work.
10. As a group member, I want to update project task statuses so that the group knows what is done.
11. As a student, I want reminders so that I do not forget exams or group meetings.
12. As a student, I want a polished mobile-responsive interface so that I can use it on different screens.
13. As a group member, I want to send direct messages to teammates so that we can coordinate project work quickly.
14. As a group member, I want a shared group chat room so that the whole team can coordinate checkpoint work and project tasks.
15. As a student, I want to create a profile with my skills and availability so that teammates know how to collaborate with me.
16. As a group member, I want to view teammate profiles so that I can message the right person for a project task.

## Folder Structure

```text
studysync/
├── app/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── api.py
│   ├── static/
│   │   ├── css/styles.css
│   │   └── js/
│   │       ├── app.js
│   │       ├── ai.js
│   │       ├── exam.js
│   │       ├── group.js
│   │       ├── messages.js
│   │       ├── group_chat.js
│   │       └── profile.js
│   ├── templates/
│   │   ├── auth/login.html
│   │   ├── base.html
│   │   └── pages/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── forms.py
│   ├── models.py
│   └── seed.py
├── tests/
│   ├── test_core.py
│   └── selenium/test_ui.py
├── migrations/README.md
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### 1. Create and activate a virtual environment

Windows PowerShell:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the database with demo data

```bash
flask --app run.py init-db
```

### 4. Run the application

```bash
flask --app run.py run
```

Open:

```text
http://127.0.0.1:5000
```

Demo login:

```text
Email: you@student.uwa.edu.au
Password: password123
```

## Running Tests

### Unit tests

```bash
pytest tests/test_core.py
```

### Selenium tests

Start the server first:

```bash
flask --app run.py init-db
flask --app run.py run
```

Then open a second terminal and run:

```bash
RUN_SELENIUM=1 pytest tests/selenium
```

On Windows PowerShell:

```bash
$env:RUN_SELENIUM="1"
pytest tests/selenium
```

## Database Migrations

Flask-Migrate is already configured. If you want to generate migrations:

```bash
flask --app run.py db init
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
```

## GitHub Workflow Recommendation

Use this workflow to show Agile development:

1. Create GitHub issues for each feature or bug.
2. Create a branch for each issue.
3. Commit small, meaningful changes.
4. Open a pull request.
5. Ask a teammate to review it.
6. Merge only after review.

Example commit messages:

```bash
git commit -m "Add login and registration forms"
git commit -m "Implement AJAX topic status updates"
git commit -m "Add unit tests for AI planner endpoint"
```

## Presentation Talking Points

- StudySync solves student time-management and group-collaboration problems.
- The backend is Flask with a proper app factory structure.
- SQLAlchemy models store users, events, exams, topics, resources, reminders, groups, tasks, direct messages, group chat messages, and student profiles.
- Passwords are hashed and forms use CSRF protection.
- AJAX is used for interactive topic/task/reminder updates, AI chat, student-to-student messenger messages, group chat messages, and profile updates.
- The AI planner does rely on paid external APIs; it reads database progress and generates a personalised plan.
- The project includes more than five Pytest tests and five Selenium UI test cases.
- The UI is responsive and uses Bootstrap plus custom CSS.

## UWA Handbook Catalogue Feature

The project now includes a local UWA Handbook subject catalogue.

### What it does

- Adds a new **UWA Handbook** page in the sidebar.
- Stores official-style Handbook unit records in the SQLite database through the `HandbookSubject` model.
- Lets students search by unit code, title, coordinator, school or field of education.
- Lets students filter by semester, level and school.
- Lets students click **Add to Courses**, which uses AJAX to save that unit into their personal StudySync course list.
- Includes a bundled 2026 seed catalogue so the feature works even without internet during the demo.
- Includes a refresh importer that can download/parse current public UWA Handbook search results.

### Refreshing Handbook units

The database is seeded automatically when you run:

```bash
flask --app run.py init-db
```

To refresh the Handbook catalogue from UWA public search pages, run either:

```bash
flask --app run.py import-uwa-handbook
```

or:

```bash
python scripts/import_uwa_handbook.py
```

The importer uses UWA Handbook unit search pages and stores the results locally, so the app can search quickly without repeatedly calling the website.


## Messenger Feature

The project includes a direct messaging system between students.

### What it does

- Adds a new **Messenger** page in the sidebar.
- Shows all students in the current user's group as contacts.
- Stores every message in SQLite using the `DirectMessage` model.
- Uses AJAX to send messages without refreshing the page.
- Uses AJAX polling to refresh the open conversation every few seconds.
- Shows unread message counts.
- Protects the route so users can only message students in their own group.

## Group Chat Feature

The project also includes a shared group chat room for group project coordination.

### What it does

- Adds a new **Group Chat** page in the sidebar.
- Displays the current project group name, group code, and all group members.
- Stores every chat message in SQLite using the `GroupMessage` model.
- Uses AJAX to send messages without refreshing the page.
- Uses AJAX polling to refresh the room every few seconds.
- Protects the backend so only logged-in students who belong to a group can post.
- Gives a clear demonstration of user-to-user interaction and persisted group data.

## Student Profile Feature

The project includes full student profile pages for both the logged-in user and other students in the same project group.

### What it does

- Adds a new **My Profile** page where the logged-in user can edit their name, UWA ID, program, year level, bio, skills, study goal, availability, preferred contact method, avatar colour, and email visibility.
- Adds a **Student Profiles** directory page showing all group members.
- Adds individual public profile pages at `/students/<id>`.
- Uses the existing `User` model with additional profile fields, so profile information is persisted between sessions.
- Uses AJAX on the profile page through `/api/profile` so the user can quick-save profile changes without a full page refresh.
- Protects student profile pages so users can only view students who belong to their own group.
- Links profiles to Messenger so a user can quickly contact a teammate.

### Authentication pages

StudySync includes a complete authentication flow:

- `/login` — dedicated login page with demo login and quick create-account tab.
- `/register` — full student account creation page.
- `/logout` — confirmation page that logs out using a CSRF-protected POST form instead of a plain logout link.

This supports the project requirement that users can login and logout, while also demonstrating good security practice for session handling.


## Fully wired button actions

The latest version connects the visible buttons to real frontend/backend behaviour:

- **Forgot password** opens a reset request page.
- **AI Planner → Clear** deletes saved chat history from the database.
- **AI Planner → History** loads saved AI messages from `/api/ai/history`.
- **Exam Detail → Share** generates a shareable exam summary and copies it to the clipboard.
- **My Group → Invite Member** prepares an invite, copies the invite text, and records the action in group chat.
- **Common Free Slot → Book** creates group study events for the project group and posts a group chat announcement.
- **Task status dropdowns** save instantly through AJAX.
- **Reminder check buttons** toggle completion through AJAX.


## AI Planner Fix / How the AI Works

The AI Planner doesn't return one default message. The backend endpoint `/api/ai/message` now reads the logged-in user's exams, revision topics, timetable events, reminders and group tasks from SQLite using SQLAlchemy, then generates a contextual response.

Supported prompts include:

- `Generate my study plan`
- `What are my weak topics?`
- `Give me one MCQ practice question`
- `What group tasks are pending?`
- `Explain SQLAlchemy relationships`
- `What should I study today?`

By default it uses the built-in local study planner, so the project works with and without paid API keys. It can also support open AI keys.

Start an OpenAI-compatible local server in LM Studio, then run the Flask app.

### Course card buttons and details

The **Courses** page is now interactive:

- Click any course card to open a quick details modal.
- Use **Details** to open a full course page.
- Use **Event** to create a lecture/lab/tutorial/workshop linked to that course.
- Use **Exam** to create a course exam linked to Exams & Tasks.
- New course events are saved in SQLite and then appear automatically in the Timetable.

## UI polish update

This version includes an upgraded user interface layer:

- animated aurora background and soft grain overlay
- glassmorphism cards with hover glow
- reveal-on-scroll page animations
- ripple effects on buttons, navigation items and filter chips
- subtle 3D tilt effect on important cards
- animated gradient buttons and improved progress-bar shine
- polished timetable/event cards, modals, chat bubbles, profile cards and login page
- custom dark scrollbars and stronger visual hierarchy for demo presentation

These effects are implemented with plain CSS and JavaScript only, so they stay within the allowed project technology stack.

## Latest usability fixes

This build includes a final timetable and modal usability patch:

- Close buttons now use a hard cleanup helper, so Invite/Create/Event Detail modals do not get stuck behind a dark overlay.
- The timetable has explicit scroll buttons for left, right, earlier time, later time, and jump-to-9-AM.
- The timetable panel has its own scroll area with mouse-wheel/touchpad support.
- Shift + mouse wheel scrolls the timetable sideways.
- The Create Event button uses the same safe modal helper, and saved events still appear in the correct week.
