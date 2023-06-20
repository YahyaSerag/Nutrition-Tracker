from flask import render_template, Flask, request, redirect, url_for, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# NOTES ...

# create virtual env >> ptyhon -m venv virtual
# To activate venv in pycharm >> virtual\Scripts\Activate.ps1
# To activate venv in sublime >> source virtual/Scripts/activate
# create db from terminal >>> winpty python or python
#                         >>> from app import db
#                         >>> db.create_all()




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# create database Models:

log_food = db.Table('log_food',
                    db.Column('log_id', db.Integer, db.ForeignKey('log.id'), primary_key=True),
                    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True))


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    proteins = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)

    @property
    def calories(self):
        return self.proteins * 4 + self.carbs * 4 + self.fats * 9


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    foods = db.relationship('Food', secondary=log_food, lazy='dynamic')


@app.route("/")
def index():
    logs = Log.query.order_by(Log.date.desc()).all()

    log_dates = []

    for log in logs:
        proteins = 0
        carbs = 0
        fats = 0
        calories = 0

        for food in log.foods:
            proteins += food.proteins
            carbs += food.carbs
            fats += food.fats
            calories += food.calories

        log_dates.append({
            'log_date': log,
            'proteins': proteins,
            'carbs': carbs,
            'fats': fats,
            'calories': calories
        })

    return render_template('index.html', log_dates=log_dates)


@app.route('/add')
def add():
    foods = Food.query.all()
    return render_template('add.html', foods=foods)


@app.route('/create_log', methods=['POST'])
def create_log():
    date = request.form.get('date')

    log = Log(date=datetime.strptime(date, '%Y-%m-%d'))
    db.session.add(log)
    db.session.commit()

    return redirect(url_for('/view', log_id=log.id))


@app.route('/add', methods=['POST'])
def add_post():
    '''
     Adding new item to food list >>>
    <label for="food-name">Food Name</label>
	<input type="text" class="form-control" id="food-name" name="food-name" placeholder="Food Name" autofocus>
    '''
    food_name = request.form.get('food-name')
    proteins = request.form.get('protein')
    carbs = request.form.get('carbohydrates')
    fats = request.form.get('fat')

    new_food = Food(
        name=food_name,
        proteins=proteins,
        carbs=carbs,
        fats=fats
    )

    db.session.add(new_food)
    db.session.commit()

    return redirect('/add')


@app.route('/delete_food/<int:food_id>')
def delete_food(food_id):
    food = Food.query.get(food_id)
    db.session.delete(food)
    db.session.commit()

    return redirect('/add')


@app.route('/view/<int:log_id>')
def view(log_id):
    log = Log.query.get(log_id)
    foods = Food.query.all()

    totals = {
        'proteins': 0,
        'carbs': 0,
        'fats': 0,
        'calories': 0
    }

    for food in log.foods:
        totals['proteins'] += food.proteins
        totals['carbs'] += food.carbs
        totals['fats'] += food.fats
        totals['calories'] += food.calories

    return render_template('view.html', foods=foods, log=log, totals=totals)


@app.route('/add_food_to_log/<int:log_id>', methods=['POST'])
def add_food_to_log(log_id):
    log = Log.query.get_or_404(log_id)

    selected_food = request.form.get('food-select')

    food = Food.query.get(int(selected_food))
    error_message = "sorry...!"

    if food in log.foods:
        return redirect(url_for('/view', log_id=log_id, error_message=error_message))

    else:
        log.foods.append(food)
        db.session.commit()
        return redirect(url_for('/view', log_id=log_id))


@app.route('/remove_food_from_log/<int:log_id>/<int:food_id>')
def remove_food_from_log(log_id, food_id):
    log = Log.query.get(log_id)
    food = Food.query.get(food_id)

    log.foods.remove(food)
    db.session.commit()

    return redirect(url_for('/view', log_id=log_id))


@app.route('/delete_log/<int:log_id>')
def delete_log(log_id):
    log = Log.query.get(log_id)
    db.session.delete(log)
    db.session.commit()
    return redirect(url_for('/index', log_id=log_id))



if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True, port=1000)