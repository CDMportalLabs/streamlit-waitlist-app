# Create a class for a group object
import datetime

class group:
	def __init__(self, group_name, members):
		self.group_name = group_name
		self.members = members
		self.timestamp = datetime.datetime.now()
	
	def get_group_name(self):
		return self.group_name
	
	def get_members(self):
		return self.members
	
	def get_timestamps(self):
		return self.timestamp
		
