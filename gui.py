from tkinter import *
import ttk
import tkFileDialog
import tkMessageBox
from datetime import datetime
import cms_login as cms
import os
import csv

class Gui:
	data_file='CMS_username.csv'
	directory=None


	#status_text.set(cms.status)

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

	def askuser(self):
		print "askuser"
		askuserwindow=Toplevel(root)
		askuserwindow.title("Enter your CMS details")
		askuserwindow.config(bd=2)
		userlabel=Label(askuserwindow, text="Username:", font="serif 14")
		self.username=StringVar()
		self.password=StringVar()
		userentry=Entry(askuserwindow, relief=SUNKEN, bg="white",textvariable=self.username)
		pwdlabel=Label(askuserwindow, text="Password:", font="serif 14")
		pwdentry=Entry(askuserwindow, relief=SUNKEN, bg="white", show="*",textvariable=self.password)
		self.remember=BooleanVar()
		ask_to_remember=Checkbutton(askuserwindow, text="Remember details", font="serif 14", variable=self.remember)
		confirmbut=Button(askuserwindow, text="Confirm", relief=RAISED,bg="blue",fg="white", font="serif 14", command=self.save_details)

		userlabel.pack(fill=BOTH, expand=True, anchor=NW, padx=2)
		userentry.pack(fill=BOTH, anchor=NE, padx=2)
		pwdlabel.pack(fill=BOTH, expand=True, anchor=SW, padx=2)
		pwdentry.pack(fill=BOTH, anchor=SE, padx=2)
		ask_to_remember.pack()
		confirmbut.pack(expand=True, anchor=S, padx=20, pady=2)

		return (self.username, self.password)

	def save_details(self):
		save_username=self.username.get()
		save_pwd=self.password.get()
		#self.directory_var=StringVar(root)
		self.click_count=IntVar(root)
		if self.remember.get():
			if len(save_username)>=1 and len(save_pwd)>=1:
				userdata = (str(save_username),str(save_pwd),str(Gui.directory))
				with open('CMS_username.csv', 'w') as userfile:
					userwriter=csv.writer(userfile)
					userwriter.writerow(userdata)
				tkMessageBox.showinfo(title="Updated",message="Your login details have been updated with username %s"%(save_username))
			else:
				tkMessageBox.showerror("Error","You can't have an empty username/password -_- ")

	def load_details(self,details_file):
		if os.path.isfile(details_file) and os.stat(details_file).st_size != 0:
			with open(details_file, 'r') as reader:
					csvreader = csv.reader(reader)
					datafile = list(csvreader)
			# print "datafile=",datafile
			return datafile
			#userdata = datafile.read()
			#user, pwd = map(str, userdata.split(','))
			#datafile.close()
		else:
			self.askuser()
			# self.askdir()
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
		self.report_tree.pack(fill=BOTH, expand=True, padx=(20, 20), pady=(20, 20))

	def check_news(self):
		if (not cms.init()):
			tkMessageBox.showerror("Connection Error", "Unable to connect to CMS now. Please try again later.")
			# self.status.config(bg="red",text="Cannot connect to CMS")
			return False
		cms.check_site_news()

	def login_to_cms(self):
		if (not cms.init()):
			tkMessageBox.showerror("Connection Error", "Unable to connect to CMS now. Please try again later.")
			self.statusbar.config(bg="red",text="Cannot connect to CMS")
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
		print "Checking courses"
		if(self.login_to_cms()):
			user_land_soup = cms.get_init_soup(self.website)
			print "Hello %s !" % (cms.get_name(user_land_soup))
			self.status_text.set("Hello "+cms.get_name(user_land_soup)+" !")
			self.statusbar.config(bg="blue",fg="white", text=cms.get_name(user_land_soup))
			activity=cms.check_my_courses(self.website)
			if activity:
				print self.show_report(activity)
				self.show_report(activity)

	def show_last(self):
		lastscan=Toplevel(root)
		lastscan.minsize(width=900,height=500)
		lastscan.title("Last Scan Results")
		#lastscan.config(bg="white", bd=2)
		self.scantree=ttk.Treeview(lastscan,displaycolumns='#all')
		self.scantree['show']='headings'
		self.scantree["columns"]=("Timestamp", "Course", "Activity")
		self.scantree.column("Timestamp", minwidth=350, stretch=True)
		self.scantree.column("Course", minwidth=350, stretch=True)
		self.scantree.column("Activity", width=50, stretch=True)
		self.scantree.heading("Timestamp", text="Timestamp")
		self.scantree.heading("Course", text="Course")
		self.scantree.heading("Activity", text="Activity")

		if os.path.isfile('Lastactivity.csv') and os.stat('Lastactivity.csv').st_size!=0:
			with open('Lastactivity.csv', 'r') as chandler:
					activityreader = csv.reader(chandler)
					activitydata = list(activityreader)
					# print activitydata,type(activitydata)
					for i in activitydata:
						# print i
						self.scantree.insert('', 0,
								 values=(i[0],i[1], i[2]))
		self.scantree.pack(fill=BOTH, expand=True, padx=(20, 20), pady=(20, 20))

	def __init__(self, master):
		frame=Frame(root)
		settingsmenu = Menu(root, tearoff=0)
		root.config(menu = settingsmenu)
		root.wm_title("CMS downloader v1.0 Alpha")

		submenu = Menu(settingsmenu, tearoff=0)
		settingsmenu.add_cascade(label="Settings", menu=submenu)
		# submenu.add_command(label="Run Now", command=self.check_courses)
		submenu.add_command(label="Change user details", command=self.askuser)
		#submenu.add_command(label="Log in as different user (Currently %s )"%(self.load_details(Gui.data_file).keys()[0]), command=self.askuser)
		submenu.add_command(label="Change downloads directory", command=self.askdir)

		submenu.add_separator()
		submenu.add_command(label="Exit", command=root.destroy)

		helpsubmenu=Menu(settingsmenu, tearoff=0)
		settingsmenu.add_cascade(label="Help", menu=helpsubmenu)
		helpsubmenu.add_command(label="Read Me", command=self.readmewindow)
		helpsubmenu.add_separator()
		helpsubmenu.add_command(label="Report bug", command=self.doNothing)
		helpsubmenu.add_command(label="Contact dev", command=self.doNothing)

		self.tree=ttk.Treeview(master)
		self.tree['show']='headings'
		self.tree["columns"]=("File Name", "Course", "Path", "Date Added", "File Size")
		self.tree.column("File Name", width=100, stretch=True)
		self.tree.column("Course", width=100, stretch=True)
		self.tree.column("Path", width=100, stretch=True)
		self.tree.column("Date Added", width=100, stretch=True)
		self.tree.column("File Size", width=100, stretch=True)
		self.tree.heading("File Name", text="File Name")
		self.tree.heading("Course", text="Course")
		self.tree.heading("Path", text="Path")
		self.tree.heading("Date Added", text="Date Added")
		self.tree.heading("File Size", text="File Size")
		self.tree.insert('', 0, 'gallery',
						 values=("File1", "MATH", "C:/", datetime.now().strftime('%I:%M:%S %p,%d/%m/%Y'), "14.3 kB"))

		self.runbutton=Button(master, text="Check my courses now", font="serif 18",bg="green",fg="black", relief=RAISED,command=self.check_courses)
		self.newsbutton=Button(master,text="Check site news",font="serif 14",relief=RAISED,command=self.check_news)
		self.lastbutton=Button(master, text="Show last scan results", font="serif 12", relief=RAISED,command=self.show_last)
		#self.progress = ttk.Progressbar(master, mode='indeterminate', name='run Progress')
		self.status_text = StringVar()
		self.statusbar=Label(master, bd=2,bg="white", relief=SUNKEN, anchor=W, font="serif 14",textvariable=self.status_text)

		self.runbutton.pack(anchor=NW, expand=True, padx=20,pady=5, ipadx=1, ipady=1)
		self.newsbutton.pack(anchor=W, expand=True, padx=20,pady=5,ipadx=1, ipady=1)
		self.lastbutton.pack(anchor=W,expand=True,padx=20,pady=5,ipadx=1,ipady=1,side=TOP)
		#self.progress.pack(side=BOTTOM, fill=X, expand=True, anchor=SE, padx=(2, 2), pady=(2, 2))
		self.statusbar.pack(side=BOTTOM, fill=X, expand=True, anchor=SE, padx=(2, 2), pady=(2, 2))
		self.tree.pack(fill=BOTH, expand=True, padx=(20, 20), pady=(20, 20), anchor=SW, side=BOTTOM)


root=Tk()
t=Gui(root)
root.mainloop()
