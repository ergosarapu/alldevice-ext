import streamlit as st
import streamlit_3d as sd
import requests
import json

st.title("🎈 CMMS Extension")

auth = {'username': st.secrets['alldevice']['username'],
        'password': st.secrets['alldevice']['password'],
        'key': st.secrets['alldevice']['key']}

def get_locations():
    response = requests.post("https://demo.alldevicesoft.com/api/devices/locations", json={'auth': auth}).json()['response']
    filtered_locations = [location for location in response if location["object_name"].startswith('EXT:')]
    return filtered_locations

def get_tasks(object_id: str):
    response = requests.post("https://demo.alldevicesoft.com/api/tasks/list", json={'auth': auth, 'object_id': object_id}).json()['response']['data']
    return response

def remove_prefix(value: str):
    return value.replace('EXT:', '')

def set_task(task):
    st.session_state.task = task
    st.session_state.action = 0
    st.session_state.action_step = 0

def has_next_action():
    return st.session_state.action < len(st.session_state.task["actions"]) - 1

def has_prev_action():
    return st.session_state.action > 0

def has_next_step():
    return st.session_state.action_step < len(st.session_state.task["actions"][st.session_state.action]["data"]) - 1

def has_prev_step():
    return st.session_state.action_step > 0

def has_next():
    return has_next_action() or has_next_step()

def has_prev():
    return has_prev_action() or has_prev_step()

def next():
    if has_next_step():
        st.session_state.action_step+=1
        return
    if has_next_action():
        st.session_state.action+=1
        st.session_state.action_step=0

def prev():
    if has_prev_step():
        st.session_state.action_step-=1
        return
    if has_prev_action():
        st.session_state.action-=1
        st.session_state.action_step=len(st.session_state.task["actions"][st.session_state.action]["data"]) - 1
    
if not st.session_state["task"]:
    locations = get_locations()
    for location in locations:
        st.header(remove_prefix(location["object_name"]))
        tasks = get_tasks(location["object_id"])
        for task in tasks:
            with st.container(border=True):
                st.subheader(remove_prefix(task["device_name"]))
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(task["service_name"])
                with col2:
                    st.write(task["service_date"])
                with col3:
                    st.button("Start", on_click=set_task, args=[task])

if st.session_state["task"]:
    st.button("Home", on_click=set_task, args=[None])
    task = st.session_state["task"]

    action = task["actions"][st.session_state.action]
    st.header(remove_prefix(action["action"]))
    action_step = json.loads(action["data"][st.session_state.action_step]["action"])
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button('Prev', on_click=prev, disabled=not has_prev())
        with col2:
            st.subheader(remove_prefix(action_step["action"]))
        with col3:
            st.button('Next', on_click=next, disabled=not has_next())
        
        value = sd.streamlit_3d(model=action_step["model"],height=700,points=action_step["points"])
        st.write(value)
