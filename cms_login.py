# CMS downloader###
# The script logs in to CMS, and checks the 'Activity' area for new files.
# If there are any files, it will download them to user specified path.
# Most forum posts are written to a txt file in the same path.


import cookielib
import os
from sys import setrecursionlimit
import time as tm
import csv
from datetime import datetime
import mechanize
from bs4 import BeautifulSoup
from requests import get,ConnectionError,HTTPError

br = None
setrecursionlimit(50000)

timestamp=None

def site_check(url):
    try:
        response=get(url,timeout=10)
        if(int(response.status_code)==200):
            return True
    except ((ConnectionError) or (HTTPError)):
        return False


def nowtime():
	return datetime.now().strftime('%I:%M:%S %p,%d/%m/%Y')

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
		print 'There was an error with login. Check your login details again.'
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
	with open('.Lastactivity.csv', 'w') as writefile:
		writer=csv.writer(writefile)
		for active in activitylist:
			writer.writerow(active)

def check_site_news():
	global status
	news_url='http://id.bits-hyderabad.ac.in/moodle/mod/forum/view.php?id=1'
	site_news_soup=BeautifulSoup(br.open(news_url).read(),'html.parser')
	news_box = site_news_soup.body.find('table', attrs={'class': 'forumheaderlist'})
	status="Checking site news"
	#print news_box
	latest_news=[]
	for news in news_box.findAll("tr"):
		try:
			news_name=news.find('td', attrs={'class': 'topic starter'})
			print news_name.a.string
			latest_news.append(news_name.a.string)
		except:
			continue
	return 'job done'

def course_details(course):
	course_name = course.get('title')
	course_site = course.get('href')
	return (course_name,course_site)

def course_activity_block(coursesite):
	# Check the 'recent activity' block for any new files.
	# The website gives details for the past 48 hrs,or since the last login,whichever is latest.
	course_site_read = br.open(coursesite).read()
	course_soup = BeautifulSoup(course_site_read, 'html.parser')
	activity_block = course_soup.body.find('div', attrs={'class': 'block_recent_activity  block'})
	return activity_block

def write_forum(file_name,document,path):
	#print "in write_forum(%s,%s,%s)"%(file_name,document,path)
	forum_post = br.open(document).read()
	postsoup = BeautifulSoup(forum_post, 'html.parser')
	post = postsoup.body.find('div', attrs={'role': 'main'})
	text_to_write=post.text
	#text_to_write = ' '.join(post.text.split('(')[:-1])
	# this is to take care of
	# '(There are no discussion topics yet in this forum)' text.
	# This may give some issues in some cases.Have to find another way maybe.
	if (text_to_write == ''):
		#print 'There was an error reading the forum post. Please check manually.' + 'Sorry :( '
		return False
	save_post_with_name = file_name + '.txt'

	if (os.path.isfile(path + save_post_with_name) and os.stat(
				path + save_post_with_name).st_size != 0):
		forum_exists=True
		return (True, forum_exists)
	else:
		forum_exists=False
		try:
			with open(path + save_post_with_name, 'w') as g:
				g.write(text_to_write)
			return (True,forum_exists)
		except:
			return False

def dwld_file(file_name,document,dwl_path):
	save_filename = file_name + '.' + document.split('.')[-1]
	exists=False
	if os.path.isfile(dwl_path + save_filename) and os.stat(dwl_path + save_filename).st_size != 0:
		exists=True
		return (True,exists)
	else:
		try:
			br.open(document)
			br.retrieve(document, dwl_path + save_filename)
			tm.sleep(3)
			# This downloads the file to dwl_path.
			return (True,exists)
		except:
			return False


