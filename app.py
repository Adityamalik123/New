from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database import Base, User, Company, Services, Contact, Forgot, ServicesJoined
from flask import session as login_session
import random, string
from werkzeug.security import generate_password_hash, check_password_hash
import os, sys, time
from message import regText
from emailcontact import emailfunc2
from emailinform import emailfunc3
from emailreg import emailfunc1
from emailreset import emailfunc4
from time import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20

engine=create_engine('mysql+pymysql://sql12190078:6QLIPbV5vS@sql12.freemysqlhosting.net:3306/sql12190078')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.errorhandler(404)
def pagenotfound(error):
	return render_template('error404.html')

@app.errorhandler(405)
def pagenotfound(error):
	return render_template('error405.html')


@app.errorhandler(500)
def pagenotfound(error):
	return render_template('error500.html')

@app.teardown_request
def session_clear(exception=None):
    session.close()



def get_current_user():
	user_result = None
	if 'id' in login_session:
		id = login_session['id']
		user_result=session.query(User).filter_by(id=id).first()
	return user_result


@app.route('/')
def index():
	user=get_current_user()
	if user and user.admin:
		return redirect(url_for('admin'))
	#print request.environ['REMOTE_ADDR']
	return render_template('index.html', user=user)


@app.route('/register', methods=['POST', 'GET'])
def register():
	user = get_current_user()
	if request.method == 'POST':
		existing_user=session.query(User).filter_by(email=request.form['email']).first()
		if existing_user:
			comp=session.query(Company).all()
			error='E-mail / Mobile No. already registered with some another account'
			return render_template('register.html', comp=comp, error=error)
		existing_user1=session.query(User).filter_by(mobile=request.form['contact']).first()
		if existing_user1:
			comp=session.query(Company).all()
			error='E-mail / Mobile No. already registered with some another account'
			return render_template('register.html', comp=comp, error=error)
		hashed_password=generate_password_hash(request.form['password'], method='sha256')
		newUser=User(name=request.form['name'], password=hashed_password, email
			=request.form['email'], mobile=request.form['contact'], admin=0, company_id=request.form['company'], mverifies=0)
		session.add(newUser)
		session.commit()

		id=session.query(User.id).filter_by(email=request.form['email']).first()
		login_session['id']=id
		return redirect(url_for('otp'))

	if user:
		return redirect(url_for('index'))

	comp=session.query(Company).all()
	return render_template('register.html', comp=comp)




@app.route('/getotp', methods=['POST', 'GET'])
def getotp():
	user_result=get_current_user()
	if not user_result:
		return redirect(url_for('index'))
	if request.method=='POST':
		otp=regText(user_result.mobile)
		hashed_OTP=generate_password_hash(otp, method='sha256')
		user_result.otp=hashed_OTP
		session.commit()
	return 'Sent'
	
@app.route('/otp', methods=['POST', 'GET'])
def otp():
	user=get_current_user()
	if user and user.mverifies:
		abort(404)
	if not user:
		return redirect(url_for('index'))
	if user: 	
		user_result=session.query(User).filter_by(id=login_session['id']).first()
		if not user_result.otp:
			otp=''.join(random.choice(string.digits) for x in xrange(4))
			hashed_OTP=generate_password_hash(otp, method='sha256')
			user_result.otp=hashed_OTP
			session.commit()
		if request.method=='POST':
			written=request.form['otp']
			if check_password_hash(user_result.otp, written):
				user_result.mverifies=1
				session.commit()
				return redirect(url_for('index'))
			else:
				return render_template('otp.html', error="Wrong OTP", user=user_result)
		return render_template('otp.html', user=user_result)

@app.route('/Profile')
def profile():
	user=get_current_user()
	if not user:
		return redirect(url_for('login'))
	comp=session.query(Company).filter_by(id=user.company_id).first()
	return render_template('Profile.html', user=user, comp=comp)


@app.route('/login', methods=['GET', 'POST'])
def login():
	user=get_current_user()
	error=None
	if user and request.method=='GET':
		return redirect(url_for('index'))
	if request.method=='POST':
		email=request.form['email']
		password=request.form['password']
		user_result=session.query(User).filter_by(email=email).first()
		if user_result:
			if check_password_hash(user_result.password, password):
				login_session['id']=user_result.id
				if user_result.admin:
					return redirect(url_for('admin'), code=307)
				return redirect(url_for('index'))
			else:
				error="Incorrect Email/Password combination"
		else:
			error="Incorrect Email/Password combination"
	return render_template('login.html', error=error)



