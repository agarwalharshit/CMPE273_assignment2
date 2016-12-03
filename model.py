from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask.ext.script import Manager
#from flask.ext.migrate import Migrate, MigrateCommand

app=Flask(__name__)
DATABASE = 'test'
PASSWORD = 'harshit'
USER = 'Harshit'
HOSTNAME = 'localhost'


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s'%(USER, PASSWORD, HOSTNAME, DATABASE)
db=SQLAlchemy(app)
#migrate = Migrate(app, db)
#manager = Manager(app)
#manager.add_command('db', MigrateCommand)

class Orders(db.Model):
    __tablename__='Orders'
    id=db.Column('ID',db.Integer, primary_key=True)
    customerName=db.Column('CUSTOMER_NAME',db.String(50))
    customerEmail=db.Column('CUSTOMER_EMAIL',db.String(50))
    category=db.Column('CATEGORY',db.String(50))
    description = db.Column('DESCRIPTION', db.String(200))
    link = db.Column('LINK', db.String(300))
   # estimatedCost = db.Column('ESTIMATED_COST', db.Integer)
    estimatedCost = db.Column('ESTIMATED_COST', db.String(300))
    submitDate = db.Column('SUBMIT_DATE', db.String(100))
    status = db.Column('STATUS', db.String(20))
    decisionDate = db.Column('DECISION_DATE',db.String(20))


    def __init__(self, customerName, customerEmail, category, description, link, estimatedCost, submitDate, status, decisionDate):
        self.customerName=customerName
        self.customerEmail=customerEmail
        self.category=category
        self.description=description
        self.link=link
        self.estimatedCost=estimatedCost
        self.submitDate=submitDate
        self.status=status
        self.decisionDate=decisionDate

class CreateDB():
    def __init__(self, hostname=None):
        import sqlalchemy
        engine = sqlalchemy.create_engine('mysql://%s:%s@%s' % (USER, PASSWORD, HOSTNAME))  # connect to server
        engine.execute("CREATE DATABASE IF NOT EXISTS %s " % (DATABASE))  # create db
        db.create_all()







#mpobj=employees(1,'harshit','harshit')

#db.session.add(empobj)
#db.session.commit()

#ex=employees.query.all()
#a=employees.query.filter_by(id=1).first()
#a.name='bb'
#for ex1 in ex:
#   ex1.name='aa'
#db.create_all()
#db.session.commit()

#if __name__ == '__main__':
#	manager.run()