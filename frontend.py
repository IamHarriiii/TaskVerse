import streamlit as st
import requests
from datetime import datetime, timedelta, timezone, date
from typing import List, Dict, Any
import pandas as pd

# ================= CONFIG ================= #
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="User Task Manager",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================= HELPERS ================= #

def handle_api_error(response: requests.Response, success_message: str = "") -> bool:
    if response.status_code in (200, 201):
        if success_message:
            st.success(success_message)
        return True

    try:
        error_detail = response.json().get("detail", "Unknown error")
    except Exception:
        error_detail = f"HTTP {response.status_code}"

    st.error(f"❌ {error_detail}")
    return False


@st.cache_data(show_spinner=False)
def get_users() -> List[Dict[str, Any]]:
    try:
        r = requests.get(f"{API_BASE_URL}/users", timeout=5)
        return r.json() if r.status_code == 200 else []
    except requests.RequestException:
        return []


@st.cache_data(show_spinner=False)
def get_tasks() -> List[Dict[str, Any]]:
    try:
        r = requests.get(f"{API_BASE_URL}/tasks", timeout=5)
        return r.json() if r.status_code == 200 else []
    except requests.RequestException:
        return []


def delete_user(user_id: str) -> bool:
    try:
        r = requests.delete(f"{API_BASE_URL}/users/{user_id}", timeout=5)
        return handle_api_error(r, "User deleted successfully ✅")
    except requests.RequestException as e:
        st.error(str(e))
        return False


def delete_task(task_id: str) -> bool:
    try:
        r = requests.delete(f"{API_BASE_URL}/tasks/{task_id}", timeout=5)
        return handle_api_error(r, "Task deleted successfully ✅")
    except requests.RequestException as e:
        st.error(str(e))
        return False


def update_task(task_id: str, updates: Dict[str, Any]) -> bool:
    try:
        r = requests.put(
            f"{API_BASE_URL}/tasks/{task_id}",
            json=updates,
            timeout=5,
        )
        return handle_api_error(r, "Task updated successfully ✅")
    except requests.RequestException as e:
        st.error(str(e))
        return False


# ================= SIDEBAR ================= #

with st.sidebar:
    st.header("📊 Statistics")

    users = get_users()
    tasks = get_tasks()

    col1, col2 = st.columns(2)
    col1.metric("Users", len(users))
    col2.metric("Tasks", len(tasks))

    if tasks:
        st.divider()
        st.subheader("Task Status")

        st.write("⏳ Pending:", sum(t["status"] == "pending" for t in tasks))
        st.write("🔄 In Progress:", sum(t["status"] == "in_progress" for t in tasks))
        st.write("✅ Done:", sum(t["status"] == "done" for t in tasks))


# ================= MAIN UI ================= #

st.title("🧠 User Task Management System")

tab_users, tab_tasks, tab_analytics = st.tabs(
    ["👤 Users", "📋 Tasks", "📈 Analytics"]
)

# ======================================================
# 👤 USERS TAB
# ======================================================
with tab_users:
    st.header("Create User")

    with st.form("create_user_form", clear_on_submit=True):
        name = st.text_input("Name")
        email = st.text_input("Email")
        submitted = st.form_submit_button(
            "➕ Create User",
            use_container_width=True,
        )

        if submitted:
            payload: Dict[str, str] = {"name": name, "email": email}
            r = requests.post(
                f"{API_BASE_URL}/users",
                json=payload,
                timeout=5,
            )
            if handle_api_error(r, "User created successfully ✅"):
                st.cache_data.clear()
                st.rerun()

    st.divider()
    st.subheader("All Users")

    if users:
        df_users = pd.DataFrame(users)[
            ["id", "name", "email", "created_at"]
        ]
        st.dataframe(df_users, use_container_width=True, hide_index=True)

        st.divider()
        user_map = {
            f"{u['name']} ({u['email']})": u["id"]
            for u in users
        }
        selected_user = st.selectbox(
            "Delete User",
            user_map.keys(),
        )
        if st.button("🗑 Delete User"):
            if delete_user(user_map[selected_user]):
                st.cache_data.clear()
                st.rerun()
    else:
        st.info("No users found")