@app.route('/ForgotPassword', methods=['GET', 'POST'])
def forgotPassword():
	error=None
	error1=None
	user=get_current_user()
	if user:
		return redirect(url_for('index'))
	if request.method=='POST':
		email=request.form['email']
		user_find=session.query(User).filter_by(email=email).first()
		if user_find:
			string1=''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(30))
			user_findmain=Forgot(user_id=user_find.id, ustring=string1, extime=time()+600)
			session.add(user_findmain)
			session.commit()
			emailfunc4(email, user_find.name, string1)
			error1="Password reset link sent successfully"
		else:
			error='*Not registered with us'

	return render_template('ForgotPassword.html', error=error, error1=error1)






@app.route('/ChangeProfile', methods=['POST', 'GET'])
def changeProfile():
	user=get_current_user()
	if request.method=='GET':
		return redirect(url_for('profile'))
	if not user:
		return redirect(url_for('index'))
	comp=session.query(Company).filter_by(id=user.company_id).first()
	error=None
	email=request.form['email']
	mobile=request.form['mobile']
	name=request.form['name']
	if user.email!=email:
		ekk=session.query(User).filter_by(email=email).first()
		if ekk:
			error="Email id already registered"
			return render_template('Profile.html', error=error, user=user, comp=comp)
	if user.mobile!=mobile:
		mkk=session.query(User).filter_by(mobile=mobile).first()
		if mkk:
			error="Mobile number already registered"
			return render_template('Profile.html', error=error, user=user, comp=comp)
		else:
			user.mverifies=0
	user.email=email
	user.mobile=mobile
	if user.name!=name:
		user.name=name
	session.commit()
	error1="Changes saved Successfully"
	return render_template('Profile.html', error=error1, user=user, comp=comp)

@app.route('/Reset/<string:ustring>', methods=['GET', 'POST'])
def reset(ustring):
	error=None
	find=session.query(Forgot).filter_by(ustring=ustring).first()
	if request.method=='POST':
		if not find:
			error='Either No such link exists or link is expired'
			return render_template('ResetPassword.html', error=error)
		else:
			a1=time()
			if find.extime<a1:
				session.delete(find)
				session.commit()
				error='Either No such link exists or link is expired'
				return render_template('ResetPassword.html', error=error)
			else:
				find_it=session.query(User).filter_by(id=find.user_id).first()
				session.delete(find)
				session.commit()
				password=generate_password_hash(request.form['Password'], method='sha256')
				find_it.password=password
				session.commit()
				error='Password Reset Successfull'
				return render_template('ResetPassword.html', error=error)

	if not find:
		error='Either No such link exists or link is expired'
	else:
		a=time()
		if find.extime<a:
			session.delete(find)
			session.commit()
			error='Either No such link exists or link is expired'
		else:
			return render_template('ResetPassword.html', error=error, find=find)

	return render_template('ResetPassword.html', error=error)






@app.route('/ResetSuccess', methods=['POST'])
def resetSuccess():
	return 'Password changed successfully'




@app.route('/ChangePassword', methods=['POST', 'GET'])
def changepass():
	if request.method=='GET':
		return redirect(url_for('profile'))
	user=get_current_user()
	if not user:
		return redirect(url_for('index'))
	comp=session.query(Company).filter_by(id=user.company_id).first()
	password=request.form['oldpass']
	if check_password_hash(user.password, password):
		user.password=generate_password_hash(request.form['newpass'], method='sha256')
		session.commit()
		error='Password Changed Successfully'
		return render_template('Profile.html', error=error, user=user, comp=comp)

	else:
		error='Incorrect Password Entered'
		return render_template('Profile.html', error=error, user=user, comp=comp)




@app.route('/Contactus', methods=['POST', 'GET'])
def contactus():
	user=get_current_user()
	if request.method=='POST':
		if user:
			companyn=session.query(Company.name).filter_by(id=user.company_id).first()
			requests=Contact(name=user.name, email=user.email, mobile=user.mobile, message=request.form['message'], company=companyn.name, completed=0)
			name=user.name
			email=user.email
			print name, email
		else:
			requests=Contact(name=request.form['name'], email=request.form['email'], mobile=request.form['mobile'], message=request.form['message'], company=request.form['company'], completed=0)
			name=request.form['name']
			email=request.form['email']
	
		session.add(requests)
		session.commit()
		emailfunc2(email,name)
		emailfunc3()
		return 'successfull contact'
	if request.method=='GET':
		return redirect('/#contact')


