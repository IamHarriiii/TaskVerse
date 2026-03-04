"""
TaskVerse — Streamlit Frontend
Features: Auth (register/login), task CRUD with tags & subtasks,
charts (Plotly), analytics dashboard, and responsive design.
"""

import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone, date
from typing import List, Dict, Any, Optional
import pandas as pd

# ================= CONFIG ================= #
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="TaskVerse",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================= CUSTOM CSS ================= #
st.markdown("""
<style>
    .stApp { }
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 0.9rem; opacity: 0.8; }
    .tag-chip {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)


# ================= AUTH STATE ================= #
if "token" not in st.session_state:
    st.session_state.token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None


def auth_headers() -> Dict[str, str]:
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


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


def api_get(endpoint: str, params: dict = None) -> Optional[Any]:
    try:
        r = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            headers=auth_headers(),
            timeout=5,
        )
        return r.json() if r.status_code == 200 else None
    except requests.RequestException:
        return None


def api_post(endpoint: str, json_data: dict) -> Optional[requests.Response]:
    try:
        return requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=json_data,
            headers=auth_headers(),
            timeout=5,
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


def api_put(endpoint: str, json_data: dict) -> Optional[requests.Response]:
    try:
        return requests.put(
            f"{API_BASE_URL}{endpoint}",
            json=json_data,
            headers=auth_headers(),
            timeout=5,
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


def api_delete(endpoint: str) -> Optional[requests.Response]:
    try:
        return requests.delete(
            f"{API_BASE_URL}{endpoint}",
            headers=auth_headers(),
            timeout=5,
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


# ================= AUTH PAGES ================= #
def show_auth_page():
    st.title("🧠 TaskVerse")
    st.markdown("##### Cloud-Scale Task Management")
    st.divider()

    auth_tab_login, auth_tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with auth_tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                r = api_post("/auth/login", {"email": email, "password": password})
                if r and r.status_code == 200:
                    token_data = r.json()
                    st.session_state.token = token_data["access_token"]
                    # Fetch current user info
                    me = api_get("/users/me")
                    if me:
                        st.session_state.user_id = me["id"]
                        st.session_state.user_name = me["name"]
                    st.success("Login successful! 🎉")
                    st.rerun()
                elif r:
                    handle_api_error(r)

    with auth_tab_register:
        with st.form("register_form"):
            name = st.text_input("Name", key="reg_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")
            submitted = st.form_submit_button("Register", use_container_width=True)

            if submitted:
                r = api_post(
                    "/auth/register",
                    {"name": name, "email": email, "password": password},
                )
                if r and handle_api_error(r, "Account created! Please login. ✅"):
                    pass


# ================= MAIN APP ================= #
def show_main_app():
    # ── Fetch data ──
    users = api_get("/users") or []
    tasks_response = api_get("/tasks") or {"tasks": [], "total": 0}
    tasks = tasks_response.get("tasks", [])

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name or 'User'}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.rerun()

        st.divider()
        st.header("📊 Quick Stats")

        col1, col2 = st.columns(2)
        col1.metric("Users", len(users))
        col2.metric("Tasks", tasks_response.get("total", len(tasks)))

        if tasks:
            st.divider()
            pending = sum(1 for t in tasks if t["status"] == "pending")
            in_prog = sum(1 for t in tasks if t["status"] == "in_progress")
            done = sum(1 for t in tasks if t["status"] == "done")

            st.markdown(f"⏳ **Pending:** {pending}")
            st.markdown(f"🔄 **In Progress:** {in_prog}")
            st.markdown(f"✅ **Done:** {done}")

            # Collect all tags
            all_tags = set()
            for t in tasks:
                all_tags.update(t.get("tags", []))
            if all_tags:
                st.divider()
                st.subheader("🏷️ Tags")
                tag_html = " ".join(
                    f'<span class="tag-chip">{tag}</span>' for tag in sorted(all_tags)
                )
                st.markdown(tag_html, unsafe_allow_html=True)

    # ── Main tabs ──
    st.title("🧠 TaskVerse")

    tab_tasks, tab_users, tab_analytics = st.tabs(
        ["📋 Tasks", "👤 Users", "📈 Analytics"]
    )

    # ======================================================
    # 📋 TASKS TAB
    # ======================================================
    with tab_tasks:
        # ── Filters ──
        st.subheader("🔍 Filter & Search")
        filter_cols = st.columns(5)
        with filter_cols[0]:
            f_status = st.selectbox(
                "Status", ["All", "pending", "in_progress", "done"], key="f_status"
            )
        with filter_cols[1]:
            f_priority = st.selectbox(
                "Priority", ["All", 1, 2, 3, 4, 5], key="f_priority"
            )
        with filter_cols[2]:
            f_tag = st.text_input("Tag", key="f_tag")
        with filter_cols[3]:
            f_search = st.text_input("Search", key="f_search")
        with filter_cols[4]:
            f_limit = st.number_input("Per page", min_value=5, max_value=200, value=50)

        # Build query params
        params: Dict[str, Any] = {"limit": f_limit}
        if f_status != "All":
            params["status"] = f_status
        if f_priority != "All":
            params["priority"] = f_priority
        if f_tag:
            params["tag"] = f_tag.strip().lower()
        if f_search:
            params["search"] = f_search

        filtered_response = api_get("/tasks", params=params) or {
            "tasks": [],
            "total": 0,
        }
        filtered_tasks = filtered_response.get("tasks", [])

        st.divider()
        st.subheader("➕ Create Task")

        if not users:
            st.warning("Create a user first")
        else:
            with st.form("create_task_form", clear_on_submit=True):
                title = st.text_input("Title")
                description = st.text_area("Description")
                col_a, col_b = st.columns(2)
                with col_a:
                    priority = st.slider("Priority", 1, 5, 3)
                    task_status = st.selectbox(
                        "Status", ["pending", "in_progress", "done"], key="create_status"
                    )
                with col_b:
                    due: date = st.date_input(
                        "Due Date", datetime.now().date() + timedelta(days=1)
                    )
                    tags_input = st.text_input(
                        "Tags (comma-separated)", placeholder="e.g. urgent, backend"
                    )

                # Subtasks
                st.markdown("**Subtasks** (one per line)")
                subtasks_text = st.text_area(
                    "Subtasks", placeholder="Design UI\nWrite tests", label_visibility="collapsed"
                )

                submitted = st.form_submit_button(
                    "➕ Create Task", use_container_width=True
                )

                if submitted:
                    due_dt = datetime.combine(
                        due, datetime.min.time(), tzinfo=timezone.utc
                    )
                    tags = [
                        t.strip().lower()
                        for t in tags_input.split(",")
                        if t.strip()
                    ]
                    subtasks = [
                        {"title": line.strip(), "is_completed": False}
                        for line in subtasks_text.split("\n")
                        if line.strip()
                    ]

                    payload = {
                        "user_id": st.session_state.user_id,
                        "title": title,
                        "description": description or None,
                        "priority": priority,
                        "status": task_status,
                        "due_date": due_dt.isoformat(),
                        "tags": tags,
                        "subtasks": subtasks,
                    }
                    r = api_post("/tasks", payload)
                    if r and handle_api_error(r, "Task created successfully ✅"):
                        st.rerun()

        st.divider()
        st.subheader(f"📋 All Tasks ({filtered_response.get('total', 0)} total)")

        if filtered_tasks:
            for task in filtered_tasks:
                with st.expander(
                    f"{'✅' if task['status'] == 'done' else '🔄' if task['status'] == 'in_progress' else '⏳'} "
                    f"{task['title']}  |  P{task['priority']}  |  "
                    f"{', '.join(task.get('tags', [])) if task.get('tags') else 'no tags'}"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**ID:** `{task['id'][:8]}…`")
                        st.markdown(f"**Status:** {task['status']}")
                        st.markdown(f"**Priority:** {'⭐' * task['priority']}")
                        st.markdown(
                            f"**Due:** {task.get('due_date', 'N/A')[:10]}"
                        )
                    with col2:
                        st.markdown(
                            f"**Description:** {task.get('description') or '_None_'}"
                        )
                        if task.get("tags"):
                            tag_html = " ".join(
                                f'<span class="tag-chip">{t}</span>'
                                for t in task["tags"]
                            )
                            st.markdown(f"**Tags:** {tag_html}", unsafe_allow_html=True)

                    # Subtasks
                    subtasks = task.get("subtasks", [])
                    if subtasks:
                        st.markdown("**Subtasks:**")
                        for st_item in subtasks:
                            check = "✅" if st_item.get("is_completed") else "⬜"
                            st.markdown(f"  {check} {st_item['title']}")

                    # Quick actions
                    act_cols = st.columns(3)
                    with act_cols[0]:
                        new_status = st.selectbox(
                            "Change Status",
                            ["pending", "in_progress", "done"],
                            index=["pending", "in_progress", "done"].index(
                                task["status"]
                            ),
                            key=f"status_{task['id']}",
                        )
                        if new_status != task["status"]:
                            if st.button("💾 Update Status", key=f"upd_{task['id']}"):
                                r = api_put(
                                    f"/tasks/{task['id']}",
                                    {"status": new_status},
                                )
                                if r and handle_api_error(r, "Status updated ✅"):
                                    st.rerun()
                    with act_cols[2]:
                        if st.button("🗑 Delete", key=f"del_{task['id']}"):
                            r = api_delete(f"/tasks/{task['id']}")
                            if r and handle_api_error(r, "Task deleted ✅"):
                                st.rerun()
        else:
            st.info("No tasks found matching your filters")

    # ======================================================
    # 👤 USERS TAB
    # ======================================================
    with tab_users:
        st.subheader("All Users")
        if users:
            df_users = pd.DataFrame(users)[["id", "name", "email", "created_at"]]
            st.dataframe(df_users, use_container_width=True, hide_index=True)
        else:
            st.info("No users found")

    # ======================================================
    # 📈 ANALYTICS TAB
    # ======================================================
    with tab_analytics:
        st.header("📈 Task Analytics")

        if not tasks:
            st.info("No tasks to analyze — create some tasks first!")
        else:
            df = pd.DataFrame(tasks)

            # ── Row 1: KPI Metrics ──
            m1, m2, m3, m4 = st.columns(4)
            total = len(df)
            done_count = len(df[df["status"] == "done"])
            avg_priority = df["priority"].mean()

            # Overdue calculation
            now = datetime.now(timezone.utc)
            overdue = 0
            for _, row in df.iterrows():
                try:
                    due = datetime.fromisoformat(str(row["due_date"]))
                    if due.tzinfo is None:
                        due = due.replace(tzinfo=timezone.utc)
                    if due < now and row["status"] != "done":
                        overdue += 1
                except Exception:
                    pass

            m1.metric("Total Tasks", total)
            m2.metric("Completed", done_count)
            m3.metric("Avg Priority", f"{avg_priority:.1f}")
            m4.metric("⚠️ Overdue", overdue)

            st.divider()

            # ── Row 2: Charts ──
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                # Status Distribution — Donut Chart
                status_counts = df["status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
                fig_status = px.pie(
                    status_counts,
                    names="Status",
                    values="Count",
                    title="Task Status Distribution",
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                fig_status.update_traces(textinfo="percent+label")
                fig_status.update_layout(
                    showlegend=False,
                    margin=dict(t=40, b=20, l=20, r=20),
                    height=350,
                )
                st.plotly_chart(fig_status, use_container_width=True)

            with chart_col2:
                # Priority Distribution — Bar Chart
                priority_counts = (
                    df["priority"]
                    .value_counts()
                    .sort_index()
                    .reset_index()
                )
                priority_counts.columns = ["Priority", "Count"]
                fig_priority = px.bar(
                    priority_counts,
                    x="Priority",
                    y="Count",
                    title="Priority Distribution",
                    color="Priority",
                    color_continuous_scale="Viridis",
                )
                fig_priority.update_layout(
                    showlegend=False,
                    margin=dict(t=40, b=20, l=20, r=20),
                    height=350,
                )
                st.plotly_chart(fig_priority, use_container_width=True)

            st.divider()

            chart_col3, chart_col4 = st.columns(2)

            with chart_col3:
                # Tasks per User — Horizontal Bar
                users_map = {u["id"]: u["name"] for u in users}
                df["user_name"] = df["user_id"].map(users_map).fillna("Unknown")
                user_counts = (
                    df["user_name"].value_counts().reset_index()
                )
                user_counts.columns = ["User", "Tasks"]
                fig_users = px.bar(
                    user_counts,
                    x="Tasks",
                    y="User",
                    orientation="h",
                    title="Tasks per User",
                    color="Tasks",
                    color_continuous_scale="Blues",
                )
                fig_users.update_layout(
                    margin=dict(t=40, b=20, l=20, r=20),
                    height=350,
                    showlegend=False,
                )
                st.plotly_chart(fig_users, use_container_width=True)

            with chart_col4:
                # Tags — Treemap (if tags exist)
                all_tag_list = []
                for _, row in df.iterrows():
                    for tag in row.get("tags", []) or []:
                        all_tag_list.append(tag)

                if all_tag_list:
                    tag_df = (
                        pd.Series(all_tag_list)
                        .value_counts()
                        .reset_index()
                    )
                    tag_df.columns = ["Tag", "Count"]
                    fig_tags = px.treemap(
                        tag_df,
                        path=["Tag"],
                        values="Count",
                        title="Tag Distribution",
                        color="Count",
                        color_continuous_scale="RdYlGn",
                    )
                    fig_tags.update_layout(
                        margin=dict(t=40, b=20, l=20, r=20),
                        height=350,
                    )
                    st.plotly_chart(fig_tags, use_container_width=True)
                else:
                    st.info("No tags found — add tags to your tasks to see the treemap")

            # ── Status × Priority Heatmap ──
            st.divider()
            st.subheader("Status × Priority Heatmap")
            heatmap_data = df.groupby(["status", "priority"]).size().unstack(fill_value=0)
            fig_heat = px.imshow(
                heatmap_data,
                labels=dict(x="Priority", y="Status", color="Tasks"),
                title="Status vs Priority Distribution",
                color_continuous_scale="YlOrRd",
                aspect="auto",
            )
            fig_heat.update_layout(
                margin=dict(t=40, b=20, l=20, r=20),
                height=300,
            )
            st.plotly_chart(fig_heat, use_container_width=True)


# ================= ROUTER ================= #
if st.session_state.token:
    show_main_app()
else:
    show_auth_page()