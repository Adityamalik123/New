
from mailin import Mailin

def emailfunc1(email, name):
	m = Mailin("https://api.sendinblue.com/v2.0","f3zYcrFqMjtUxn5T")


	data = { "to" : {email:name},
			"from" : ["wellness@camelotgroup.in", "Camelot Wellness"],
			"subject" : "Register",
			"html" : "Hi register"
			}

	result = m.send_email(data)
	print(result)