from app import db, User

# Создание пользователя
manager = User(username='manager', password='manager_password', role='manager')
director = User(username='director', password='director_password', role='director')

db.session.add(manager)
db.session.add(director)
db.session.commit()