@app.route('/Subscribe', methods=['POST'])
def subscribe():
	#em=session.query(User).filter_by(email=request.form['email']).first()
	#if em:
	#	return 'You are already Subscribed'
	#else:
	#	kk=Subscribe(email=request.form['email'])
	#	session.add(kk)
	#	session.commit()
	#return 'Subscribed
	return render_template('UnderDevelopment.html')



@app.route('/Slotbooking')
def book():
	user=get_current_user()
	if not user:
		abort(404)
	return render_template('UnderDevelopment.html')

@app.route('/Feedback')
def feedback():
	return render_template('UnderDevelopment.html')



@app.route('/logout')
def logout():
	user=get_current_user()
	if user:
		login_session.pop('id', None)
	return redirect(url_for('index'))

#@app.route('/testimonials')
#return render_template('testimonials.html')





#All related to Admin------------------------------
@app.route('/Admin', methods=['POST', 'GET'])
def admin():
	return render_template('adminindex.html')
	





#All related to services@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@app.route('/ServicesPanel')
def servicesControl():
	return render_template('ServicesControl.html')

@app.route('/ServicesPanel/New', methods=['POST', 'GET'])
def servicesNew():
	if request.method=='POST':
		new_serv=Services(name=request.form['name'])
		session.add(new_serv)
		session.commit()

	serv=session.query(Services).all()
	return render_template('ServicesControlNew.html', serv=serv)

@app.route('/ServicesPanel/Delete')
def servicesDel():
	serv=session.query(Services).all()
	return render_template('ServicesControlDel.html', serv=serv)


@app.route('/ServicesPanel/Delete/<int:Del_id>')
def servicesDelwithid(Del_id):
	servDel=session.query(Services).filter_by(id=Del_id).one()
	session.delete(servDel)
	session.commit()
	return redirect(url_for('servicesDel'))


@app.route('/ServicesPanel/Edit')
def servicesEdit():
	serv=session.query(Services).all()
	return render_template('ServicesControlEdit.html', serv=serv)


@app.route('/ServicesPanel/Edit/<int:Edit_id>', methods=['GET', 'POST'])
def servicesEditwithid(Edit_id):
	servEdit=session.query(Services).filter_by(id=Edit_id).one()
	if request.method=='POST':
		servEdit.name=request.form['name']
		session.commit()
		return redirect(url_for('servicesEdit'))

	return render_template('ServicesEditIndiv.html', servEdit=servEdit)
#Services part Ends@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@







#All related to Company Changes~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/CompanyControl')
def companyControl():
	return render_template('CompanyControl.html')


@app.route('/CompanyControl/New', methods=['GET','POST'])
def companyNew():
	if request.method=='POST':
		new_comp=Company(name=request.form['name'])
		session.add(new_comp)
		session.commit()

	comp=session.query(Company).all()
	return render_template('CompanyControlNew.html', comp=comp)


@app.route('/CompanyControl/Delete')
def companyDel():
	comp=session.query(Company).all()
	return render_template('CompanyControlDel.html', comp=comp)


@app.route('/CompanyControl/Delete/<int:Del_id>')
def companyDelwithid(Del_id):
	i=session.query(User).filter_by(company_id=Del_id).all()
	if i:
		for gm in i:
			kk=session.query(Forgot).filter_by(user_id=gm.id).all()
			if kk:
				for ii in kk:
					session.delete(ii)
					session.commit()
			session.delete(gm)
			session.commit()

	compDel=session.query(Company).filter_by(id=Del_id).first()
	if compDel:
		session.delete(compDel)
		session.commit()
	
	
	return redirect(url_for('companyDel'))


@app.route('/CompanyControl/Edit')
def companyEdit():
	comp=session.query(Company).all()
	return render_template('CompanyControlEdit.html', comp=comp)


@app.route('/CompanyControl/Edit/<int:Edit_id>', methods=['GET', 'POST'])
def companyEditwithid(Edit_id):
	compEdit=session.query(Company).filter_by(id=Edit_id).one()
	if request.method=='POST':
		compEdit.name=request.form['name']
		session.commit()
		return redirect(url_for('companyEdit'))

	return render_template('CompanyEditIndiv.html', compEdit=compEdit)


@app.route('/CompanyControl/Service', methods=['GET', 'POST'])
def addAll():
	comp=session.query(Company).all()
	serv=session.query(Services).all()
	if request.method=='POST':
		new=ServicesJoined(services_id=request.form['service'], company_id=request.form['company'])
		session.add(new)
		session.commit()
	return render_template('CompanyServe.html', comp=comp, serv=serv)


