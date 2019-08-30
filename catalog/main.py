from flask import Flask,url_for,redirect,render_template,request,flash
from flask_mail import Mail,Message
from random import randint
from projectdatabase import Register,Base, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_login import LoginManager,login_user,current_user,logout_user,login_required,UserMixin


engine=create_engine('sqlite:///iiit.db',connect_args={'check_same_thread':False},echo=True)
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()

app=Flask(__name__)

login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'


app.secret_key='super secret_key'


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='vangarayamini370@gmail.com'
app.config['MAIL_PASSWORD']='rnynp123'
app.config['MAIL_USE_TLS']=False	
app.config['MAIL_USE_SSL']=True
mail=Mail(app)
otp=randint(000000,999999)
@app.route("/email")
def email():
	return render_template("demo_email.html")
@app.route("/email_verify",methods=['POST','GET'])
def verify_email():
	email=request.form['email']
	msg=Message('One Time Password',sender='vangarayamini370@gmail.com',recipients=[email])
	msg.body=str(otp)
	mail.send(msg)
	return render_template('email_verify.html')
@app.route("/email_validate",methods=['POST','GET'])
def email_validate():
	user_otp=request.form['otp']
	if otp==int(user_otp):
		# return "Valid OTP"
		register=session.query(Register).all()
		flash("Successfully Login...")
		return redirect(url_for('showData',reg=register))
	# return "Invalid OTP"
	flash("Please check your OTP")
	return render_template("email_verify.html")


@app.route("/")
def index():
	return render_template('index.html')


@login_required
@app.route('/show',methods=['POST','GET'])
def showData():
	register=session.query(Register).all()
	return render_template('show.html',reg=register)

@app.route("/add",methods=['POST','GET'])
def addData():
	if request.method=='POST':
		newData=Register(name=request.form['name'],
			surname=request.form['surname'],
			email=request.form['email'],
			branch=request.form['branch'])
		session.add(newData)
		session.commit()
		return redirect(url_for('showData'))
	else:

		return render_template('add.html')

@app.route("/<int:register_id>/edit", methods=['POST','GET'])
def editData(register_id):
	editedData=session.query(Register).filter_by(id=register_id).one()
	if request.method=='POST':
		editedData.name=request.form['name']
		editedData.surname=request.form['surname']
		editedData.email=request.form['email']
		editedData.branch=request.form['branch']

		session.add(editedData)
		session.commit()
		flash("Successfully Edited %s" %(editedData.name))
		return redirect(url_for('showData'))
	else:
		return render_template('edit.html',register=editedData)

@app.route("/<int:register_id>/delete",methods=['POST','GET'])
def deleteData(register_id):
	delData=session.query(Register).filter_by(id=register_id).one()
	if request.method=='POST':
		session.delete(delData)
		session.commit()
		flash("Successfully deleted %s" %(deleteData.name))
		return redirect(url_for('showData',register_id=register_id))
	else:
		return render_template('delete.html',register=delData)

@app.route("/account",methods=['POST','GET'])
@login_required
def account():
	return render_template("account.html")

@app.route("/register1", methods=['POST','GET'] )
def register1():
	if request.method=='POST':
		userData=User(name=request.form['name'],
			email=request.form['email'],
			password=request.form['password'])
		session.add(userData)
		session.commit()
		return redirect(url_for('index'))
	else:
		return render_template('register.html')

@login_required
@app.route("/login",methods=['POST','GET'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('showData'))

	try:
		if request.method=='POST':
			user=session.query(User).filter_by(email=request.form['email'],password=request.form['password']).first()

			if user:
				login_user(user)
				return redirect(url_for('showData'))
			else:
				flash("Login Invalid....")
		else:
			return render_template('login.html',title="login")
	except Exception as e:
		flash("login failed...")

	else:
		return render_template('login.html',title="login")

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
	return session.query(User).get(int(user_id))

if __name__=='__main__':
	app.run(debug=True)