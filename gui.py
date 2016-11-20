from tkinter import *
import ttk
import tkFileDialog
import tkMessageBox
from datetime import datetime
import time as tm
import cms_login as cms
import os
import csv

class Gui:
	data_file='.CMS_username.csv'
	directory=None
	activity = []

	def __init__(self, master):
		frame=Frame(root)
		self.createGui()

	def createGui(self):

		root.configure(background='white')
		self.status_text = StringVar()

		settingsmenu = Menu(root, tearoff=0)
		root.config(menu=settingsmenu)
		root.wm_title("CMS downloader v1.0 Alpha")

		submenu = Menu(settingsmenu, tearoff=0)
		settingsmenu.add_cascade(label="Settings", menu=submenu)
		# submenu.add_command(label="Run Now", command=self.check_courses)
		submenu.add_command(label="Add/Remove users", command=self.userconsole)
		# submenu.add_command(label="Log in as different user (Currently %s )"%(self.load_details(Gui.data_file).keys()[0]), command=self.userconsole)
		submenu.add_command(label="Change downloads directory", command=self.askdir)

		submenu.add_separator()
		submenu.add_command(label="Exit", command=root.destroy)

		helpsubmenu = Menu(settingsmenu, tearoff=0)
		settingsmenu.add_cascade(label="Help", menu=helpsubmenu)
		helpsubmenu.add_command(label="Read Me", command=self.readmewindow)
		helpsubmenu.add_separator()
		helpsubmenu.add_command(label="Report bug", command=self.doNothing)
		helpsubmenu.add_command(label="Contact dev", command=self.doNothing)

		self.runbutton = Button(root, text="Check my courses now", font="serif 14", bg="dodger blue", fg="white",
								relief=FLAT, command=self.check_courses)

		self.newsbutton = Button(root, text="Check  site  news", font="serif 14", bg="white", fg="black", relief=FLAT,
								 command=self.check_news)

		self.tree = ttk.Treeview(root)
		self.tree['show'] = 'headings'
		self.tree["columns"] = ("File Name", "Course", "Path", "Date Added")
		self.tree.column("File Name", width=250, stretch=True)
		self.tree.column("Course", width=250, stretch=True)
		self.tree.column("Path", width=200, stretch=True)
		self.tree.column("Date Added", width=150, stretch=True)
		self.tree.heading("File Name", text="File Name")
		self.tree.heading("Course", text="Course")
		self.tree.heading("Path", text="Path")
		self.tree.heading("Date Added", text="Date Added")
		dwld_data=[]
		if os.path.isfile('.cms-dl_downloads.csv') and os.stat('.cms-dl_downloads.csv').st_size!=0:
			with open('.cms-dl_downloads.csv', 'r') as dwlfile:
					dwldreader = csv.reader(dwlfile)
					dwld_data = list(dwldreader)
		print dwld_data
		if(len(dwld_data)>0):
			for dwlds in dwld_data:
				self.tree.insert('', 'end',values=(dwlds[0],dwlds[1], dwlds[2],dwlds[3]))


		# self.lastbutton = Button(root, text="Show last scan results", font="serif 12",relief=FLAT,
		# 						 command=self.show_last)
		self.progress = ttk.Progressbar(root, orient=HORIZONTAL, length=200, mode='determinate')

		self.statusbar = Label(root, bd=2, bg="white", relief=SUNKEN, font="serif 12")

		self.runbutton.pack(anchor=NW, expand=True,fill=Y, padx=10, pady=10, ipadx=1, ipady=1)
		self.newsbutton.pack(anchor=W, expand=True,fill=Y, padx=10, pady=2, ipadx=1, ipady=1)
		self.progress.pack(side=BOTTOM, anchor=SE, expand=True, fill=BOTH, padx=(10, 10), pady=(5, 5))
		self.statusbar.pack(side=BOTTOM, anchor=SE, expand=True, fill=BOTH, padx=(10, 10), pady=(5, 5))
		self.tree.pack(fill=BOTH, expand=True, padx=(10, 10), anchor=SW, side=BOTTOM)

	def doNothing(self):
		pass

	def readmewindow(self):
		readme=Toplevel(root)
		readme.title("Read Me")
		readme.config(bg="white", padx=5,pady=10)
		with open('README.md', 'r') as readfile:
			readtext=readfile.read()
		text=Text(readme, bg="white", font="helvetica 12")
		text.insert(END, readtext)
		text.pack(fill=BOTH, padx=10, pady=10)

	def askdir(self):
		# global directory
		Gui.directory=tkFileDialog.askdirectory(parent=root, mustexist=True)
		print "askdir"
		#if directory:
		#	self.directory_var.set(directory)

	def nowtime(self):
		return datetime.now().strftime('%I:%M:%S %p,%d/%m/%Y')

	def userconsole(self):
		userconsolewindow=Toplevel(root)
		userconsolewindow.title("Add/Remove Users")
		userconsolewindow.config(bd=2)
		userdata=self.load_details(Gui.data_file)
		addusertext='Add User'
		if(not userdata):
			self.newlabel = Label(userconsolewindow, bd=2, relief=FLAT, text="Hi ! Looks like you're new here.\n Add a user below to start.",font="helvetica 12").grid(column=0,columnspan=5,row=1, padx=(5,5),pady=10)
		else:
			Label(userconsolewindow, bd=2, relief=FLAT,
				  text="Choose a user :", font="helvetica 12").grid(
				column=0, columnspan=5, row=0, padx=(5, 5), pady=5)
			for user in userdata:
				Button(userconsolewindow, text=user[0], relief=RAISED,font="serif 12",command=self.doNothing).grid(column=2,row=1,ipadx=3,ipady=1,padx=5,pady=10)
				addusertext = 'Add another user'
		addusers=Button(userconsolewindow, text=addusertext, relief=RAISED,bg="lime green",fg="white", font="serif 14", command=self.adduser)
		addusers.grid(column=2,row=3,padx=10,pady=10)

	def adduser(self):

		adduserwindow = Toplevel(root)
		adduserwindow.title("Add User")

		userlabel=Label(adduserwindow, text="CMS Username", font="serif 12")
		self.username=StringVar()
		self.password=StringVar()
		userentry=Entry(adduserwindow, relief=SUNKEN, bg="white",font="serif 12",textvariable=self.username)
		pwdlabel=Label(adduserwindow, text="CMS Password", font="serif 12")
		pwdentry=Entry(adduserwindow, relief=SUNKEN, bg="white", show="*",font="serif 12",textvariable=self.password)
		addbut=Button(adduserwindow, text="Add User", relief=RAISED,bg="lime green",fg="white", font="serif 14", command=self.save_details)

		userlabel.grid(column=0,row=0,padx=10,pady=10)
		userentry.grid(column=1,columnspan=3, row=0,ipadx=3,ipady=1,padx=(10,10),pady=(10,10))
		pwdlabel.grid(column=0,row=1,padx=10,pady=5)
		pwdentry.grid(column=1,columnspan=3,row=1,ipadx=3,ipady=1,padx=(10,10),pady=(10,10))
		addbut.grid(column=1,row=2,pady=10)

		return (self.username, self.password)

	def save_details(self):
		save_username=self.username.get()
		save_pwd=self.password.get()
		if len(save_username)>=1 and len(save_pwd)>=1:
			userdata = (str(save_username),str(save_pwd),str(Gui.directory))
			with open('.CMS_username.csv', 'a') as userfile:
				userwriter=csv.writer(userfile)
				userwriter.writerow(userdata)
			tkMessageBox.showinfo(title="Added",message="User %s has been added "%(save_username))
		else:
			tkMessageBox.showerror("Error","You can't have an empty username/password -_- ")

	def load_details(self,details_file):
		if os.path.isfile(details_file) and os.stat(details_file).st_size != 0:
			with open(details_file, 'r') as reader:
					csvreader = csv.reader(reader)
					datafile = list(csvreader)
			#print "datafile=",datafile
			return datafile
		else:
			return False
		# Include option to overwrite,login as different user.
		# May have to change data storage type to recognise different users.
		# return (user, pwd)
	def show_report(self,list):
		self.report=Toplevel(root)
		self.report.title("Report")
		self.report.minsize(width=600,height=500)
		self.report_tree=ttk.Treeview(self.report,show='headings')
		self.report_tree["columns"]=("Course", "Activity")
		self.report_tree.column("Course", minwidth=350, stretch=True)
		self.report_tree.column("Activity", minwidth=50, stretch=True)
		self.report_tree.heading("Course", text="Course")
		self.report_tree.heading("Activity", text="Activity")
		for i in list:
			self.report_tree.insert('', 'end',values=(i[1], i[2]))

		self.ok=Button(self.report, text="  OK  ", font="helvetica 12", fg="black", relief=RAISED,command=self.report.destroy)
		self.report_tree.pack(fill=BOTH, expand=True, padx=(20, 20), pady=(20, 20),side=TOP)
		self.ok.pack(expand=False,padx=20,pady=10,anchor=SE,side=BOTTOM)

	def check_news(self):
		if (not cms.init()):
			tkMessageBox.showerror("Connection Error", "Unable to connect to CMS now. Please try again later.")
			# self.status.config(bg="red",text="Cannot connect to CMS")
			return False
		cms.check_site_news()

	def login_to_cms(self):
		if (not cms.init()):
			tkMessageBox.showerror("Connection Error", "Unable to connect to CMS now. Please try again later.")
			self.statusbar.config(bg="firebrick2",text="  Cannot connect to CMS  ")
			return False
			# global data_file
		
		self.user_details = self.load_details(Gui.data_file)
		# print user_details
		if (self.user_details != None):
			self.website = cms.submit_form(self.user_details)
			if (self.website == False):
				tkMessageBox.showerror("User details Error",
									   "Looks like there is an error in your user details. Please check them again")
				return False
		return True
	def check_courses(self):
		self.progress['value']=0
		self.progress['maximum'] = 100
		print "Checking courses"
		if(self.login_to_cms()):
			user_land_soup = cms.get_init_soup(self.website)
			print "Hello %s !" % (cms.get_name(user_land_soup))
			#self.status_text.set("Hello "+cms.get_name(user_land_soup)+" !")
			self.statusbar.config(bg="white",fg="black", text='Hello'+cms.get_name(user_land_soup), font="helvetica 12")
			root.update_idletasks()
			course_box = cms.get_course_boxes(cms.get_init_soup(self.website))
			for coursebox in course_box:
				course_links = coursebox.find_all('a')
				# Link to the course page is found.
				# course_site_read='C:/Python27/CMS%20downloader/cms_login_dataset/Course_%20CS_ECE_EEE_INSTR%20F215%20DIGITAL%20DESIGN%20LS1.html'
				for course in course_links:
					coursename=cms.course_details(course)[0]
					status = "Checking %s ......" % coursename
					print status
					self.statusbar.config(bg="goldenrod1", fg="brown", text=status, font="serif 12")
					root.update_idletasks()
					checkresult = cms.check_each_course(course)
					guitimestamp = cms.timestamp
					if (not checkresult):
						status='No recent activity'
						self.statusbar.config(bg="lime green", fg="white", text=status, font="serif 12")
						root.update_idletasks()
						Gui.activity.append((guitimestamp,coursename,'No activity'))
					tm.sleep(1)
					self.progress["value"] += self.progress['maximum'] // len(course_box)
			print "Done checking"
			self.statusbar.config(bg="lime green", fg="white", text='Done checking', font="serif 10")
			self.progress["value"] = self.progress['maximum']
			root.update_idletasks()
			self.show_report(Gui.activity)

	def show_last(self):
		if os.path.isfile('.Lastactivity.csv') and os.stat('.Lastactivity.csv').st_size!=0:
			with open('.Lastactivity.csv', 'r') as chandler:
					activityreader = csv.reader(chandler)
					activitydata = list(activityreader)
					# print activitydata,type(activitydata)
		self.show_report(activitydata)


root=Tk()
t=Gui(root)
root.mainloop()
