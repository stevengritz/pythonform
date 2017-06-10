from google.appengine.ext import ndb
from google.appengine.api import users
import webapp2
import webapp2_extras.security
import json
import urllib
import urllib2


CLIENT_ID = "22681371415-mfjqri0d1tsdog1q8q9k8honco8gbj4v.apps.googleusercontent.com"
CLIENT_SECRET = "3DQNUTNHrP48MP_EW2Bj1O1p"
REDIRECT_URI = "https://formtesting-166817.appspot.com/redirect"
#REDIRECT_URI = "http://localhost:8080/redirect"
#REDIRECT_URI_SECONDARY = "http://localhost:8080/displayname"
API_URL = " https://api.imgur.com/3?"

global access_token
global current_user

# [START main_page]
class MainPage(webapp2.RequestHandler):
	def get(self):
		text = '<a href="%s">Authenticate with Google</a>'
		url = text % make_authorization_url2()
		self.response.write(url)

class PolicyPage(webapp2.RequestHandler):
	def get(self):
		self.response.write("API wrapper for adding convenience functions for Imgur API")

class AccInfo(ndb.Model) :
	id = ndb.StringProperty(indexed = True)
	user = ndb.StringProperty() # displayname
	url = ndb.StringProperty() #image id of latest image
	email = ndb.FloatProperty()
	object_type = ndb.StringProperty()
	query = ndb.StringProperty() # query text


class ActivityInfo(ndb.Model):
	id = ndb.StringProperty()
	query = ndb.StringProperty() # query text
	title = ndb.IntegerProperty() # number of views on image
	url = ndb.IntegerProperty() # raw score of image

def make_authorization_url2():
	global toketoken_get_header
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

class AuthorizePage(webapp2.RequestHandler):
	def get(self):
		urllib2.urlopen(make_authorization_url())

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

		access_token = token_json['access_token']

		token_get_header = {'Authorization' : "Bearer " + access_token,
							'cache-control': "no-cache"}

		google_request = urllib2.Request(url = "https://www.googleapis.com/plus/v1/people/me", headers = token_get_header)
		google_response = urllib2.urlopen(google_request)

		google_response_json = json.load(google_response)


		id = google_response_json['id']
		current_user = id;
		user = google_response_json['displayName'] # displayname
		url = google_response_json['url'] #image id of latest image
		object_type = google_response_json['objectType']

		acc_info = AccInfo()
		# u = ndb.Key(urlsafe=id).get()
		# if u is None:
		acc_info.id = id
		acc_info.user = user
		acc_info.url = url
		acc_info.object_type = object_type

		acc_info.put()
			
		# else:
		# 	u.username = username
		# 	u.latestImage = latest_image
		# 	u.reputation = reputation
		# 	u.bio = bio

		self.response.write("Completed")

class AccountPage(webapp2.RequestHandler):
	def get(self):
		u = ndb.Key(urlsafe=current_user).get()
		u_d = u.to_dict()
		u_d['self'] = "/account"
		self.response.write(json.dumps(u_d))

	def post(self):
		

		acc_info = AccInfo()
		u = ndb.Key(urlsafe=username).get()
		if u is None:
			acc_info.username = username
			acc_info.latestImage = latest_image
			acc_info.reputation = reputation
			acc_info.bio = bio
			acc_info.put()

		self.response.write("Completed" + access_token)

class ActivityPage(webapp2.RequestHandler):
	def post(self, user = None):
		query_data = json.loads(self.request.body)
		query_string = query_data['query']

		params = {
			"query" : query_string,
			"key" : access_token
		}

		google_request = urllib2.Request(url = "https://www.googleapis.com/plus/v1/activities", data = urllib.urlencode(params))
		google_response = urllib2.urlopen(google_request)
		google_response_json = json.load(google_response)

		#Add top query entry to activty table with user key
		u = ndb.Key(urlsafe=user).get()
		u.query = query_string

		act_info = ActivityInfo()
		act_info.id = google_response_json['items'][0]['id']
		act_info.query = query_string
		act_info.title = google_response_json['items'][0]['title']
		act_info.url = google_response_json['items'][0]['url']

	def get(self, user = None):
		u = ndb.Key(urlsafe=user).get()
		u_d = u.to_dict()
		u_d['self'] = "/latest"
		self.response.write(json.dumps(u_d))


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
	('/', MainPage),
	('/policy', PolicyPage),
	('/authorize', AuthorizePage),
	('/redirect', RedirectPage),
	('/account', AccountPage),
	('/activity', ActivityPage)


], debug=True)