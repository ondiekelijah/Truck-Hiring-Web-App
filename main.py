from flask import Blueprint
from flask import current_app
from main_app import create_app
from main_app import login_manager
from models import *
from forms import *
from utils import *
from decorators import admin_required, moderator_required, permission_required

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for,
    abort,
)
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
from werkzeug.routing import BuildError
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from PIL import Image

app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------------------- MAIN APP ROUTES -----------------------------

# Home
@app.route("/", methods=("GET", "POST"), strict_slashes=False)
@login_required
def index():
    trucks = Trucks.query.order_by(Trucks.id.desc()).all()
    return render_template("index.html",title="Mtruck | Home",trucks=trucks)

@app.route("/dashboard", methods=("GET", "POST"), strict_slashes=False)
@login_required
def dashboard():
    return render_template("dashboard.html",title="Mtruck | Dashboard")


@app.route("/trucks", methods=("GET", "POST"), strict_slashes=False)
@login_required
def trucks():
    trucks = Trucks.query.order_by(Trucks.id.desc()).all()
    return render_template("trucks.html",
    title="Mtruck | Trucks",
    trucks=trucks
    )

@app.route("/my_trucks", methods=("GET", "POST"), strict_slashes=False)
@login_required
def my_trucks():
    trucks = Trucks.query.filter_by(user_id=current_user.id).all()
    return render_template("trucks.html",
    title="Mtruck | Trucks",
    trucks=trucks
    )
@app.route("/<int:truck_id>/update",
    methods=("GET", "POST"),
    strict_slashes=False,
)
@login_required
def update_truck(truck_id):
    truck = Trucks.query.filter_by(id=truck_id).first()
    if truck.user_id != current_user.id:
        abort(403)

    form = AddTruck()
    if request.method=='POST':
    
        picture_file = upload_img(form.truck_img.data)

        truck.truck_img = picture_file
        truck.size = form.size.data
        truck.regno = form.regno.data

        db.session.commit()

        flash("Record succesfully Updated", "success")
        return redirect(url_for("my_trucks"))

    elif request.method == "GET":
        form.truck_img.data = truck.truck_img
        form.size.data = truck.size
        form.regno.data = truck.regno

    return render_template("add.html",
        title="Mtruck | Update Truck",
        form=form
        )

@app.route("/<int:truck_id>/delete",
    methods=("GET", "POST"),
    strict_slashes=False,
)
@login_required
def delete_truck(truck_id):
    truck = Trucks.query.filter_by(id=truck_id).first()
    if truck.user_id != current_user.id:
        abort(403)

    flash("Truck has been deleted succesfully ", "success")
    db.session.delete(truck)
    db.session.commit()
    return redirect(url_for("my_trucks"))


@app.route("/add_truck", methods=("GET", "POST"), strict_slashes=False)
@login_required
def add():
    form= AddTruck()
    if form.truck_img.data:
        picture_file = upload_img(form.truck_img.data)
        regno = form.regno.data
        truck_img = picture_file
        size = form.size.data

        truck = Trucks(
                regno=regno,
            truck_img=truck_img,
            size=size,
            user_id=current_user.id,
        )
        db.session.add(truck)
        db.session.commit()
        flash(f"Truck successfully added", "success")
        return redirect(url_for("my_trucks"))

    return render_template("add.html",
        title="Mtruck | Add Truck",
        form=form
        )

if __name__ == "__main__":
    app.run(debug=True)
