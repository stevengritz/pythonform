from google.appengine.ext import ndb
from google.appengine.api import users
import webapp2
import json
import urllib
import requests
import requests.auth


MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/responsepage" method="post">
  		First name:<br>
  		<input type="text" name="firstname"><br>
  		Last name:<br>
  		<input type="text" name="lastname">
      <div><input type="submit" value="Login"></div>
    </form>
  </body>
</html>
"""

CLIENT_ID = "22681371415-e54rraaueok44fbuk2ce46efcsah18tt.apps.googleusercontent.com"
CLIENT_SECRET = "gDbCrJNvNYpYna-t4qTJhcu5"
REDIRECT_URI = "https://formtesting-166817.appspot.com/redirect"
API_URL = "https://www.googleapis.com/plus/v1/people/me"

GOOGLE_AUTH = """\
<html>
  <body>
    <a href="https://www.googleapis.com/auth/userinfo.email">link Click here to authorize this app</a>
  </body>
</html>
"""
def homepage():
	text = '<a href="%s">Authenticate with Google+</a>'
	return text % make_authorization_url()

def make_authorization_url():
	from uuid import uuid4
	state = str(uuid4())
	save_created_state(state)
	params = {"client_id": CLIENT_ID,
			  "response_type": "code",
			  "state": state,
			  "redirect_uri": REDIRECT_URI,
			  "duration": "temporary",
			  "scope": "email"}
	import urllib
	url = "https://accounts.google.com/o/oauth2/auth?" + urllib.urlencode(params)
	return url  

class MainPage(webapp2.RequestHandler):
	def get(self):

		self.response.write(make_authorization_url)

class ResponsePage(webapp2.RequestHandler):
    def post(self):
        res = json.loads(self.request.body)

class PolicyPage(webapp2.RequestHandler):
	def get(self):
		self.response.write("Comming soon")

class RedirectPage(webapp2.RequestHandler):
	def get(self):
		
		code = self.request.get('code')

		token_params = {
		"grant_type" : "authorization_code",
		"code" : code,
		"redirect_uri" : REDIRECT_URI,
		"client_id" : CLIENT_ID,
		"client_secret" : CLIENT_SECRET
		}

		token_response = urllib.urlopen("https://accounts.google.com/o/oauth2/token", urllib.urlencode(token_params))
		#get the token
		token_json = token_response.json()
		token_string = token_json['access_token']

		token_get_params = {"Authorization" : "bearer" + token_string}
		google_response = urllib.urlopen(API_URL % token_get_params)
		google_response_json = google_response.json()
		self.response.write(google_response_json['name']['givenName'] + '\n')
		self.response.write(google_response_json['name']['familyName'] + '\n')

# [START app]
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
	('/', MainPage),
	('/responsepage', ResponsePage),
	('/policy', PolicyPage),
	('/redirect', RedirectPage)

], debug=True)
# [END app]
