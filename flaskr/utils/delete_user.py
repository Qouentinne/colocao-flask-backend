import os
import sys
print(sys.path)
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User

def main():
    # Get user ID from command line arguments
    user_id = str(sys.argv[1])
    if not user_id:
        print("Script requires a user ID as argument.")
        return
    try:
        user_id = user_id
    except ValueError:
        pass

    # Connect to database
    db_uri = 'postgresql://'+os.getenv('SUPABASE_USER')+':'+os.getenv(urllib.parse.quote_plus('SUPABASE_PWD'))+'@'+os.getenv('SUPABASE_HOST')+':5432/postgres'
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Delete user with given ID
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        session.delete(user)
        session.commit()
        print(f"User with ID {user_id} deleted successfully.")
    else:
        print(f"No user found with ID {user_id}.")

if __name__ == '__main__':
    main()