# ======================================================
# 📋 TASKS TAB
# ======================================================
with tab_tasks:
    st.header("Create Task")

    if not users:
        st.warning("Create a user first")
    else:
        user_map = {
            f"{u['name']} ({u['email']})": u["id"]
            for u in users
        }

        with st.form("create_task_form", clear_on_submit=True):
            user_label = st.selectbox(
                "Assign to User",
                user_map.keys(),
            )
            title = st.text_input("Title")
            description = st.text_area("Description")
            priority = st.slider("Priority", 1, 5, 3)
            status = st.selectbox(
                "Status",
                ["pending", "in_progress", "done"],
            )
            due: date = st.date_input(
                "Due Date",
                datetime.now().date() + timedelta(days=1),
            )

            submitted = st.form_submit_button(
                "➕ Create Task",
                use_container_width=True,
            )

            if submitted:
                due_dt = datetime.combine(
                    due,
                    datetime.min.time(),
                    tzinfo=timezone.utc,
                )

                payload: Dict[str, Any] = {
                    "user_id": user_map[user_label],
                    "title": title,
                    "description": description or None,
                    "priority": priority,
                    "status": status,
                    "due_date": due_dt.isoformat(),
                }

                r = requests.post(
                    f"{API_BASE_URL}/tasks",
                    json=payload,
                    timeout=5,
                )
                if handle_api_error(r, "Task created successfully ✅"):
                    st.cache_data.clear()
                    st.rerun()

    st.divider()
    st.subheader("All Tasks")

    if tasks:
        df_tasks = pd.DataFrame(tasks)
        st.dataframe(df_tasks, use_container_width=True, hide_index=True)

        st.divider()
        task_map = {
            f"{t['title']} ({t['id'][:8]}…)": t["id"]
            for t in tasks
        }

        col1, col2 = st.columns(2)

        with col1:
            task_label = st.selectbox(
                "Update Task",
                task_map.keys(),
                key="update_task_select"
            )
            selected_task_id = task_map[task_label]
            selected_task = next(t for t in tasks if t["id"] == selected_task_id)

            with st.expander("Edit Task Details", expanded=True):
                new_title = st.text_input("New Title", value=selected_task["title"])
                new_desc = st.text_area("New Description", value=selected_task["description"] or "")
                new_status = st.selectbox(
                    "New Status",
                    ["pending", "in_progress", "done"],
                    index=["pending", "in_progress", "done"].index(selected_task["status"])
                )
                new_priority = st.slider("New Priority", 1, 5, value=selected_task["priority"])
                
                if st.button("Save Changes", use_container_width=True):
                    updates = {}
                    if new_title != selected_task["title"]:
                        updates["title"] = new_title
                    if new_desc != (selected_task["description"] or ""):
                        updates["description"] = new_desc if new_desc.strip() else None
                    if new_status != selected_task["status"]:
                        updates["status"] = new_status
                    if new_priority != selected_task["priority"]:
                        updates["priority"] = new_priority
                    
                    if updates:
                        if update_task(selected_task_id, updates):
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.info("No changes detected")

        with col2:
            del_task = st.selectbox(
                "Delete Task",
                task_map.keys(),
            )
            if st.button("Delete Task"):
                if delete_task(task_map[del_task]):
                    st.cache_data.clear()
                    st.rerun()
    else:
        st.info("No tasks found")

# ======================================================
# 📈 ANALYTICS TAB (PYTHON 3.14 SAFE – NO CHARTS)
# ======================================================
with tab_analytics:
    st.header("Task Analytics")

    if not tasks:
        st.info("No tasks to analyze")
    else:
        # ---- Status Summary ----
        st.subheader("Status Summary")
        status_summary = (
            pd.DataFrame(tasks)["status"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Status", "status": "Count"})
        )
        st.dataframe(status_summary, use_container_width=True, hide_index=True)

        # ---- Priority Summary ----
        st.subheader("Priority Summary")
        priority_summary = (
            pd.DataFrame(tasks)["priority"]
            .value_counts()
            .sort_index()
            .reset_index()
            .rename(columns={"index": "Priority", "priority": "Count"})
        )
        st.dataframe(priority_summary, use_container_width=True, hide_index=True)

        # ---- Tasks per User ----
        st.subheader("Tasks per User")
        users_map = {u["id"]: u["name"] for u in users}

        df_tasks = pd.DataFrame(tasks)
        df_tasks["user_name"] = df_tasks["user_id"].map(users_map)

        tasks_per_user = (
            df_tasks["user_name"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "User", "user_name": "Tasks"})
        )

        st.dataframe(tasks_per_user, use_container_width=True, hide_index=True)