def check_each_course(course):
	global timestamp
	coursename = course_details(course)[0]
	coursesite = course_details(course)[1]
	#coursesite='file:///C:/Python27/CMS%20downloader/cms_login_dataset/Course_%20CS_ECE_EEE_INSTR%20F215%20DIGITAL%20DESIGN%20LS1.html'
	course_activity=course_activity_block(coursesite)
	time = course_activity.find('div', attrs={'class': 'activityhead'})
	timestamp = time.string
	try:
		recentactivity=course_activity.p.string
	except AttributeError:
		recentactivity=course_activity.li.text
	print recentactivity,(recentactivity=='No recent activity')

	if recentactivity == 'No recent activity':
		new_activity_indicator = 0
		return new_activity_indicator

	else:
		new_files = course_activity.find_all("p", "activity")
		dwl_path = 'C:\\Users\\Nikhilanj\\Desktop\\'


		for new_file in new_files:
			try:
				file_name = new_file.a.string
				dwldfile1 = new_file.a.get('href')
			except AttributeError:
				continue
			if('cms.bits-hyderabad.ac.in'in dwldfile1):
				dwldfile=dwldfile1.replace('cms.bits-hyderabad.ac.in','id.bits-hyderabad.ac.in')
			else:
				dwldfile=dwldfile1
			try:
				br.open(dwldfile)
			except :
				continue

			# In most cases,this directs to a document file.Tested on .pdf,.docx ,the most common formats.
			document = br.geturl()
			try:
				dwld_result=dwld_file(file_name, document, dwl_path)
				if (dwld_result):
					new_activity_indicator = 1
					if(not dwld_result[1]):
						print "File `%s` downloaded to %s"%(file_name,dwl_path)
						dwdata=(file_name,coursename,dwl_path,nowtime())
						with open('.cms-dl_downloads.csv', 'a') as dwlist_file:
							dwlwriter = csv.writer(dwlist_file)
							dwlwriter.writerow(dwdata)
					else:
						print "File `%s` already exists at %s"%(file_name,dwl_path)
					continue
				else:
					print 'Unable to download file `%s` from _%s_' % (file_name, document)

						#return (False, timestamp)
			except :
				if ('/forum/' in document):
					# try:
					forumstatus=write_forum(file_name,document,dwl_path)
					if(forumstatus):
						if(not forumstatus[1]):
							print 'Forum `%s` written to %s'%(file_name,dwl_path)
							dwdata = (file_name, coursename, dwl_path, nowtime())
							with open('.cms-dl_downloads.csv', 'a') as dwlist_file:
								dwlwriter = csv.writer(dwlist_file)
								dwlwriter.writerow(dwdata)
					# except:
					# 	print'Error'

				elif ('folder' in document):
					print 'Unable to download folder.'
					#return
				else:
					print 'There was a problem in reading the post in %s' % coursename
				# Adjust for now.
					# Downloading folders is not supported yet.
					# The 'download folder' button is a submit only form(SubmitControl).
					# Unable to submit it for some reason.
				# except AttributeError:
				# 	print 'AttributeError'
					# 	return False


if __name__=='__main__':
	activity_list = []
	activity_indicator = None

	initstatus=init()
	if(not initstatus):
		print 'Unable to connect to CMS site. Quitting script.'
		exit()
	details_file='.CMS_username.csv'
	# load_details(details_file)

	if os.path.isfile(details_file) and os.stat(details_file).st_size != 0:
		with open(details_file, 'r') as reader:
				csvreader = csv.reader(reader)
				datafile = list(csvreader)
		# print "datafile=",datafile
	website=submit_form(datafile)
	user_land_soup = get_init_soup(website)
	print "Hello %s !" % (get_name(user_land_soup))
	# print website
	prompt=str(raw_input("What do you want me to do ? Type 'A' for checking your courses, or 'B' for checking site news.Any other key to quit now.")).lower()
	if(prompt=='a'):
		course_box = get_course_boxes(user_land_soup)
		#print check_my_courses(website)
		for coursebox in course_box:
			course_links = coursebox.find_all('a')
			# Link to the course page is found.
			for course in course_links:
				status = "Checking %s ......" % course_details(course)[0]
				print status
				checkresult=check_each_course(course)
				#timestamp=checkresult[1]
				print checkresult
				if(not checkresult and checkresult != None):
					print 'No recent %s here\n' % (timestamp[:1].lower() + timestamp[1:])
					activity_list.append((course_details(course)[0],'No activity'))
				tm.sleep(1)
		print ['%s -- %s'%(i[0],i[1]) for i in activity_list ]
	elif(prompt=='b'):
		print check_site_news()
	else:
		exit()
