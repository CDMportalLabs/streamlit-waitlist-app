from logging import PlaceHolder
from streamlit_autorefresh import st_autorefresh
from requests import session
import streamlit as st
import pandas as pd
import numpy as np
import time
import math
from firebase_admin import initialize_app, delete_app, get_app
from firebase_admin import credentials, firestore

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

# # initialize sdk
# cred = credentials.Certificate("./serviceAccountKey.json")
# try:
#     default_app = get_app()
# except ValueError:
#     default_app = initialize_app(cred)
# # initialize firestore instance
# firestore_db = firestore.client()

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

if (st.session_state["bay1"].is_available()):
	if (st.session_state["bay1"].is_alert_on()):
		st.info("Bay 1 is freed up!")
		st.session_state["bay1"].set_alert_off()
	
if (st.session_state["bay2"].is_available()):
	if (st.session_state["bay2"].is_alert_on()):
		st.info("Bay 2 is freed up!")
		st.session_state["bay2"].set_alert_off()

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
		elapsed_time_1 = min(math.floor((time.time() - st.session_state["bay1"].get_session_start_time())), 10)
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
		elapsed_time_2 = min(math.floor((time.time() - st.session_state["bay2"].get_session_start_time())), 10)
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
		user1_col1, user1_col2, user1_col3, user1_col4 = st.columns(4)
		user1_firstname = user1_col1.text_input("First name", key = "user1_first_name")
		user1_lastname = user1_col2.text_input("Last name", key = "user1_last_name")
		user1_email = user1_col3.text_input("email", key = "user1_email")
		user1_phone = user1_col4.text_input("phone", key = "user1_phone")
		
		user2_col1, user2_col2, user2_col3, user2_col4 = st.columns(4)
		user2_firstname = user2_col1.text_input("First name", key = "user2_first_name")
		user2_lastname = user2_col2.text_input("Last name", key = "user2_last_name")
		user2_email = user2_col3.text_input("email", key = "user2_email")
		user2_phone = user2_col4.text_input("phone", key = "user2_phone")

		user3_col1, user3_col2, user3_col3, user3_col4 = st.columns(4)
		user3_firstname = user3_col1.text_input("First name", key = "user3_first_name")
		user3_lastname = user3_col2.text_input("Last name", key = "user3_last_name")
		user3_email = user3_col3.text_input("email", key = "user3_email")
		user3_phone = user3_col4.text_input("phone", key = "user3_phone")

		submitted = st.form_submit_button("Join waitlist")
		if submitted:
			user1 = user(user1_firstname, user1_lastname, user1_email, user1_phone)
			user2 = user(user2_firstname, user2_lastname, user2_email, user2_phone)
			user3 = user(user3_firstname, user3_lastname, user3_email, user3_phone)
			users = [user1, user2, user3]
			# for usr in users:		
			# 	firestore_db.collection(u'users').add({
			# 		u"firstName": usr.get_first_name(),
			# 		u"lastName": usr.get_last_name(),
			# 		u"email": usr.get_email(),
			# 		u"phone": usr.get_phone_number()
			# 	})
			waiting_time1 = st.session_state["waitlist"].get_curr_waiting_time()
			group1 = group(group_name, users, waiting_time1)
			st.session_state["waitlist"].add_group_to_waitlist(group1)
			st.experimental_rerun()

# try:
#     delete_app(default_app)
# except ValueError:
#     pass
