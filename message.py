from twilio.rest import Client
import random,string

def regText(number):
	account_sid = "AC309b4529097a4a869e2da0f1d426eec4"
	auth_token  = "b5c368bc47462020e67b74ceeb3eb7e6"
	client = Client(account_sid, auth_token)
	otp=''.join(random.choice(string.digits) for x in xrange(4))
	message = client.messages.create(to="+91"+number, from_="+17153164046", body="The OTP for registration is - " + otp + ". Happy Wellness!!!. Visit Here- https://goo.gl/5RebMC" )
	print(message.sid)
	return otp
