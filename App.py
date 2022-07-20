from logging import PlaceHolder
from streamlit_autorefresh import st_autorefresh
from requests import session
import streamlit as st
import pandas as pd
import numpy as np
import time
import math

# Import data model
from bay import bay
from group import group
from user import user
from waitlist import waitlist

# Set streamlit app config
st.set_page_config(
    page_title="Real-Time Waitlist monitoring dashboard",
    layout="wide"
)

# Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
# after it's been refreshed 100 times.
count = st_autorefresh(interval=1000, key="fizzbuzzcounter")

# Initialize bays if they don't already exist
if "bay1" not in st.session_state:
	st.session_state["bay1"] = bay()
	st.session_state["bay2"] = bay()
# Initialize waitlist if it doesn't already exist
if "waitlist" not in st.session_state:
	st.session_state["waitlist"] = waitlist()

placeholder = st.empty()

with placeholder.container():
# Step 1: Display bays with their current status
	st.title("Uncontained VR operator console")
	bay_1_status, bay_2_status = st.columns(2)
	elapsed_time_1, elapsed_time_2 = 0, 0

	bay_1_status.subheader("Bay 1 status")
	if st.session_state["bay1"].is_available():
		bay_1_status.success("Available")
	else:
		bay_1_status.error(f"In session. In use by group: {st.session_state['bay1'].get_curr_group()}")
		# Elapsed time in seconds
		elapsed_time_1 = math.floor((time.time() - st.session_state["bay1"].get_session_start_time()))
		elapsed_time_percent_1 = elapsed_time_1 * 10 if elapsed_time_1 <= 10 else 100
		bay_1_status.text(f"Time remaining: {max(10-elapsed_time_1, 0)} seconds")
		my_bar = bay_1_status.progress(elapsed_time_percent_1)
		# After complete set as available
		if elapsed_time_percent_1 >= 100:
			st.session_state["bay1"].make_available()
			if (st.session_state["bay2"].is_available()):
				st.session_state["waitlist"].update_waiting_times_session_end()


	bay_2_status.subheader("Bay 2 status")
	if st.session_state["bay2"].is_available():
		bay_2_status.success("Available")
	else:
		bay_2_status.error(f"In session. In use by group: {st.session_state['bay2'].get_curr_group()}")
		elapsed_time_2 = math.floor((time.time() - st.session_state["bay2"].get_session_start_time()))
		elapsed_time_percent_2 = elapsed_time_2 * 10 if elapsed_time_2 <= 10 else 100
		bay_2_status.text(f"Time remaining: {max(10-elapsed_time_2, 0)} seconds")
		if (len(st.session_state["waitlist"].get_curr_waitlist()) > 0):
			if (elapsed_time_1 > 0):
				st.session_state["waitlist"].update_waiting_times(10-elapsed_time_1, 10-elapsed_time_2)
			elif(elapsed_time_1 == 0):
				st.session_state["waitlist"].update_waiting_times(0, 10-elapsed_time_2)
		my_bar = bay_2_status.progress(elapsed_time_percent_2)
		if elapsed_time_percent_2 == 100:
			st.session_state["bay2"].make_available()
			if (st.session_state["bay1"].is_available()):
				st.session_state["waitlist"].update_waiting_times_session_end()

	# Step 2: Display existing waitlist as df for now
	if len(st.session_state["waitlist"].get_curr_waitlist()) > 0:
		st.subheader("Current waitlist")
		st.table(st.session_state["waitlist"].waitlist_to_dataframe())
	
		# Step 2a: Move user to available bay
		if st.session_state.bay1.is_available() or st.session_state.bay2.is_available():
			b1, b2, b3, _, _, _, _, _= st.columns(8)
			if st.session_state.bay1.is_available():
				move_bay1 = b1.button("Move to bay 1")
				if move_bay1:
					# Move to bay 1
					g = st.session_state["waitlist"].remove_first_group()
					st.session_state["bay1"].occupy_bay(g.get_group_name())	
			else:
				move_bay1 = b1.button("Move to bay 1", key=None, help=None, on_click=None, args=None, kwargs=None, disabled=True)
			if st.session_state.bay2.is_available():
				move_bay2 = b2.button("Move to bay 2")
				if move_bay2:
					# Move to bay 2
					g = st.session_state["waitlist"].remove_first_group()
					st.session_state["bay2"].occupy_bay(g.get_group_name())	
			else:
				move_bay2 = b2.button("Move to bay 2", key=None, help=None, on_click=None, args=None, kwargs=None, disabled=True)
			if len(st.session_state["waitlist"].get_curr_waitlist()) > 1:
				move_to_end = b3.button("Move to end of waitlist")
				if move_to_end:
					g = st.session_state["waitlist"].remove_first_group()
					st.session_state["waitlist"].add_group_to_waitlist(g)
					bay1_remaining_time = 0 
					if not st.session_state["bay1"].is_available():
						bay1_remaining_time = 10 - math.floor((time.time() - st.session_state["bay1"].get_session_start_time()))	
					bay2_remaining_time = 0
					if not st.session_state["bay2"].is_available():
						bay2_remaining_time = 10 - math.floor((time.time() - st.session_state["bay2"].get_session_start_time()))
					st.session_state["waitlist"].update_waiting_times(bay1_remaining_time, bay2_remaining_time)
					st.experimental_rerun()
			else:
				move_to_end = b3.button("Move to end of waitlist", key=None, help=None, on_click=None, args=None, kwargs=None, disabled=True)
		else:
			b1, b2, b3, _, _, _, _, _= st.columns(8)
			move_bay1 = b1.button("Move to bay 1", key=None, help=None, on_click=None, args=None, kwargs=None, disabled=True)
			move_bay2 = b2.button("Move to bay 2", key=None, help=None, on_click=None, args=None, kwargs=None, disabled=True)
			move_to_end = b3.button("Move to end of waitlist", key=None, help=None, on_click=None, args=None, kwargs=None, disabled=True)

	# Step 3: Add option to add group to waitlist (streamlit form works just fine heres)
	with st.form(key="my_form"):
		st.subheader("Sign up for waitlist")		
		# Every form must have a submit button.
		group_name = st.text_input("Group name")
		st.text("Group members")
		col1, col2, col3, col4 = st.columns(4)
		user1_firstname = col1.text_input("First name")
		user1_lastname = col2.text_input("Last name")
		user1_email = col3.text_input("email")
		user1_phone = col4.text_input("phone")
		
		submitted = st.form_submit_button("Join waitlist")
		if submitted:
			user1 = user(user1_firstname, user1_lastname, user1_email, user1_phone)
			waiting_time1 = st.session_state["waitlist"].get_curr_waiting_time()
			group1 = group(group_name, [user1], waiting_time1)
			st.session_state["waitlist"].add_group_to_waitlist(group1)
			st.experimental_rerun()


