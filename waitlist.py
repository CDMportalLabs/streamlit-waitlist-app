from tokenize import group
import pandas as pd
import time
import datetime
from node import LinkedList

class waitlist:

	def __init__(self):
		# This will hold a list of groups -> inorder
		self.waitlist = LinkedList()
	
	def get_curr_waitlist(self):
		return self.waitlist
	
	def get_first_group(self):
		return self.waitlist.head.data
	
	def remove_first_group(self):
		self.waitlist.delFromBeginning()
	
	def update_waiting_times_session_end(self):
		i = 0
		curr = self.waitlist.head
		while (curr != None):
			if (i == 0):
				curr.data.update_waiting_time(0)
			else:
				curr.data.update_waiting_time((i-1) * 10)
			i += 1
			curr = curr.next
		# for i, group in enumerate(self.waitlist):
		# 	if (i == 0):
		# 		group.update_waiting_time(0)
		# 	else:
		# 		group.update_waiting_time((i-1) * 10)
	
	def update_waiting_times(self, bay1RemainingTime, bay2RemainingTime):
		i = 0
		curr = self.waitlist.head
		while (curr != None):
			if (i == 0):
				curr.data.update_waiting_time(max(min(bay1RemainingTime, bay2RemainingTime), 0))
			else:
				if ((i-1) % 2 == 0):
					curr.data.update_waiting_time((i-1) * 10 + bay2RemainingTime)
				else:
					curr.data.update_waiting_time((i-1) * 10 + bay1RemainingTime)
			i += 1
			curr = curr.next
		# for i, group in enumerate(self.waitlist):
		# 	if (i == 0):
		# 		group.update_waiting_time(max(min(bay1RemainingTime, bay2RemainingTime), 0))
		# 	else:
		# 		if ((i-1) % 2 == 0):
		# 			group.update_waiting_time((i-1) * 10 + bay2RemainingTime)
		# 		else:
		# 			group.update_waiting_time((i-1) * 10 + bay1RemainingTime)

	def get_curr_waiting_time(self):
		# will be replaced with (bay remaining time + waitlist length * 15)
		return (self.waitlist.getLength()-1) * 10 if self.waitlist.getLength() >= 1 else 0 
	
	def add_group_to_waitlist(self, group):
		# print(group.get_group_name())
		self.waitlist.insertAtEnd(group)

	def remove_group_from_waitlist(self, position):
		self.waitlist.delAtPos(position)


	def waitlist_to_dataframe(self):
		# Extract columns
		group_names = []
		group_times = []
		group_members = []
		group_waiting_times = []
		curr = self.waitlist.head
		while (curr != None):
			group_names.append(curr.data.get_group_name())
			group_times.append(curr.data.get_timestamps())
			group_members.append(curr.data.get_members())
			group_waiting_times.append(curr.data.get_waiting_time())
			curr = curr.next
		# group_times = [group.get_timestamps() for group in self.waitlist]
		# group_members = [group.get_members() for group in self.waitlist]
		# group_waiting_times = [group.get_waiting_times() for group in self.waitlist]
		group_members_names = []
		group_members_phones = []
		group_members_emails = []
		for group in group_members:
			group_members_names.append([f'{member.get_first_name()} {member.get_last_name()}' for member in group])
			group_members_phones.append([f'{member.get_phone_number()}' for member in group])
			group_members_emails.append([f'{member.get_email()}' for member in group])
		
		return pd.DataFrame({'Group Name': group_names, 'Group Time': group_times, 'Group Members': group_members_names, 'Group Members Phone': group_members_phones, 'Group Members Email': group_members_emails, 'Group Waiting Time': group_waiting_times})
	
	
		