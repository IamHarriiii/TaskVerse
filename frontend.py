import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional # type: ignore
import pandas as pd

# ---------------- CONFIG ---------------- #
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="User Task Manager",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- HELPERS ---------------- #

def handle_api_error(response: requests.Response, success_message: str = "") -> bool:
    """
    Handle API response and show appropriate messages.
    
    Args:
        response: The response object from requests
        success_message: Message to show on success
        
    Returns:
        True if successful, False otherwise
    """
    if response.status_code in [200, 201]:
        if success_message:
            st.success(success_message)
        return True
    else:
        try:
            error_detail = response.json().get("detail", "Unknown error occurred")
        except Exception:
            error_detail = f"Error: {response.status_code}"
        st.error(f"❌ {error_detail}")
        return False


def get_users() -> List[Dict[str, Any]]:
    """Fetch all users from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/users", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to API: {e}")
        return []


def get_tasks() -> List[Dict[str, Any]]:
    """Fetch all tasks from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/tasks", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to API: {e}")
        return []


def delete_user(user_id: str) -> bool:
    """Delete a user by ID."""
    try:
        response = requests.delete(f"{API_BASE_URL}/users/{user_id}", timeout=5)
        return handle_api_error(response, "User deleted successfully ✅")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to delete user: {e}")
        return False


def delete_task(task_id: str) -> bool:
    """Delete a task by ID."""
    try:
        response = requests.delete(f"{API_BASE_URL}/tasks/{task_id}", timeout=5)
        return handle_api_error(response, "Task deleted successfully ✅")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to delete task: {e}")
        return False


def update_task_status(task_id: str, new_status: str) -> bool:
    """Update a task's status."""
    try:
        payload = {"status": new_status}
        response = requests.put(
            f"{API_BASE_URL}/tasks/{task_id}",
            json=payload,
            timeout=5
        )
        return handle_api_error(response, f"Task status updated to '{new_status}' ✅")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to update task: {e}")
        return False


# ---------------- UI ---------------- #

# Sidebar for stats
with st.sidebar:
    st.header("📊 Statistics")
    users = get_users()
    tasks = get_tasks()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Users", len(users))
    with col2:
        st.metric("Total Tasks", len(tasks))
    
    if tasks:
        pending = sum(1 for t in tasks if t["status"] == "pending")
        in_progress = sum(1 for t in tasks if t["status"] == "in_progress")
        done = sum(1 for t in tasks if t["status"] == "done")
        
        st.divider()
        st.subheader("Task Status")
        st.write(f"⏳ Pending: {pending}")
        st.write(f"🔄 In Progress: {in_progress}")
        st.write(f"✅ Done: {done}")


st.title("🧠 User Task Management System")

tab_users, tab_tasks, tab_analytics = st.tabs(["👤 Users", "📋 Tasks", "📈 Analytics"])

# =========================================================
# 👤 USERS TAB
# =========================================================
with tab_users:
    st.header("Create User")
    
    with st.form("create_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", placeholder="John Doe")
        with col2:
            email = st.text_input("Email", placeholder="john@example.com")
        
        submitted = st.form_submit_button("➕ Create User", use_container_width=True)
        
        if submitted:
            if not name or not email:
                st.error("Please fill in all fields")
            else:
                payload = {"name": name, "email": email}
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/users",
                        json=payload,
                        timeout=5
                    )
                    if handle_api_error(response, "User created successfully ✅"):
                        st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to create user: {e}")

    st.divider()
    st.subheader("All Users")
    
    users = get_users()
    if users:
        # Create DataFrame for better display
        df_users = pd.DataFrame(users)
        df_users = df_users[["id", "name", "email", "created_at"]]
        
        # Display table
        st.dataframe(
            df_users,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "email": st.column_config.TextColumn("Email", width="medium"),
                "created_at": st.column_config.DatetimeColumn(
                    "Created At",
                    format="DD/MM/YYYY HH:mm",
                    width="medium"
                ),
            }
        )
        
        # Delete user section
        st.divider()
        with st.expander("🗑️ Delete User"):
            user_to_delete = st.selectbox(
                "Select user to delete",
                options=[u["id"] for u in users],
                format_func=lambda x: next(
                    (f"{u['name']} ({u['email']})" for u in users if u["id"] == x),
                    x
                ),
                key="delete_user_select"
            )
            if st.button("Delete User", type="primary", key="delete_user_btn"):
                if delete_user(user_to_delete):
                    st.rerun()
    else:
        st.info("No users found. Create your first user above!")

