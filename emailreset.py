
from mailin import Mailin

def emailfunc4(email, name, link):
	m = Mailin("https://api.sendinblue.com/v2.0","f3zYcrFqMjtUxn5T")

	kk="127.0.0.1:5000/Reset/"
	kk+=link

	data = { "to" : {email:name},
			"from" : ["wellness@camelotgroup.in", "Camelot Wellness"],
			"subject" : "Password Reset Link",
			"html" : "Click on the link to reset "+ kk,
			}

	result = m.send_email(data)
	print(result)