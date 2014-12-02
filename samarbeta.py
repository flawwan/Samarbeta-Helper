# -*- coding: utf-8 -*-
from lib.samlib import samlib

samlib = samlib()
resp_login = samlib.login()

if "Ogiltig login" in resp_login or resp_login == "":
	exit("Wrong username/password")
else:
	print "Logged in successfully"
	samlib.menu()
