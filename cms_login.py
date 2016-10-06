# CMS downloader###
# The script logs in to CMS, and checks the 'Activity' area for new files.
# If there are any files, it will download them to user specified path.
# Most forum posts are written to a txt file in the same path.


import cookielib
import os
from sys import setrecursionlimit
import time as tm
import csv

import mechanize
from bs4 import BeautifulSoup

from site_test import site_check

br = None
setrecursionlimit(50000)


def init():
	global br
	cms_general = 'http://id.bits-hyderabad.ac.in/moodle/login/index.php'

	if not site_check(cms_general):
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
	username=details[0][0]
	br.form['username'], br.form['password'] = username,details[0][1]
	response = br.submit()
	tm.sleep(1)
	site = response.read()
	#
	if br.geturl() != 'http://id.bits-hyderabad.ac.in/moodle/my/':
		# print 'There was an error with login. Check your login details again.'
		# exit()
		return False
	return site

user_landing_page_soup=None


def get_init_soup(url):
	# global user_landing_page_soup
	user_landing_page_soup = BeautifulSoup(url, 'html.parser')
	return user_landing_page_soup


def get_name(site_soup):
	usename = site_soup.body.find('div', attrs={'id': 'page-content'})
	return ' '.join(usename.h3.string.split(' ')[:-1])


def get_course_boxes(site_soup):
	courselist = site_soup.body.find('div', attrs={'class': 'course_list'})
	# courselist gets all the courses the user has enrolled in.
	course_boxes = courselist.find_all('div', attrs={'class': 'box coursebox'})
	# course_links gets the 'box coursebox' area,where links and name are shown.
	return course_boxes


def write_activity_to_file(activitylist):
	with open('Lastactivity.csv', 'w') as writefile:
		writer=csv.writer(writefile)
		for active in activitylist:
			writer.writerow(active)

def main_job(site):
	user_land_soup=get_init_soup(site)
	print "Hello %s !" % (get_name(user_land_soup))
	course_box=get_course_boxes(user_land_soup)


	# Todo : Store the list of all enrolled courses along with userdata.
	# Check if user has not enrolled in any new course.
	# If not, then jump directly to checking,instead of getting each box every time.

	activity_list=[]
	activity_indicator=None
	for coursebox in course_box:
		course_links = coursebox.find_all('a')
		# Link to the course page is found.
		# course_site_read='C:/Python27/CMS%20downloader/cms_login_dataset/Course_%20CS_ECE_EEE_INSTR%20F215%20DIGITAL%20DESIGN%20LS1.html'
		for course in course_links:
			course_name = course.get('title')
			course_site = course.get('href')
			#print "Checking %s ......" %course_name
			# Check the 'recent activity' block for any new files.
			# The website gives details for the past 48 hrs,or since the last login,whichever is latest.
			course_site_read = br.open(course_site).read()
			course_soup = BeautifulSoup(course_site_read, 'html.parser')
			course_activity = course_soup.body.find('div', attrs={'class': 'block_recent_activity  block'})
			time = course_activity.find('div', attrs={'class': 'activityhead'})
			timestamp = time.string


			if course_activity.p.string == 'No recent activity':
				activity_indicator="No activity"
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
					activity_indicator='Downloaded file %s'%save_filename,

					try:
						if os.path.isfile(dwl_path + save_filename) and os.stat(dwl_path + save_filename).st_size != 0:
							print 'File %s already exists at %s' % (save_filename, dwl_path)
						else:
							br.retrieve(document, dwl_path + save_filename)
							# This downloads the file to dwl_path.
							print '%s saved' %save_filename
							tm.sleep(3)

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
									print 'There was an error reading the forum post. Please check manually.' + 'Sorry :( '

									post_read_error_flag = 0

								save_post_with_name = file_name+'.txt'

								if (os.path.isfile(dwl_path+save_post_with_name) and os.stat(
											dwl_path + save_filename).st_size != 0 and post_read_error_flag):
									print 'File %s already exists at %s' % (save_post_with_name, dwl_path)
								else:
									if (post_read_error_flag):
										with open(dwl_path+save_post_with_name, 'w') as g:
											g.write(text_to_write)
											#print 'Forum post written to %s at %s' % (save_post_with_name, dwl_path)
											activity_indicator='Forum post written to %s at %s' % (save_post_with_name, dwl_path),
							except:
								return False

						if ('folder' in document):
							print 'Unable to download folder.'
							return False
						# Adjust for now.
						# Downloading folders is not supported yet.
						# The 'download folder' button is a submit only form(SubmitControl).
						# Unable to submit it for some reason.
		activity_list.append((str(timestamp).strip('\n'),str(course_name).strip('\n'),str(activity_indicator).strip('\n')))
		#print activity_list
		#print str(course_name)
		#print str(activity_indicator)
		tm.sleep(1)
	# print activity_list

	write_activity_to_file(activity_list)
	return activity_list

if __name__=='__main__':
	init()
	details_file='CMS_username.csv'
	# load_details(details_file)

	if os.path.isfile(details_file) and os.stat(details_file).st_size != 0:
		with open(details_file, 'r') as reader:
				csvreader = csv.reader(reader)
				datafile = list(csvreader)
		# print "datafile=",datafile

	website=submit_form(datafile)

	main_job(website)
