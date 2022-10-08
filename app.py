from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import enum
import os


app=Flask(__name__)
load_dotenv()

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_PATH')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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
    filename = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)

# Setup
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)