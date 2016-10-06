from tkinter import *
import ttk
import tkFileDialog
import tkMessageBox
from datetime import datetime
import pickle as pckl
import cms_login as cms
import os

class Gui:
	data_file='CMS_username.dat'
	directory=None
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
				userdata = {str(save_username):(str(save_pwd),str(Gui.directory))}
				with open('CMS_username.dat', 'wb') as handle:
					pckl.dump(userdata, handle, protocol=pckl.HIGHEST_PROTOCOL)
				tkMessageBox.showinfo(title="Updated",message="Your login details have been updated with username %s"%(save_username))
			else:
				tkMessageBox.showerror("Error","You can't have an empty username/password -_- ")

	def load_details(self,details_file):
		if os.path.isfile(details_file) and os.stat(details_file).st_size != 0:
			with open(details_file, 'rb') as chandler:
					datafile=pckl.load(chandler)
			print "datafile=",datafile
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

	def run_app(self):

		if(not cms.init()):
			tkMessageBox.showerror("Connection Error", "Unable to connect to CMS now. Please try again later.")
			self.status.config(bg="red",text="Cannot connect to CMS")
			return False
		#global data_file
		user_details=self.load_details(Gui.data_file)
		print user_details

		website=cms.submit_form(user_details)
		cms.main_job(website)

	def show_last(self):
		lastscan=Toplevel(root)
		lastscan.title("Last Scan Results")
		#lastscan.config(bg="white", bd=2)
		self.scantree=ttk.Treeview(lastscan)
		self.scantree['show']='headings'
		self.scantree["columns"]=("Timestamp", "Course", "Activity")
		self.scantree.column("Timestamp", width=100, stretch=True)
		self.scantree.column("Course", width=100, stretch=True)
		self.scantree.column("Activity", width=100, stretch=True)
		self.scantree.heading("Timestamp", text="Timestamp")
		self.scantree.heading("Course", text="Course")
		self.scantree.heading("Activity", text="Activity")

		if os.path.isfile('Lastactivity.dat') and os.stat('Lastactivity.dat').st_size!=0:
			with open('Lastactivity.dat', 'rb') as chandler:
					print repr(chandler.read())
					activitydata=pckl.load(chandler)
					print activitydata
					for i in activitydata:
						print i
						self.scantree.insert('', 0, 'gallery',
								 values=(i[0],i[1], i[2]))
		self.scantree.pack(fill=BOTH, expand=True, padx=(20, 20), pady=(20, 20))

	def __init__(self, master):
		frame=Frame(root)
		settingsmenu = Menu(root, tearoff=0)
		root.config(menu = settingsmenu)
		root.wm_title("CMS downloader v1.0 Alpha")

		submenu = Menu(settingsmenu, tearoff=0)
		settingsmenu.add_cascade(label="Settings", menu=submenu)
		# submenu.add_command(label="Run Now", command=self.run_app)
		submenu.add_command(label="Change user details", command=self.askuser)
		submenu.add_command(label="Log in as different user (Currently %s )"%(self.load_details(Gui.data_file).keys()[0]), command=self.askuser)
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

		self.runbutton=Button(master, text="Run Now", font="serif 20",bg="green",fg="black", relief=RAISED,command=self.run_app)
		self.lastbutton=Button(master, text="Show last scan results", font="serif 12", relief=RAISED,command=self.show_last)
		self.status=Label(master,  text="Status Bar", bd=2,bg="white", relief=SUNKEN, anchor=E, font="serif 10")

		self.runbutton.pack(anchor=NW, expand=True, padx=20, pady=(10, 10), ipadx=1, ipady=1)
		self.lastbutton.pack(anchor=W,expand=True,padx=20,pady=10,ipadx=1,ipady=1,side=TOP)
		self.status.pack(side=BOTTOM, fill=X, expand=True, anchor=SE, padx=(2, 2), pady=(2, 2))
		self.tree.pack(fill=BOTH, expand=True, padx=(20, 20), pady=(20, 20), anchor=SW, side=BOTTOM)


root=Tk()
t=Gui(root)
root.mainloop()
