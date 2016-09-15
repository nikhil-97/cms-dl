###CMS downloader###
##The script logs in to CMS, and checks the 'Activity' area for new files.
##If there are any files, it will download them to user specified path.Most forum posts are written to a txt file in the same path.

import mechanize
import cookielib
from bs4 import BeautifulSoup
import os
from sys import exit
from site_test import site_check

cms_general='http://cms.bits-hyderabad.ac.in/moodle/login/index.php'
cms_intranet='http://172.16.100.125/'

if(site_check(cms_general)):
    print 'Connected to CMS'
    workingsite=cms_general
elif(site_check(cms_intranet)):
    print 'Connected to CMS via intranet'
    workingsite=cms_intranet      
else:
    print "Unable to connect to CMS.Try again later."
    print "Exiting script for now."
    exit()

br = mechanize.Browser()
br.set_handle_robots(False)
cj = cookielib.CookieJar()
br.set_cookiejar(cj)

##Intranet site leads to an intial landing page,having a 'Proceed' button.

if(workingsite==cms_intranet): 
    site=br.open(workingsite).read()
    proceed = br.click_link(text='Proceed')
    br.open(proceed)
    site2=br.click_link(text='Log in')
    br.open(site2)
    workingsite=br.geturl()

print "Opening %s "%(workingsite)
br.open(workingsite)

##Fill login form.Login details stored in CMS_userdata.dat
if(os.path.isfile('CMS_userdata.dat') and os.stat('CMS_userdata.dat').st_size!=0):
    datafile=open('CMS_userdata.dat','r')
    userdata=datafile.read()
    user,pwd=map(str,userdata.split(','))
    datafile.close()
else:
    cms_username=raw_input("Enter your CMS Username :     ")
    cms_password=raw_input("Enter your CMS Password :     ")
    file_write=raw_input("Do you want me to remember these details ?(Y/N)   ")
    
    if(file_write.lower()=='y'):
        with open('CMS_userdata.dat', 'wb') as datafile:
            datafile.write(str(cms_username)+','+str(cms_password))
    user,pwd=cms_username,cms_password
    ##Include option to overwrite,login as different user.
    ##May have to change data storage type to recognise different users.

br.select_form(nr=0)
print "Logging in as %s . . . . . \n"%str(user)
br.form['username'] = user
br.form['password'] = pwd
response=br.submit()
site=response.read()
##

UserLandingPageSoup = BeautifulSoup(site, 'html.parser')
usename=UserLandingPageSoup.body.find('div', attrs={'id':'page-content'})
print "Hello %s !"%(' '.join((usename.h3.string).split(' ')[:-1]))

courselist= UserLandingPageSoup.body.find('div', attrs={'class':'course_list'})
##courselist gets all the courses the user has enrolled in.
course_boxes=courselist.find_all('div', attrs={'class':'box coursebox'})
##course_links gets the 'box coursebox' area,where links and name are shown.

##Todo : Store the list of all enrolled courses along with userdata.
##Check if user has not enrolled in any new course.If not, then jump directly to checking,instead of getting each box everytime.

for coursebox in course_boxes:
    course_links=coursebox.find_all('a')
    ##Link to the course page is found.

    for course in course_links:
        course_name=course.get('title')
        course_site=course.get('href')
        print "Checking %s ......"%(course_name)
        ##Check the 'recent activity' block for any new files.
        ##The website gives details for the past 48 hrs,or since the last login,whichever is earlier.
        course_site_read=br.open(course_site).read()
        course_soup = BeautifulSoup(course_site_read, 'html.parser')
        course_activity=course_soup.body.find('div',attrs={'class':'block_recent_activity  block'})
        time=course_activity.find('div',attrs={'class':'activityhead'})
        timestamp=time.string
        
        if(course_activity.p.string=='No recent activity'):
            print 'No recent %s here :) \n'%(timestamp[:1].lower()+timestamp[1:])
            ##timestamp is stored as 'Activity since '
        else:
            new_files=course_activity.find_all("p", "activity")
            for new_file in new_files:
                try:
                    file_name=new_file.a.string
                except AttributeError:
                    continue
                dwldfile=new_file.a.get('href')
                print file_name
                br.open(dwldfile)
                ##In most cases,this directs to a document file.Tested on .pdf,.docx ,the most common formats.
                document=br.geturl()
                br.open(document)

                dwl_path='C:\\Users\\Nikhilanj\\Desktop\\'
                save_filename=file_name+'.'+ref.split('.')[-1]

                try:
                    if(os.path.isfile(dwl_path+save_filename) and os.stat(dwl_path+save_filename).st_size!=0):
                        print 'File %s already exists at %s'%(save_filename,dwl_path)
                    else:
                        br.retrieve(ref,dwl_path+save_filename)
                        ##This downloads the file to dwl_path.
                        print '%s saved to '%(save_filename,dwl_path)       

                except IOError:

                    if('forum' in document):
                        try:
                            forum_post=br.open(ref).read()
                            postsoup=BeautifulSoup(forum_post,'html.parser')
                            post=postsoup.body.find('div',attrs={'role':'main'})
                            text_to_write=' '.join(post.text.split('(')[:-1])
                            ##this is to take care of
                            ##'(There are no discussion topics yet in this forum)' text.
                            ##This may give some issues in some cases.Have to find another way maybe.
                            post_read_error_flag=1
                            if(text_to_write==''):
                                print 'There was an error reading the forum post. Please check manually at '+ref+' .Sorry :( '
                                post_read_error_flag=0
                            

                            save_post_with_name=fil_name+'.txt'

                            if(os.path.isfile(dwl_path+save_post_with_name) and os.stat(dwl_path+save_filename).st_size!=0 and post_error_read_flag):
                                print 'File %s already exists at %s'%(save_post_with_name,dwl_path)
                            else:
                                if(post_read_error_flag):
                                    with open(dwl_path+save_post_with_name, 'w') as g:
                                        g.write(thing_to_write)
                                        print 'Forum post written to %s at %s'%(save_post_with_name,dwl_path)
                        except :
                            print 'There was an error reading the post'

                    if('folder' in document):
                        print 'Unable to download folder.'##Adjust for now.
                        ##Downloading folders is not supported yet.
                        ##The 'download folder' button is a submit only form(SubmitControl).
                        ##Unable to submit it for some reason.
