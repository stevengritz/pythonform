from google.appengine.ext import ndb
from google.appengine.api import users
import webapp2
import webapp2_extras.security
import json
import urllib
import urllib2


CLIENT_ID = "22681371415-mfjqri0d1tsdog1q8q9k8honco8gbj4v.apps.googleusercontent.com"
CLIENT_SECRET = "3DQNUTNHrP48MP_EW2Bj1O1p"
#CLIENT_ID = "22681371415-985cnvfq394itn9gg39h5gfu5n9te1ln.apps.googleusercontent.com"
#CLIENT_SECRET = "Lxnsh7lzqJNZBQ_AFFi8AD7O"
REDIRECT_URI = "https://formtesting-166817.appspot.com/redirect"
REDIRECT_URI_SECONDARY = "https://formtesting-166817.appspot.com/displayname"
#REDIRECT_URI = "http://localhost:8080/redirect"
#REDIRECT_URI_SECONDARY = "http://localhost:8080/displayname"
API_URL = "https://www.googleapis.com/plus/v1/people/me?"

state = str()

def homepage():
	text = '<a href="%s">Authenticate with Google+</a>'
	return text % make_authorization_url()

def make_authorization_url():
	
	global state
	state = webapp2_extras.security.generate_random_string(12)
	
	params = {"client_id": CLIENT_ID,
			  "response_type": "code",
			  "state": state,
			  "redirect_uri": REDIRECT_URI,
			  "duration": "temporary",
			  "scope": "email"}
	url = "https://accounts.google.com/o/oauth2/auth?" + urllib.urlencode(params)
	return url  

class MainPage(webapp2.RequestHandler):
	def get(self):

		self.response.write(homepage())

class ResponsePage(webapp2.RequestHandler):
    def post(self):
        res = json.loads(self.request.body)

class PolicyPage(webapp2.RequestHandler):
	def get(self):
		self.response.write("Comming soon")

class RedirectPage(webapp2.RequestHandler):
	def get(self):
		
		code = self.request.get('code')
		req_state = self.request.get('state')
		if state != req_state:
			webapp2.abort(403)
		#self.response.write(code)

		token_params = {
		"grant_type" : "authorization_code",
		"code" : code,
		"redirect_uri" : REDIRECT_URI,
		"client_id" : CLIENT_ID,
		"client_secret" : CLIENT_SECRET
		}

		token_response = urllib.urlopen("https://accounts.google.com/o/oauth2/token", urllib.urlencode(token_params))
		#get the token
		token_json = json.load(token_response)
		#self.response.write(json.dumps(token_json))
		token_string = token_json['access_token']

		token_get_header = {'Authorization' : "bearer " + token_string,
							'cache-control': "no-cache"}

		#google_response = urllib.urlopen("https://www.googleapis.com/plus/v1/people/me?%s" % urllib.urlencode(token_get_params))
		google_request = urllib2.Request(url = "https://www.googleapis.com/plus/v1/people/me", headers = token_get_header)
		google_response = urllib2.urlopen(google_request)
		#google_response = urllib.urlopen(API_URL % token_get_params)
		google_response_json = json.load(google_response)
		#self.response.write("https://www.googleapis.com/plus/v1/people/me?%s" % urllib.urlencode(token_get_params) + '\n')

		self.response.write(json.dumps(google_response_json))

		#self.response.write(google_response_json['name']['givenName'] + '\n')
		#self.response.write(google_response_json['name']['familyName'] + '\n')


# [START app]
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
	('/', MainPage),
	('/policy', PolicyPage),
	('/redirect', RedirectPage),

], debug=True)
# [END app]