# =========================================================
# 📋 TASKS TAB
# =========================================================
with tab_tasks:
    st.header("Create Task")
    
    users = get_users()
    
    if not users:
        st.warning("⚠️ Create a user before adding tasks.")
    else:
        user_map = {f"{u['name']} ({u['email']})": u["id"] for u in users}
        
        with st.form("create_task_form", clear_on_submit=True):
            selected_user = st.selectbox("Assign to User", list(user_map.keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Task Title", placeholder="Complete project report")
            with col2:
                status = st.selectbox("Status", ["pending", "in_progress", "done"])
            
            description = st.text_area(
                "Description",
                placeholder="Detailed description of the task...",
                height=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                priority = st.slider("Priority", 1, 5, 3, help="1 = Highest, 5 = Lowest")
            with col2:
                due_date = st.date_input(
                    "Due Date",
                    value=datetime.now(timezone.utc).date() + timedelta(days=1),
                    min_value=datetime.now(timezone.utc).date()
                )
            
            submitted = st.form_submit_button("➕ Create Task", use_container_width=True)
            
            if submitted:
                if not title:
                    st.error("Task title is required")
                else:
                    # Convert date to datetime with timezone
                    due_datetime = datetime.combine(
                        due_date,
                        datetime.min.time()
                    ).replace(tzinfo=timezone.utc)
                    
                    payload = {
                        "user_id": user_map[selected_user],
                        "title": title,
                        "description": description if description else None,
                        "priority": priority,
                        "status": status,
                        "due_date": due_datetime.isoformat()
                    }
                    
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/tasks",
                            json=payload,
                            timeout=5
                        )
                        if handle_api_error(response, "Task created successfully ✅"):
                            st.rerun()
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to create task: {e}")

    st.divider()
    st.subheader("All Tasks")
    
    tasks = get_tasks()
    if tasks:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                ["pending", "in_progress", "done"],
                default=["pending", "in_progress", "done"]
            )
        with col2:
            priority_filter = st.multiselect(
                "Filter by Priority",
                [1, 2, 3, 4, 5],
                default=[1, 2, 3, 4, 5]
            )
        with col3:
            if users:
                user_filter = st.multiselect(
                    "Filter by User",
                    [u["id"] for u in users],
                    format_func=lambda x: next(
                        (f"{u['name']}" for u in users if u["id"] == x),
                        x
                    ),
                    default=[u["id"] for u in users]
                )
            else:
                user_filter = []
        
        # Apply filters
        filtered_tasks = [
            t for t in tasks
            if t["status"] in status_filter
            and t["priority"] in priority_filter
            and t["user_id"] in user_filter
        ]
        
        if filtered_tasks:
            # Create DataFrame
            df_tasks = pd.DataFrame(filtered_tasks)
            
            # Reorder columns
            column_order = ["title", "status", "priority", "due_date", "user_id", "created_at", "id"]
            df_tasks = df_tasks[[col for col in column_order if col in df_tasks.columns]]
            
            st.dataframe(
                df_tasks,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.TextColumn("ID", width="small"),
                    "title": st.column_config.TextColumn("Title", width="large"),
                    "status": st.column_config.TextColumn("Status", width="small"),
                    "priority": st.column_config.NumberColumn("Priority", width="small"),
                    "due_date": st.column_config.DatetimeColumn(
                        "Due Date",
                        format="DD/MM/YYYY",
                        width="medium"
                    ),
                    "user_id": st.column_config.TextColumn("User ID", width="small"),
                    "created_at": st.column_config.DatetimeColumn(
                        "Created",
                        format="DD/MM/YYYY",
                        width="medium"
                    ),
                }
            )
            
            # Task actions
            st.divider()
            with st.expander("⚙️ Task Actions"):
                task_map = {f"{t['title']} (ID: {t['id'][:8]}...)": t["id"] for t in filtered_tasks}
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Update Status")
                    task_to_update = st.selectbox(
                        "Select task",
                        options=list(task_map.keys()),
                        key="update_task_select"
                    )
                    new_status = st.selectbox(
                        "New status",
                        ["pending", "in_progress", "done"],
                        key="new_status_select"
                    )
                    if st.button("Update Status", key="update_status_btn"):
                        if update_task_status(task_map[task_to_update], new_status):
                            st.rerun()
                
                with col2:
                    st.subheader("Delete Task")
                    task_to_delete = st.selectbox(
                        "Select task",
                        options=list(task_map.keys()),
                        key="delete_task_select"
                    )
                    if st.button("Delete Task", type="primary", key="delete_task_btn"):
                        if delete_task(task_map[task_to_delete]):
                            st.rerun()
        else:
            st.info("No tasks match the current filters")
    else:
        st.info("No tasks found. Create your first task above!")

