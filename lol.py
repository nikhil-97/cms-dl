import pickle
import os
activity_list=[('Activity since Thursday, 6 October 2016, 3:18 AM', 'CS/ECE/EEE/INSTR F215 DIGITAL DESIGN LS1', "('No recent activity',)"), ('Activity since Thursday, 6 October 2016, 3:18 AM', 'ECE/EEE/INSTR F211 ELECTRICAL MACHINES LS1', "('No recent activity',)")]
with open('activity.dat', 'wb') as writefile:
    pickle.dump(activity_list, writefile, protocol=pickle.HIGHEST_PROTOCOL)
if os.path.isfile('activity.dat') and os.stat('activity.dat').st_size!=0:
    with open('activity.dat', 'rb') as chandler:
        print repr(chandler.read())
        activitydata=pickle.load(chandler)
        print activitydata
