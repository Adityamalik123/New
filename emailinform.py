
from mailin import Mailin

def emailfunc3():
	m = Mailin("https://api.sendinblue.com/v2.0","f3zYcrFqMjtUxn5T")


	data = { "to" : {"adityamalik360@gmail.com":"Aditya", "archish@outlook.in":"Archish"},
			"from" : ["wellness@camelotgroup.in", "Camelot Wellness"],
			"subject" : "New Request",
			"html" : "You got a contact us request... check the same by logging in"
			}

	result = m.send_email(data)
	print(result)