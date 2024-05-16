# Patient Management System
This is a Patient Management System built using FastAPI for the backend and Jinja2 for server-side rendering of HTML templates. It includes features for managing patients, appointments, and users, with endpoints to create, read, update, and delete records. The system ensures data validation, user authentication, and secure password handling. The project aims to provide an efficient, user-friendly interface for handling patient and appointment information in a healthcare setting.

To run this application on a local setting, follow these steps:
1. Clone the repository.
2. Pull the repository to local environment.
3. Start your virtual environment.
4. Install the dependencies in Requirements.txt file using command: `pip install -r requirements.txt`.
5. cd to FastAPI directory.
6. Edit the `SQLALCHEMY_DATABASE_URL` in `database.py` by typing your postgreSQL username and password.
7. Edit the `STRIPE_API_KEY` in `config.py` by getting a test api key from stripe.
8. Run the command: `uvicorn main:app --reload` to start the application.
9. The application will start running on localhost. Go to `/docs` to check the endpoints.

I have made this application from scratch and tried my level best to keep the front end user-friendly and code easily understandable. I hope you will enjoy the project!!
