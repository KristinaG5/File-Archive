import os
import enum
from pkgutil import extend_path
from flask import Flask, render_template, request, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import date


app=Flask(__name__)
load_dotenv()
UPLOAD_FOLDER = "uploads"

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_PATH')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 * 1000
db = SQLAlchemy(app)

#Enum
class FileType(enum.Enum):
    pdf = "pdf"
    xml = "xml"
    jpeg = "jpeg"


# Tables
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(FileType), nullable=False)
    filename = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, default=date.today)


@app.route('/')
def home():
    return render_template("index.html", files=File.query.all())


def get_nonconflicting_filename(filename: str):
    name, extension = filename.split(".")
    i = 1
    while filename in os.listdir(UPLOAD_FOLDER):
        filename = f"{name}-{i}.{extension}"
        i+=1
    return filename


@app.route("/", methods=['POST'])
def upload():
    upload = request.files["file"] 
    type = upload.mimetype.split("/")[1]
    filename = get_nonconflicting_filename(upload.filename)
    
    file = File(type=type, filename=filename, description=request.form["description"])
    db.session.add(file)
    db.session.commit()

    upload.save(os.path.join(UPLOAD_FOLDER, filename))

    return redirect("/")


@app.route('/uploads/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory(directory=UPLOAD_FOLDER, path=filename, as_attachment=True)


@app.route("/delete/<path:filename>", methods=['POST'])
def delete_file(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    File.query.filter_by(filename=filename).delete()
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    with app.app_context():
        db.create_all()
    app.run(debug=True)