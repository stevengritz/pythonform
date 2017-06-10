from google.appengine.ext import ndb
from google.appengine.api import users
import webapp2
import webapp2_extras.security
import json
import urllib
import urllib2
import urlparse

CLIENT_ID = "449f7329486a792"
CLIENT_SECRET = "0b9596450b366f69c2d0f017a902ecfbdac11443"
REDIRECT_URI = "https://formtesting-166817.appspot.com/redirect"
#REDIRECT_URI = "http://localhost:8080/redirect"
#REDIRECT_URI_SECONDARY = "http://localhost:8080/displayname"
API_URL = " https://api.imgur.com/3?"

global token_get_header

# [START main_page]
class MainPage(webapp2.RequestHandler):
	def get(self):
		text = '<a href="%s">Authenticate with Imgur</a>'
		url = text % make_authorization_url2()
		self.response.write(url)

class PolicyPage(webapp2.RequestHandler):
	def get(self):
		self.response.write("API wrapper for adding convenience functions for Imgur API")

class AccInfo(ndb.Model) :
	#id = ndb.StringProperty(indexed = True)
	user = ndb.StringProperty(indexed = True) # username
	latestImage = ndb.StringProperty() #image id of latest image
	reputation = ndb.FloatProperty()
	bio = ndb.StringProperty()

class ImageInfo(ndb.Model):
	id = ndb.StringProperty()
	title = ndb.StringProperty() # title of image
	views = ndb.IntegerProperty() # number of views on image
	score = ndb.IntegerProperty() # raw score of image
	ups = ndb.IntegerProperty()
	downs = ndb.IntegerProperty()

def make_authorization_url2():
	
	global state
	state = webapp2_extras.security.generate_random_string(12)
	
	params = {"client_id": CLIENT_ID,
			  "response_type": "token",
			  "state": state}
	url = "https://api.imgur.com/oauth2/authorize?" + urllib.urlencode(params)
	return url 

def make_authorization_url():
	
	global state
	state = webapp2_extras.security.generate_random_string(12)
	
	params = {"client_id": CLIENT_ID,
			  "response_type": "token",
			  "state": state}
	url = "https://api.imgur.com/oauth2/authorize"

	data = urllib.urlencode(params)

	return urllib2.Request(url = url, data = data)

def get_acc_info():

	imgur_request_acc = urllib2.Request(url = "https://api.imgur.com/3/account/me/", headers = token_get_header)
	imgur_response_acc = urllib2.urlopen(imgur_request_acc)

	return json.load(imgur_response_acc)

def get_sub_info():

	imgur_request_img = urllib2.Request(url = "https://api.imgur.com/3/account/me/submissions", headers = token_get_header)
	imgur_response_img = urllib2.urlopen(imgur_request_img)

	return json.load(imgur_response_img)

class AuthorizePage(webapp2.RequestHandler):
	def get(self):
		urllib2.urlopen(make_authorization_url())

class RedirectPage(webapp2.RequestHandler):
	def get(self):
		
		req_state = self.request.get('state')
		if state != req_state:
			webapp2.abort(403)
		#self.response.write(code)

		# token_params = {
		# "grant_type" : "authorization_code",
		# "code" : code,
		# "redirect_uri" : REDIRECT_URI,
		# "client_id" : CLIENT_ID,
		# "client_secret" : CLIENT_SECRET
		# }

		#token_response = urllib.urlopen("https://api.imgur.com/oauth2/token", urllib.urlencode(token_params))
		#get the token
		#token_json = json.load(token_response)

		access_token = urlparse.parse_qs(urlparse.urlsplit(self.request.url).fragment).get('access_token')

		token_get_header = {'Authorization' : "Bearer " + access_token,
							'cache-control': "no-cache"}

		imgur_response_acc_json = get_acc_info()

		username = imgur_response_acc_json['data']['url']
		reputation = imgur_response_acc_json['data']['reputation']
		bio = username = imgur_response_acc_json['data']['bio']

		imgur_response_img_json = get_img_info()


		latest_image = imgur_response_img_json['data'][0]['id']
		title = imgur_response_img_json['data'][0]['title']
		views = imgur_response_img_json['data'][0]['views']
		score = imgur_response_img_json['data'][0]['score']
		ups = imgur_response_img_json['data'][0]['ups']
		downs = imgur_response_img_json['data'][0]['downs']

		acc_info = AccInfo()
		img_info = ImageInfo()
		u = ndb.Key(urlsafe=username).get()
		if u is None:
			acc_info.username = username
			acc_info.latestImage = latest_image
			acc_info.reputation = reputation
			acc_info.bio = bio

			img_info.id = latestImage
			img_info.title = title
			img_info.views = views
			img_info.score = score
			img_info.ups = ups
			img_info.downs = downs

			acc_info.put()
			img_info.put()
		else:
			u.username = username
			u.latestImage = latest_image
			u.reputation = reputation
			u.bio = bio

			i = ndb.Key(urlsafe=id).get()

			i.id = latestImage
			i.title = title
			i.views = views
			i.score = score
			i.ups = ups
			i.downs = downs

		self.response.write("Completed")

class BioPage(webapp2.RequestHandler):
	def get(self):
		imgur_response_acc_json = get_acc_info()
		u = ndb.Key(urlsafe=username).get()
		u_d = u.to_dict()
		u_d['self'] = "/bio"
		self.response.write(json.dumps(u_d))

class LatestPage(webapp2.RequestHandler):
	def get(self):
		imgur_response_acc_json = get_acc_info()
		u = ndb.Key(urlsafe=username).get()
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
	('/bio', BioPage),
	('/latest', LatestPage)


], debug=True)