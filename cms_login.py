import mechanize
from bs4 import BeautifulSoup
import cookielib
import os
import requests
from sys import exit

url1='http://cms.bits-hyderabad.ac.in/moodle/login/index.php'
url2='http://172.16.100.125/'

def is_site_working(url):
    try:
        response=requests.get(url,timeout=10)
        if(int(response.status_code)==200):
            return True
    except ((requests.ConnectionError) or (requests.HTTPError)):
        return False

if(is_site_working(url1)):
    finalsite=url1
    print "Connected to CMS.Let's start."
elif(is_site_working(url2)):
    print "Connected to CMS.Let's start."
    finalsite=url2
else:
    print "Unable to connect to CMS.Try again later."
    print "Exiting script for now."
    exit()

br = mechanize.Browser()
br.set_handle_robots(False)
cj = cookielib.CookieJar()
br.set_cookiejar(cj)

if(finalsite==url2): 
    site=br.open(finalsite).read()
    soup = BeautifulSoup(site, 'html.parser')
    req = br.click_link(text='Proceed')
    br.open(req)
    #print br.geturl()
    sitef=br.click_link(text='Log in')
    br.open(sitef)
    finalsite=br.geturl()

print "Opening %s "%(finalsite)
url=br.open(finalsite)

if(os.path.isfile('CMS_userdata.dat')):
    f=open('CMS_userdata.dat','r')
    data=f.read()
    user,pwd=map(str,data.split(' '))
    f.close()
    
else:
    cms_username=raw_input("Enter your CMS Username :     ")
    cms_password=raw_input("Enter your CMS Password :     ")
    file_write=raw_input("Do you want me to remember these details ?(Y/N)   ")
    
    if(file_write.lower()=='y'):
        with open('CMS_userdata.dat', 'w') as f:
            f.write(str(cms_username)+' '+str(cms_password))
    user,pwd=cms_username,cms_password


br.select_form(nr=0)
print "Logging in as %s . . . . . "%str(user)
br.form['username'] = user
br.form['password'] = pwd
response=br.submit()
site=response.read()
soup = BeautifulSoup(site, 'html.parser')

usename=soup.body.find('div', attrs={'id':'page-content'})
print "Hello %s !"%(' '.join((usename.h3.string).split(' ')[:-1]))

courselist= soup.body.find('div', attrs={'class':'course_list'})
under_courses=courselist.find_all('div', attrs={'class':'box coursebox'})

for i in under_courses:
    morelol=i.find_all('a')

    for j in morelol:
        course_name=j.get('title')
        course_site=j.get('href')

        url=br.open(course_site).read()
        soup1 = BeautifulSoup(url, 'html.parser')
        activity=soup1.body.find('div',attrs={'class':'block_recent_activity  block'})
        time=activity.find('div',attrs={'class':'activityhead'})
        timestamp=time.string

        if(activity.p.string=='No recent activity'):
            print 'No recent %s in %s'%(timestamp[:1].lower()+timestamp[1:],course_name)

        else:
            files=activity.find_all("p", "activity")

            for fil in files:
                fil_name=fil.a.string
                dwfile=fil.a.get('href')
                print fil_name
                #print dwfile

                dw=br.open(dwfile)
                ref=br.geturl()
                br.open(ref)

                dwl_path='C:\\Users\\Nikhilanj\\Desktop\\'
                save_filename=dwl_path+fil_name+'.'+ref.split('.')[-1]

                try:
                    if(os.path.isfile(save_filename)):
                        print 'File %s already exists'%(save_filename)
                    else:
                        br.retrieve(ref,save_filename)
                        print '%s saved'%(save_filename)       

                except IOError:

                    if('forum' in ref):
                        forum_post=br.open(ref).read()
                        postsoup=BeautifulSoup(forum_post,'html.parser')
                        post=postsoup.body.find('div',attrs={'role':'main'})
                        thing_to_write=post.text.split('(')[0]
                        ##this is to take care of
                        ##'(There are no discussion topics yet in this forum)' text
                        save_post_with_name=dwl_path+fil_name+'.txt'

                        if(os.path.isfile(save_post_with_name)):
                            print 'File %s already exists'%(save_post_with_name)
                        else:
                            with open(save_post_with_name, 'w') as g:
                                g.write(thing_to_write)
                                print 'Forum post written to %s'%(save_post_with_name)

                    if('folder' in ref):
                        print 'Unable to download folder.'##Adjust for now.
                    
