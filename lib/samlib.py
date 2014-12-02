# -*- coding: utf-8 -*-
from Browser import Browser
from pyquery import PyQuery
import json
import webbrowser
import os
import sys
from getpass import getpass
import time


browser = Browser()


class samlib:
	username = None
	password = None

	def __init__(self):
		pass

	def login(self):

		self.username = raw_input("Username: ").decode(sys.stdin.encoding).encode('utf8')
		self.password = getpass().decode(sys.stdin.encoding).encode('utf8')

		resp = browser.fetch("http://new.samarbeta.se/login/index.php?authldap_skipntlmsso=1", {
		"username": self.username,
		"password": self.password
		})
		return resp

	def menu(self):
		while True:
			print "Wat do: "
			print "1. Dump grades, open browser"
			print "2. Exit"
			user_input = raw_input(">")
			if user_input == "1":
				print "Dumping grades....Please wait"
				self.dump_grades()
				print "Dumping done"
				time.sleep(2)
			elif user_input == "2":
				exit("bai")
			else:
				print "Unknown input"

	def get_courses(self):
		html = browser.fetch("http://new.samarbeta.se/my")
		if html == "":
			return False
		pq = PyQuery(html)
		scripts = pq("script[type='text/javascript']")
		return (pq, json.loads('{%s}' % (pq(scripts[0]).text().split(";")[3][3:].split('{', 1)[1].rsplit('}', 1)[0],))["sesskey"])

	def dump_grades(self):
		courses = self.get_courses()
		if not courses:
			print "Could not get sesskey"
			return False
		output = []
		pq = courses[0]
		output.append("""
			<!DOCTYPE html>
			<html lang="sv">
				<head>
					<meta charset='utf-8'/>
					<meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">
					<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
					<link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css\">

					<style>
						.red {
							color: red
						}
						.green {
							color: green
						}
						.orange {
							color: orange
						}
						.grey {
							color: grey
						}
					</style>
			    <body>
			    <div class="container">
			    """)
		for item in pq(".title a"):
			course_id = pq(item).attr("href").split("=")[1]
			course_name = pq(item).text()
			output.append("<h2>### Course: " + course_name.encode("utf-8") + " ###</h2>")

			data = browser.fetch("http://new.samarbeta.se/course/recent.php", {
			'id': course_id,
			'sesskey': courses[1],
			'_qf__recent_form': 1,
			'mform_showmore_id_filters': 0,
			'mform_isexpanded_id_filters': 1,
			'user': 0,
			'modid': '',
			'group': 0,
			'sortby': 'default',
			'date[day]': 26,
			'date[month]': 11,
			'date[year]': 2000,
			'date[hour]': 10,
			'date[minute]': 45,
			'date[enabled]': 1,
			'submitbutton': 'Visa senaste aktivitet'
			})
			pqb = PyQuery(data)
			for item in pqb("#region-main h3"):
				title = pqb(item).text()
				if title.startswith('Inl'):
					link = pqb(item)("a").attr("href")
					assignment = browser.fetch(link)
					if assignment == "":
						return False
					pqc = PyQuery(assignment)
					status = pqc(".cell.c1:first").text()
					betyg_status = pqc(".submissionnotgraded,.submissiongraded").text()
					trs = pqc("tr")
					class_red = "green"
					if "Inga f" in status:
						class_red = "red"
					if "Ej betygssatt" in betyg_status and " betygss" in status:
						class_red = "orange"
					if "*" in title:
						class_red = "grey"
					output.append("<pre><h3>" + title.encode("utf-8") + "</h3>")
					output.append("<b>Status:</b> " + "<span class='" + class_red + "'>" + status.encode("utf-8") + " ( " + betyg_status.encode("utf-8") + " )" + "</span><br>")

					long_comment = pqc('[class*=full_assignfeedback_comments_]').text()
					short_comment = pqc('[class*=summary_assignfeedback_comments_]').text()

					for tr in trs:
						for td in pqc(tr):
							row = pqc(td).text()
							if "Stoppdatum/tid" in row:
								output.append(row.replace("Stoppdatum/tid", "<b>Stoppdatum/tid</b>").encode("utf-8") + "<br>")

					if long_comment == "":
						output.append("<b>Kommentar:</b> " + short_comment.encode("utf-8") + "<br>")
					elif short_comment != "":
						output.append("<b>Kommentar:</b>" + long_comment.encode("utf-8") + "<br>")

					output.append("<a href='" + link + "' target='_blank'>" + link + "</a></pre><br>")
		output.append("</div></body></html>")
		file_name = self.username + "_grades.html"
		with open(file_name, 'w') as f:
			for line in output:
				f.write(line + '\n')
		os.system("start " + file_name)
