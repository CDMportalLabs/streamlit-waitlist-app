
import pandas as pd

class waitlist:

	def __init__(self):
		# This will hold a list of groups -> inorder
		self.waitlist = []
	
	def get_curr_waitlist(self):
		return self.waitlist
	
	def remove_first_group(self):
		group = self.waitlist.pop(0)
		
		return group
	
	def add_group_to_waitlist(self, group):
		self.waitlist.append(group)
	
	def waitlist_to_dataframe(self):
		# Extract columns
		group_names = [group.get_group_name() for group in self.waitlist]
		group_times = [group.get_timestamps() for group in self.waitlist]
		group_members = [group.get_members() for group in self.waitlist]
		group_members_names = []
		group_members_phones = []
		group_members_emails = []
		for group in group_members:
			group_members_names.append([f'{member.get_first_name()} {member.get_last_name()}' for member in group])
			group_members_phones.append([f'{member.get_phone_number()}' for member in group])
			group_members_emails.append([f'{member.get_email()}' for member in group])
		
		
		return pd.DataFrame({'Group Name': group_names, 'Group Time': group_times, 'Group Members': group_members_names, 'Group Members Phone': group_members_phones, 'Group Members Email': group_members_emails})
	
	
		