def deploy():
	"""Run deployment tasks."""
	from app import create_app,bcrypt

	app = create_app()
	app.app_context().push()

	from models import Role,User
	from app import db
	from flask_migrate import upgrade,migrate,init,stamp
	db.create_all()

	# create user roles
	Role.insert_roles()

	# migrate database to latest revision
	stamp()
	migrate()
	upgrade()
	
deploy()
	