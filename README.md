# ByteBoard Forums Project

A feature-rich forum application built with Python and Django, allowing users to create discussion topics, post
messages, and interact with other users.

## Features

- **User Authentication**: Register, login, and logout functionality
- **Forum Topics**: Create and browse discussion topics
- **Sticky Topics**: Important topics can be pinned to the top of the forum
- **Posts/Replies**: Add replies to topics
- **Post Management**: Edit and delete your own posts
- **User Profiles**: View topics and posts created by specific users
- **Pagination**: Browse through topics with a paginated interface

## Technologies Used

- **Python 3.13+**: Core programming language
- **Django 5.2.1+**: Web framework
- **SQLite**: Database (default)
- **HTML/CSS**: Frontend rendering
- **Django Templates**: Server-side rendering
- **Django Authentication**: User management

## Project Structure

```
myforum_project/
├── forum/                  # Main forum application
│   ├── migrations/         # Database migrations
│   ├── static/             # Static files (CSS, JS)
│   ├── templates/          # HTML templates for forum views
│   ├── admin.py            # Admin interface configuration
│   ├── apps.py             # App configuration
│   ├── forms.py            # Form definitions
│   ├── models.py           # Data models (Topic, Post)
│   ├── tests.py            # Test cases
│   ├── urls.py             # URL routing for forum app
│   └── views.py            # View functions
├── forum_project/          # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── templates/              # Project-level templates
│   └── registration/       # Authentication templates
├── manage.py               # Django management script
├── pyproject.toml          # Project dependencies
└── README.md               # Project documentation
```

## Installation

1. Ensure you have Python 3.13 or higher installed:
   ```
   python --version
   ```

2. Clone the repository:
   ```
   git clone <repository-url>
   cd myforum_project
   ```

3. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```
   pip install -e .
   ```

5. Apply database migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the forum at http://127.0.0.1:8000/forum/

## Usage

1. **Register an Account**: Visit `/accounts/signup/` to create a new user account
2. **Login**: Visit `/accounts/login/` to log in with your credentials
3. **Browse Topics**: The forum index at `/forum/` shows all discussion topics
4. **Create a Topic**: Click "New Topic" to start a new discussion
5. **Reply to Topics**: Open a topic and use the reply form at the bottom
6. **Edit/Delete Posts**: Use the edit or delete buttons on your own posts
7. **View User Profiles**: Click on a username to see their profile

## Development

To run tests:

```
pytest
```

## License

[GNU GPL V3 (c) Michael Biel](https://github.com/MickTheLinuxGeek/ByteBoard/blob/51c381e2b461d087feb12645140b1d2789cfe78c/LICENSE)

## Contributing

[Specify contribution guidelines if applicable]