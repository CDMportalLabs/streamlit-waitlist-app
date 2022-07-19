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

	bay_1_status.subheader("Bay 1 status")
	if st.session_state["bay1"].is_available():
		bay_1_status.success("Available")
	else:
		bay_1_status.error(f"In session. In use by group: {st.session_state['bay1'].get_curr_group()}")
		# Elapsed time in seconds
		elapsed_time =  math.floor((time.time() - st.session_state["bay1"].get_session_start_time()))
		elapsed_time_percent = elapsed_time * 10 if elapsed_time <= 10 else 100
		bay_1_status.text(f"Time remaining: {10-elapsed_time} seconds")
		my_bar = bay_1_status.progress(elapsed_time_percent)
		# After complete set as available
		if elapsed_time_percent >= 100:
			st.session_state["bay1"].make_available()


	bay_2_status.subheader("Bay 2 status")
	if st.session_state["bay2"].is_available():
		bay_2_status.success("Available")
	else:
		bay_2_status.error(f"In session. In use by group: {st.session_state['bay2'].get_curr_group()}")
		elapsed_time = math.floor((time.time() - st.session_state["bay2"].get_session_start_time()))
		elapsed_time_percent = elapsed_time * 10 if elapsed_time <= 10 else 100
		bay_2_status.text(f"Time remaining: {10-elapsed_time} seconds")
		my_bar = bay_2_status.progress(elapsed_time_percent)
		if elapsed_time_percent == 100:
			st.session_state["bay2"].make_available()

	# Step 2: Display existing waitlist as df for now - can refine later with separate rows maybe? like I did with the other project
	if len(st.session_state["waitlist"].get_curr_waitlist()) > 0:
		st.title("Current waitlist")
		st.table(st.session_state["waitlist"].waitlist_to_dataframe())
		
		# Step 2a: Somehow figure out how to move something to the bay - should be easy enough with agd grid? Maybe display 
		# Move user to available bay
		if st.session_state.bay1.is_available() or st.session_state.bay2.is_available():
			move = st.button("Move group to available bay")
			if move:
				g = st.session_state["waitlist"].remove_first_group()
				st.session_state["waitlist"] = st.session_state["waitlist"]
				if st.session_state["bay1"].is_available():
					st.session_state["bay1"].occupy_bay(g.get_group_name())
				else:
					st.session_state["bay2"].occupy_bay(g.get_group_name())
				st.experimental_rerun()
		else:
			st.button("Move group to available bay", key=None, help=None, on_click=None, args=None, kwargs=None, disabled=True)


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
			group1 = group(group_name, [user1])
			st.session_state["waitlist"].add_group_to_waitlist(group1)
			st.experimental_rerun()

