print("="*60)
print("THIS IS Q2B - PART B")
print("="*60)

from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, jsonify, url_for, redirect
from app import app, db

# Debug: Print which database we're connected to
print("="*60)
print(f"🚀 Running: Q2b - Part (b)")
print(f"🗄️  Connected to database: {app.config['MONGODB_SETTINGS']['db']}")
print(f"🌐 URL: http://127.0.0.1:5000")
print("="*60)

from werkzeug.security import generate_password_hash

# Register Blueprint
from app.controllers.dashboard import dashboard
from app.controllers.auth import auth
from app.controllers.bookController import booking
from app.controllers.packageController import package 

from app.models.package import Package
from app.models.book import Booking
from app.models.users import User
from app.models.forms import BookForm

# For uploading file
import csv
import io
import json
import datetime as dt
import os

# Register blueprints
app.register_blueprint(dashboard)
app.register_blueprint(auth)
app.register_blueprint(booking)
app.register_blueprint(package)

@app.template_filter('formatdate')
def format_date(value, format="%#d/%m/%Y"):
    """Format a date time to (Default): dd/mm/YYYY"""
    if value is None:
        return ""
    return value.strftime(format)

@app.template_filter('formatmoney')
def format_money(value, ndigits=2):
    """Format money with 2 decimal digits"""
    if value is None:
        return ""
    return f'{value:.{ndigits}f}'

@app.route('/base')
def show_base():
    return render_template('base.html')

@app.route("/upload", methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template("upload.html", name=current_user.name, panel="Upload")
    elif request.method == 'POST':
        type = request.form.get('type')
        if type == 'create':
            print("No create Action yet")
        elif type == 'upload':
            file = request.files.get('file')
            datatype = request.form.get('datatype')

            data = file.read().decode('utf-8')
            dict_reader = csv.DictReader(io.StringIO(data), delimiter=',', quotechar='"')
            file.close()

            if datatype == "Users":
                for item in list(dict_reader):
                    pwd = generate_password_hash(item['password'], method='sha256')
                    User.createUser(email=item['email'], password=pwd, name=item['name'])
            elif datatype == "Package":
                for item in list(dict_reader):
                    Package.createPackage(hotel_name=item['hotel_name'], duration=int(item['duration']),
                        unit_cost=float(item['unit_cost']), image_url=item['image_url'],
                        description=item['description'])
            elif datatype == "Booking":
                for item in list(dict_reader):
                    existing_user = User.getUser(email=item['customer'])
                    existing_package = Package.getPackage(hotel_name=item['hotel_name'])
                    check_in_date=dt.datetime.strptime(item['check_in_date'], "%Y-%m-%d")

                    aBooking = Booking.createBooking(check_in_date=check_in_date, customer=existing_user, package=existing_package)
                    aBooking.calculate_total_cost()
                    
        return render_template("upload.html", panel="Upload")
    
@app.route("/changeAvatar")
def changeAvatar():
    basedir = os.path.abspath(os.path.dirname(__file__))
    subfolder_path = os.path.join('assets', 'img/avatar')
    subfolder_abs_path = os.path.join(basedir, subfolder_path)
    
    files = []
    for filename in os.listdir(subfolder_abs_path):
        path = os.path.join(subfolder_abs_path, filename)
        if os.path.isfile(path):
            files.append(filename)
    return render_template("changeAvatar.html", filenames=files, panel="Change Avatar") 

@app.route("/chooseAvatar", methods=['POST'])
def chooseAvatar():
    chosenPath = request.json['path']
    print('chosen path: ', chosenPath)
  
    basedir = os.path.abspath(os.path.dirname(__file__))
    subfolder_path = os.path.join('assets', 'img/avatar')
    subfolder_abs_path = os.path.join(basedir, subfolder_path)
    
    filename = chosenPath.split('/')[-1]
    User.addAvatar(current_user, filename)
    
    return jsonify(path=chosenPath)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)  