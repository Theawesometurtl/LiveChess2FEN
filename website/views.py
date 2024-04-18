from flask import Blueprint, render_template, request

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        prevFEN = request.form.get('prevFEN')

        if len(prevFEN) == 0:
            flash('too short')
    return render_template("template.html", text = "FEN test")

