from flask import Flask, render_template, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow



#Init app
app = Flask(__name__)

#Init database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFCATIONS'] = False
db = SQLAlchemy(app)

#Init Marshmellow
ma = Marshmallow(app)




#NOTES: Create classes for SQL structure_____________
class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(20),unique=True, nullable=False)

    def __init__(self, note):
        self.note = note

class NoteSchema (ma.Schema):
    class Meta:
        fields = ('id','note')
note_schema = NoteSchema()
notes_schema = NoteSchema(many = True)



#TODO: Create classes for SQL structure_______________
class ToDo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key = True)
    todo = db.Column(db.String(20),unique = False, nullable = False)
    status = db.Column(db.String(20),unique = False, nullable = False)
    note_id = db.Column(db.Integer,unique = False, nullable = False)#
#Opportunity for improvement: If you wanted to delete the ToDos when the parent Note
#is deleted make the note_id a foreign_key.
#Currently the front end developer would choose if the ToDos should be deleted when sending a DELETE request
#By sending multiple DELETE requests for both the Note and corresponding ToDos

    def __init__(self, todo, status, note_id):
        self.todo = todo
        self.status = status
        self.note_id = note_id

class ToDoSchema (ma.Schema):
    class Meta:
        fields = ('id','todo','status','note_id')
todo_schema = ToDoSchema()
todos_schema = ToDoSchema(many = True)



#ROUTES: Front End_________________________________
@app.route('/', methods = ["GET", "POST"])
def home():
    return render_template("home.html")

@app.route('/seeallnotes', methods = ["GET", "POST"])
def seeallnotes():
    rows = Note.query.all()
    return render_template("seeallnotes.html", rows = rows)

@app.route('/seealltodos', methods = ["GET", "POST"])
def seealltodos():
    rows = ToDo.query.all()
    return render_template("seealltodos.html", rows = rows)



#ROUTES: API: NOTES_________________________________
@app.route('/notes',methods = ["GET", "POST"])
def get_notes():
    if request.method == "GET":
        try:
            notequery = Note.query.all()
            result = notes_schema.dump(notequery)
            return jsonify(result)
        except:
            return "Nothing Found", 404

    if request.method == "POST":
        note = request.json['note']
        new_note = Note(note)
        db.session.add(new_note)
        db.session.commit()
        return note_schema.jsonify(new_note),201

@app.route('/notes/<id>',methods = ["GET", "PUT", "DELETE"])
def get_note(id):
    if request.method == "GET":
        try:
            notequery = Note.query.get(id)
            return note_schema.jsonify(notequery), 200
        except:
            return "Nothing Found", 404

    if request.method == "DELETE":
        try:
            notequery = Note.query.get(id)
            db.session.delete(notequery)
            db.session.commit()
            return "Deleted", 202
        except:
            return "Was not found", 404

    if request.method == "PUT":
        try:
            get_note = Note.query.get(id)
            note = request.json['note']
            get_note.note = note
            db.session.commit()
            return note_schema.jsonify(get_note), 202
        except:
            return "Unavailable OR Not Found", 404


#ROUTES: API: TO DOS_______________________________
@app.route('/todos',methods = ["GET", "POST"])
def get_todos():
    if request.method == "GET":
        try:
            todosquery = ToDo.query.all()
            result = todos_schema.dump(todosquery)
            return jsonify(result)
        except:
            return "Nothing Found", 404

    if request.method == "POST":
        try:
            todo = request.json['todo']
            status = request.json['status']
            note_id = request.json['note_id']
            new_todo = ToDo(todo, status, note_id)
            db.session.add(new_todo)
            db.session.commit()
            return todo_schema.jsonify(new_todo), 201
        except:
            return "Unavailable OR Not Found", 404

@app.route('/todos/<id>',methods = ["GET", "PUT", "DELETE"])
def get_todo(id):
    if request.method == "GET":
        try:
            todoquery = ToDo.query.get(id)
            return todo_schema.jsonify(todoquery), 200
        except:
            return "Nothing Found", 404
    if request.method == "DELETE":
        try:
            todoquery = ToDo.query.get(id)
            db.session.delete(todoquery)
            db.session.commit()
            return "Deleted", 202
        except:
            return "Was Not Found", 404

    if request.method == "PUT":
        try:
            get_todo = ToDo.query.get(id)
            todo = request.json['todo']
            status = request.json['status']
            note_id = request.json['note_id']
            get_todo.todo = todo
            get_todo.status = status
            db.session.commit()
            return todo_schema.jsonify(get_todo), 202
        except:
            return "Unavailable OR Not Found", 404

if __name__ == '__main__':
    app.run(debug=True)
