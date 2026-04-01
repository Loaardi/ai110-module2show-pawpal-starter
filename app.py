import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime

# Check if Owner instance exists in session state before creating a new one
if 'owner' not in st.session_state:
    st.session_state.owner = None  # Placeholder; will be set based on user input

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Create Owner and Pet"):
    if st.session_state.owner is None:
        st.session_state.owner = Owner(name=owner_name, age=30)  # Assuming default age
        pet = Pet(name=pet_name, kind_of_animal=species, owner=st.session_state.owner)
        st.session_state.owner.add_pet(pet)
        st.session_state.pet = pet  # Store the current pet for task addition
        st.success(f"Created owner '{owner_name}' and pet '{pet_name}'!")
    else:
        st.info("Owner and pet already created.")

# Display current pets if owner exists
if st.session_state.owner and st.session_state.owner.pets:
    st.markdown("### Current Pets")
    for pet in st.session_state.owner.pets:
        st.write(f"- {pet.name} ({pet.kind_of_animal})")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if 'pet' in st.session_state and st.session_state.pet:
        # Create Task instance and add to pet using Pet.add_task method
        task = Task(
            description=task_title,
            time=datetime.now(),  # Use current time as placeholder
            frequency="daily",
            pet=st.session_state.pet
        )
        st.session_state.pet.add_task(task)
        st.success(f"Task '{task_title}' added to {st.session_state.pet.name}!")
    else:
        st.error("Please create an owner and pet first.")

# Display tasks from the pet's task list
if 'pet' in st.session_state and st.session_state.pet and st.session_state.pet.tasks:
    st.write("Current tasks for pet:")
    task_data = [
        {"Description": task.description, "Time": task.time.strftime("%H:%M"), "Frequency": task.frequency, "Completed": task.completion_status}
        for task in st.session_state.pet.tasks
    ]
    st.table(task_data)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if st.session_state.owner and st.session_state.owner.pets:
        scheduler = Scheduler(st.session_state.owner)
        # Get today's tasks
        all_tasks = scheduler.get_all_tasks()
        today = datetime.now().date()
        today_tasks = [task for task in all_tasks if task.time.date() == today]
        
        if today_tasks:
            st.write("Today's Schedule:")
            for task in sorted(today_tasks, key=lambda t: t.time):
                st.write(f"- {task.time.strftime('%H:%M')}: {task.description} for {task.pet.name}")
        else:
            st.info("No tasks scheduled for today.")
    else:
        st.warning("Please create an owner and pet first.")
