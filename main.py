from google.appengine.ext import ndb
from google.appengine.api import users
import webapp2
import json
import cgi


MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/sign" method="post">
      <div><text name="First_Name" ></text></div>
      <div><text name="Last_Name" ></text></div>
      <div><input type="submit" value="Sign Guestbook"></div>
    </form>
  </body>
</html>
"""

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.write(MAIN_PAGE_HTML)

class Guestbook(webapp2.RequestHandler):
    def post(self):
        self.response.write('<html><body>You wrote:<pre>')
        self.response.write(cgi.escape(self.request.get('content')))
        self.response.write('</pre></body></html>')

# [START app]
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
	('/', MainPage),
	('/sign', Guestbook),
], debug=True)
# [END app]
