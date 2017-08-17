
from mailin import Mailin

def emailfunc2(email, name):
	m = Mailin("https://api.sendinblue.com/v2.0","f3zYcrFqMjtUxn5T")


	data = { "to" : {email:name},
			"from" : ["wellness@camelotgroup.in", "Camelot Wellness"],
			"subject" : "Thanks",
			"html" : "Thank you for contacting us!!. Happy to help you...."
			}

	result = m.send_email(data)
	print(result)