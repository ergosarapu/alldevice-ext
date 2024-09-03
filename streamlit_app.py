import streamlit as st
import streamlit_3d as sd
import requests
import json

st.title("📋 Maintenance tasks")

auth = {'username': st.secrets['alldevice']['username'],
        'password': st.secrets['alldevice']['password'],
        'key': st.secrets['alldevice']['key']}

def get_locations():
    response = requests.post("https://demo.alldevicesoft.com/api/devices/locations", json={'auth': auth}).json()['response']
    filtered_locations = [location for location in response if location["object_name"].startswith('Saekaater')]
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

def in_task():
    return hasattr(st.session_state, "task") and st.session_state["task"] is not None

if not in_task():
    locations = get_locations()
    for location in locations:
        st.header(location["object_name"])
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
                    st.button("Begin service", on_click=set_task, args=[task], key=task["task_id"])
    st.divider()
    st.subheader('What is this and how this prototype works?')
    st.markdown('''
    The goal of creating this proof of concept was to quickly demo a way to define machinery maintenance tasks together with 3D models. An existing [AllDevice](https://www.alldevicesoft.com/) CMMS was used as a data source.
    
    List of service tasks are loaded from https://demo.alldevicesoft.com/ instance. To get personalised access to demo instance, contact AllDevice customer support.
    
    Only location named 'Saekaater' is currently loaded, other service tasks are ignored. Service task's action steps/activities contents defined in CMMS are expected to be encoded in JSON as follows, so the interactive 3D model with annotations can be rendered. Only glTF models are supported.''')
    st.json('{"action": "Määri laagrid","model":"https://alteirac.com/models/helmet/scene.gltf","points":[{"description": "Laagri asukoht", "data-position":{"x":0.4595949207254826,"y":0.40998085773554555,"z":0.33846317660071373},"data-normal":{"x":-0.18705895743345607,"y":-0.3420641705224677,"z":0.9208697246020658}}]}')

if in_task():
    st.button("Home", on_click=set_task, args=[None])
    task = st.session_state["task"]

    action = task["actions"][st.session_state.action]
    if "data" not in action:
        st.header("No steps available for task")
        exit()
    st.header(remove_prefix(action["action"]))
    action_step = json.loads(action["data"][st.session_state.action_step]["action"])
    #st.header("action_step: " + json.dumps(action_step))
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button('Prev', on_click=prev, disabled=not has_prev())
        with col2:
            st.subheader(remove_prefix(action_step["action"]))
        with col3:
            st.button('Next', on_click=next, disabled=not has_next())
        
        value = sd.streamlit_3d(model=action_step["model"],height=700,points=action_step["points"])
        st.write(value)
