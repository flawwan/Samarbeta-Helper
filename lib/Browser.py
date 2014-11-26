import httplib
import urllib2
import socket
import urllib
import cookielib

socket.setdefaulttimeout(10)


class Browser:
	cookies = None
	opener = None
	error_code = None

	def __init__(self):
		self.cookies = cookielib.LWPCookieJar()
		handlers = [
			urllib2.HTTPHandler(),
			urllib2.HTTPSHandler(),
			urllib2.HTTPCookieProcessor(self.cookies)
		]
		self.opener = urllib2.build_opener(*handlers)

	def fetch(self, url, data=None, extra_headers=None):
		if url is None:
			return ""
		try:
			headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux armv7l; rv:17.0) Gecko/20100101 Firefox/17.0'}
			if data is not None:
				data = urllib.urlencode(data)
			if extra_headers is not None:
				for h in extra_headers:
					headers[h] = extra_headers[h]
			req = urllib2.Request(url, data, headers)
			open_url = self.opener.open(req, timeout=10)
			result = open_url.read()

			open_url.close()
			return result

		except urllib2.HTTPError, e:
			print "Error: httperror" + str(e.code) + " = " + e.read()
			self.error_code = e.code
		except urllib2.URLError, e:
			print "Error: URLERROR"
		except socket.timeout, e:
			print "Error: Timeout"
		except httplib.IncompleteRead, e:
			print "incomplete read"
		return ""

	def dump_cookies(self):
		for cookie in self.cookies:
			print cookie.name, cookie.value

	def get_cookie_by_name(self, name):
		return [cookie for cookie in self.cookies if cookie.name == name][0].value

	def load_cookie(self, bot_id):
		self.cookies.load("cookies/" + str(bot_id) + ".txt")

	def save_cookie(self, bot_id):
		self.cookies.save("cookies/" + str(bot_id) + ".txt")

	def get_last_error_code(self):
		return self.error_code
