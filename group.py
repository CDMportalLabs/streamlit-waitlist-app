# Create a class for a group object
import datetime

class group:
	def __init__(self, group_name, members, waiting_time):
		self.group_name = group_name
		self.members = members
		self.timestamp = datetime.datetime.now()
		self.waiting_time = waiting_time
	
	def get_group_name(self):
		return self.group_name
	
	def get_members(self):
		return self.members
	
	def get_timestamps(self):
		return self.timestamp
	
	def get_waiting_time(self):
		return self.waiting_time

	def update_waiting_time(self, time):
		self.waiting_time = time
		