# =========================================================
# 📈 ANALYTICS TAB
# =========================================================
with tab_analytics:
    st.header("Task Analytics")
    
    tasks = get_tasks()
    users = get_users()
    
    if not tasks:
        st.info("No tasks available for analytics")
    else:
        # Status distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Status Distribution")
            status_counts = {}
            for task in tasks:
                status = task["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            status_df = pd.DataFrame(
                list(status_counts.items()),
                columns=["Status", "Count"]
            )
            st.bar_chart(status_df.set_index("Status"))
        
        with col2:
            st.subheader("Priority Distribution")
            priority_counts = {}
            for task in tasks:
                priority = task["priority"]
                priority_counts[f"Priority {priority}"] = priority_counts.get(f"Priority {priority}", 0) + 1
            
            priority_df = pd.DataFrame(
                list(priority_counts.items()),
                columns=["Priority", "Count"]
            )
            st.bar_chart(priority_df.set_index("Priority"))
        
        # Tasks per user
        st.divider()
        st.subheader("Tasks per User")
        
        user_task_counts = {}
        for task in tasks:
            user_id = task["user_id"]
            user_name = next((u["name"] for u in users if u["id"] == user_id), "Unknown")
            user_task_counts[user_name] = user_task_counts.get(user_name, 0) + 1
        
        if user_task_counts:
            user_df = pd.DataFrame(
                list(user_task_counts.items()),
                columns=["User", "Tasks"]
            )
            st.bar_chart(user_df.set_index("User"))
        
        # Upcoming deadlines
        st.divider()
        st.subheader("⏰ Upcoming Deadlines")
        
        now = datetime.now(timezone.utc)
        upcoming_tasks = []
        
        for task in tasks:
            if task["status"] != "done":
                due_date = datetime.fromisoformat(task["due_date"])
                days_until_due = (due_date - now).days
                
                if days_until_due <= 7:  # Show tasks due in next 7 days
                    upcoming_tasks.append({
                        "Title": task["title"],
                        "Due Date": due_date.strftime("%Y-%m-%d"),
                        "Days Until Due": days_until_due,
                        "Priority": task["priority"],
                        "Status": task["status"]
                    })
        
        if upcoming_tasks:
            df_upcoming = pd.DataFrame(upcoming_tasks)
            df_upcoming = df_upcoming.sort_values("Days Until Due")
            st.dataframe(df_upcoming, use_container_width=True, hide_index=True)
        else:
            st.info("No tasks due in the next 7 days")