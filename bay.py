import time

class bay:
	def __init__(self):
		# True for free, false for occupied
		self.available = True
		self.session_start_time = None
		self.curr_group = None
	
	def get_session_start_time(self):
		return self.session_start_time
	
	def is_available(self):
		return self.available
	
	def get_curr_group(self):
		return self.curr_group
	
	def occupy_bay(self, group_name):
		self.curr_group = group_name
		self.available = False
		self.session_start_time = time.time()
	
	def make_available(self):
		self.available = True
		self.session_start_time = None
		self.curr_group = None