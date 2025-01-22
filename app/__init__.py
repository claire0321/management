from app.authorization.hashing import bcrypt
from app.databases import role_model, user_model, database


def initialize_data():
    db = database.SessionLocal()
    try:
        if not db.query(role_model.Role).count():
            roles = [
                role_model.Role(name="admin", description="admin role ( create, read, update, delete )"),
                role_model.Role(name="manager", description="manager role ( create, read, update, delete )"),
                role_model.Role(name="general", description="general role ( read )"),
            ]
            db.add_all(roles)
            db.commit()

        if not db.query(user_model.User).count():
            users = [
                user_model.User(
                    username="admin", password=bcrypt("admin"), email="admin@example.com", role_id=1
                ),
                user_model.User(
                    username="manager", password=bcrypt("manager"), email="manager@example.com", role_id=2
                ),
                user_model.User(
                    username="general", password=bcrypt("general"), email="general@example.com", role_id=3
                ),
            ]
            db.add_all(users)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error initializing data: {e}")
    finally:
        db.close()
