# CMS downloader###
# The script logs in to CMS, and checks the 'Activity' area for new files.
# If there are any files, it will download them to user specified path.
# Most forum posts are written to a txt file in the same path.


import cookielib
import os
from sys import exit

import mechanize
from bs4 import BeautifulSoup

from site_test import site_check

# import pickle

br=None


def init():
	global br
	cms_general = 'http://id.bits-hyderabad.ac.in/moodle/login/index.php'

	if (not site_check(cms_general)):
		return False
	else:
		br = mechanize.Browser()
		br.set_handle_robots(False)
		cj = cookielib.CookieJar()
		br.set_cookiejar(cj)
		br.open(cms_general)
		return True


# Fill login form.Login details stored in CMS_userdata.dat


def submit_form(details):
	br.select_form(nr=0)
	# details_file = 'CMS_userdata.dat'
	# print get_login_details(details_file)
	username=details.keys()[0]
	br.form['username'], br.form['password'] = username,details[username][0]
	response = br.submit()
	site = response.read()
	#
	if br.geturl() != 'http://id.bits-hyderabad.ac.in/moodle/my/':
		print 'There was an error with login. Check your login details again.'
		exit()
	return site


def main_job(site):
	user_landing_page_soup = BeautifulSoup(site, 'html.parser')
	usename = user_landing_page_soup.body.find('div', attrs={'id': 'page-content'})
	print "Hello %s !" % (' '.join(usename.h3.string.split(' ')[:-1]))

	courselist = user_landing_page_soup.body.find('div', attrs={'class': 'course_list'})
	# courselist gets all the courses the user has enrolled in.
	course_boxes = courselist.find_all('div', attrs={'class': 'box coursebox'})
	# course_links gets the 'box coursebox' area,where links and name are shown.

	# Todo : Store the list of all enrolled courses along with userdata.
	# Check if user has not enrolled in any new course.
	# If not, then jump directly to checking,instead of getting each box every time.

	for coursebox in course_boxes:
		course_links = coursebox.find_all('a')
		# Link to the course page is found.

		for course in course_links:
			course_name = course.get('title')
			course_site = course.get('href')
			print "Checking %s ......" %course_name
			# Check the 'recent activity' block for any new files.
			# The website gives details for the past 48 hrs,or since the last login,whichever is latest.
			course_site_read = br.open(course_site).read()
			course_soup = BeautifulSoup(course_site_read, 'html.parser')
			course_activity = course_soup.body.find('div', attrs={'class': 'block_recent_activity  block'})
			time = course_activity.find('div', attrs={'class': 'activityhead'})
			timestamp = time.string

			if course_activity.p.string == 'No recent activity':
				print 'No recent %s here :) \n' % (timestamp[:1].lower() + timestamp[1:])
			# timestamp is stored as 'Activity since '
			else:
				new_files = course_activity.find_all("p", "activity")
				for new_file in new_files:
					try:
						file_name = new_file.a.string
					except AttributeError:
						continue
					dwldfile = new_file.a.get('href')
					print file_name
					br.open(dwldfile)
					# In most cases,this directs to a document file.Tested on .pdf,.docx ,the most common formats.
					document = br.geturl()
					br.open(document)

					dwl_path = 'C:\\Users\\Nikhilanj\\Desktop\\'
					save_filename = file_name + '.' + document.split('.')[-1]

					try:
						if os.path.isfile(dwl_path + save_filename) and os.stat(dwl_path + save_filename).st_size != 0:
							print 'File %s already exists at %s' % (save_filename, dwl_path)
						else:
							br.retrieve(document, dwl_path + save_filename)
							# This downloads the file to dwl_path.
							print '%s saved to ' %save_filename

					except:
						if ('forum' in document):
							try:
								forum_post = br.open(document).read()
								postsoup = BeautifulSoup(forum_post, 'html.parser')
								post = postsoup.body.find('div', attrs={'role': 'main'})
								text_to_write = ' '.join(post.text.split('(')[:-1])
								# this is to take care of
								# '(There are no discussion topics yet in this forum)' text.
								# This may give some issues in some cases.Have to find another way maybe.
								post_read_error_flag = 1
								if (text_to_write == ''):
									print 'There was an error reading the forum post. Please check manually at '+ref+' .Sorry :( '
									post_read_error_flag = 0

								save_post_with_name = fil_name+'.txt'

								if (os.path.isfile(dwl_path+save_post_with_name) and os.stat(
											dwl_path + save_filename).st_size != 0 and post_read_error_flag):
									print 'File %s already exists at %s' % (save_post_with_name, dwl_path)
								else:
									if (post_read_error_flag):
										with open(dwl_path+save_post_with_name, 'w') as g:
											g.write(thing_to_write)
											print 'Forum post written to %s at %s' % (save_post_with_name, dwl_path)
							except:
								print 'There was an error reading the post'

						if ('folder' in document):
							print 'Unable to download folder.'
						# Adjust for now.
						# Downloading folders is not supported yet.
						# The 'download folder' button is a submit only form(SubmitControl).
						# Unable to submit it for some reason.

if __name__=='__main__':
	init()
	details_file='CMS_userdata.dat'
	# load_details(details_file)
	website=submit_form()
	main_job(website)
