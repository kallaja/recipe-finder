from app.db import delete_db
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

# Delete the .db file
delete_db()
