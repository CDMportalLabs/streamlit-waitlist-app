import pandas as pd
import time
import datetime

class waitlist:

	def __init__(self):
		# This will hold a list of groups -> inorder
		self.waitlist = []
	
	def get_curr_waitlist(self):
		return self.waitlist
	
	def remove_first_group(self):
		group = self.waitlist.pop(0)
		return group
	
	def update_waiting_times_session_end(self):
		for i, group in enumerate(self.waitlist):
			if (i == 0):
				group.update_waiting_time(0)
			else:
				group.update_waiting_time((i-1) * 15)
	
	def update_waiting_times(self, bay1RemainingTime, bay2RemainingTime):
		for i, group in enumerate(self.waitlist):
			if (i == 0):
				group.update_waiting_time(max(min(bay1RemainingTime, bay2RemainingTime), 0))
			else:
				if ((i-1) % 2 == 0):
					group.update_waiting_time((i-1) * 15 + bay2RemainingTime)
				else:
					group.update_waiting_time((i-1) * 15 + bay1RemainingTime)

	def get_curr_waiting_time(self):
		# will be replaced with (bay remaining time + waitlist length * 15)
		return (len(self.waitlist)-1) * 15 if len(self.waitlist) >= 1 else 0 
	
	def get_waiting_times(self):
		return [group.get_waiting_times() for group in self.waitlist]
	
	def add_group_to_waitlist(self, group):
		self.waitlist.append(group)
	
	def waitlist_to_dataframe(self):
		# Extract columns
		group_names = [group.get_group_name() for group in self.waitlist]
		group_times = [group.get_timestamps() for group in self.waitlist]
		group_members = [group.get_members() for group in self.waitlist]
		group_waiting_times = [group.get_waiting_times() for group in self.waitlist]
		group_members_names = []
		group_members_phones = []
		group_members_emails = []
		for group in group_members:
			group_members_names.append([f'{member.get_first_name()} {member.get_last_name()}' for member in group])
			group_members_phones.append([f'{member.get_phone_number()}' for member in group])
			group_members_emails.append([f'{member.get_email()}' for member in group])
		
		return pd.DataFrame({'Name': group_names, 'Timestamp': group_times, 'Members': group_members_names, 'Phone': group_members_phones, 'Email': group_members_emails, 'Waiting Time': group_waiting_times})
	
	
		