@app.route('/CompanyControl/Service/View/<int:kid>')
def view(kid):
	serb=session.query(ServicesJoined).filter_by(company_id=kid).all()
	serb1=session.query(Services).join(ServicesJoined).filter_by(id=ServicesJoined.services_id).all()
	for s in serb1:
		print s.name
	return render_template('CompanyServeView.html', serb1=serb1)
 
@app.route('/CompanyControl/Service/DelOnly')
def delOnly():
	return render_template('CompanyControl.html')
#Company part ends~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~







#Users Part$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

@app.route('/UsersPanel')
def usersPanel():
	return render_template('UsersPanel.html')

@app.route('/UsersPanel/View', methods=['POST', 'GET'])
def usersView():
	userf=None
	error=None
	if request.method=='POST':
		userf=session.query(User).filter(User.name.like("%"+request.form['name']+"%")).all()
		if userf is None:
			error='No user Exists'
	comp=session.query(Company).all()
	return render_template('UsersView.html', comp=comp, userf=userf, error=error)

@app.route('/UsersPanel/View/Company_List/<int:View_id>')
def usersViewComp(View_id):
	usercompm=session.query(User).filter_by(company_id=View_id).all()
	return render_template('UsersViewComp.html', usercompm=usercompm)


@app.route('/UsersPanel/View/<int:View_id>')
def usersViewIndiv(View_id):
	userIndiv=session.query(User).filter_by(id=View_id).one()
	companyn=session.query(Company.name).filter_by(id=userIndiv.company_id).one()
	return render_template('UsersViewIndiv.html', userIndiv=userIndiv, companyn=companyn)

@app.route('/UsersPanel/Promote', methods=['GET', 'POST'])
def usersPromote():
	error=None
	if request.method=='POST':
		userdet=session.query(User).filter_by(email=request.form['email']).first()
		if userdet:
			if userdet.admin==1:
				error='Already an Admin'
			else:
				userdet.admin=1
				session.commit()
				error='Promoted Successfully'
		else:
			error='Please enter a registered Email-Id'

	userad=session.query(User.name).filter(User.admin==1).all()
	return render_template('UsersPromote.html', error=error, userad=userad)

@app.route('/UsersPanel/Demote', methods=['GET', 'POST'])
def usersDemote():
	error=None
	if request.method=='POST':
		userdet=session.query(User).filter_by(email=request.form['email']).first()
		if userdet:
			if userdet.admin==0:
				error='Already a Normal User'
			else:
				userdet.admin=0
				session.commit()
				error='Demoted Successfully'
		else:
			error='Please enter a registered Email-Id'

	userad=session.query(User.name).filter(User.admin==1).all()
	return render_template('UsersDemote.html', error=error, userad=userad)


@app.route('/UsersPanel/Delete', methods=['GET', 'POST'])
def usersDelete():
	error=None
	if request.method=='POST':
		userdet=session.query(User).filter_by(email=request.form['email']).first()
		if not userdet:
			error='No user Exists'
		else:
			session.delete(userdet)
			session.commit()
			error='USer Deleted Successfully'

	return render_template('UsersDelete.html', error=error)

#User part ends$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$






#LAter PArts++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route('/TestimonialControl')
def testimonialControl():
	return render_template('UnderDevelopment.html')

@app.route('/BookingManagement')
def bookingManagement():
	return render_template('UnderDevelopment.html')

@app.route('/FeedbackPanel')
def feedbackPanel():
	return render_template('UnderDevelopment.html')
#LaterParts ends+++++++++++++++++++++++++++++++++++++++++++++++++++++






#Contact part start^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

@app.route('/ContactRequests', methods=['GET','POST'])
def contactRequests():
	error=None
	if request.method=='POST':
		error='Successfully Marked Completed'
	req=session.query(Contact).filter_by(completed=0).order_by(Contact.id.desc()).all()
	return render_template('ContactRequests.html', req=req, error=error)

@app.route('/ContactRequests/Completed')
def completed():
	req=session.query(Contact).filter_by(completed=1).order_by(Contact.id.desc()).all()
	return render_template('ContactRequestsCompleted.html', req=req)

@app.route('/ContactRequests/Details/<int:request_id>')
def contactIndiv(request_id):
	req=session.query(Contact).filter_by(id=request_id).first()
	return render_template('ContactIndiv.html', req=req)

@app.route('/Mark/<int:request_id>')
def mark(request_id):
	req=session.query(Contact).filter_by(id=request_id).first()
	req.completed=1
	session.commit()
	return redirect(url_for('contactRequests'), code=307)

#Contact part ends^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^






#Admin part ends------------------------------------------------------




if __name__ == '__main__':
	app.run(host="0.0.0.0" , port= 5000, debug=True)