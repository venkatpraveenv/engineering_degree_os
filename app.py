import streamlit as st
import pandas as pd
import os
from pathlib import Path
from datetime import date, datetime

# ============================================================
# MY ENGINEERING DEGREE OS
# Single-file Streamlit Application
# ============================================================

st.set_page_config(
    page_title="My Engineering Degree OS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "semesters": DATA_DIR / "semesters.csv",
    "courses": DATA_DIR / "courses.csv",
    "university_syllabus": DATA_DIR / "university_syllabus.csv",
    "calendar": DATA_DIR / "calendar.csv",
    "assessments": DATA_DIR / "assessments.csv",
    "scores": DATA_DIR / "scores.csv",
    "plan_checklist": DATA_DIR / "plan_checklist.csv",
}

STATUS_OPTIONS = ["Not Started", "In Progress", "Completed"]

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,0.2);
    }

    .main-title {
        font-size: 30px;
        font-weight: 750;
        margin-bottom: 2px;
    }

    .subtitle {
        color: #888888;
        font-size: 14px;
        margin-bottom: 25px;
    }

    .section-heading {
        font-size: 21px;
        font-weight: 650;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    .semester-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 10px;
        background: rgba(128,128,128,0.035);
    }

    .semester-number {
        font-size: 13px;
        color: #888888;
    }

    .semester-title {
        font-size: 20px;
        font-weight: 700;
        margin: 5px 0;
    }

    .status-completed {
        color: #16a34a;
        font-weight: 600;
    }

    .status-progress {
        color: #d97706;
        font-weight: 600;
    }

    .status-not-started {
        color: #888888;
        font-weight: 600;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.2);
        padding: 14px;
        border-radius: 10px;
    }

    .footer {
        color: #888888;
        text-align: center;
        font-size: 12px;
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CSV FUNCTIONS
# ============================================================

def load_csv(key):
    """Load a CSV file without crashing if it is missing."""

    path = FILES[key]

    if not path.exists():
        return None

    try:
        return pd.read_csv(path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as error:
        st.warning(f"Unable to read {path}: {error}")
        return None


def save_csv(key, dataframe):
    """Save a dataframe to its corresponding CSV file."""

    try:
        dataframe.to_csv(FILES[key], index=False)
        return True
    except (OSError, PermissionError) as error:
        st.error(f"Unable to save {FILES[key]}: {error}")
        return False


def get_data(key):
    """Return loaded data or an empty dataframe."""

    df = load_csv(key)

    if df is None:
        return pd.DataFrame()

    return df


def show_missing_warning(key):
    if not FILES[key].exists():
        st.warning(
            f"Data file `{FILES[key]}` is not available. "
            "Add the CSV file to populate this section."
        )


def safe_column(df, column, default=""):
    if column in df.columns:
        return df[column]
    return pd.Series([default] * len(df), index=df.index)


def count_status(df, status):
    if df.empty or "status" not in df.columns:
        return 0

    return int(
        df["status"].fillna("Not Started").astype(str).str.strip()
        .str.lower().eq(status.lower()).sum()
    )


def get_semester_number(value):
    try:
        return int(str(value).lower().replace("semester", "").strip())
    except (ValueError, TypeError):
        return None


def format_date(value):
    try:
        return pd.to_datetime(value).strftime("%d %b %Y")
    except (ValueError, TypeError):
        return str(value)


# ============================================================
# LOAD DATA
# ============================================================

semesters = get_data("semesters")
courses = get_data("courses")
university_syllabus = get_data("university_syllabus")
calendar = get_data("calendar")
assessments = get_data("assessments")
scores = get_data("scores")
checklist = get_data("plan_checklist")


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown("## 🎓 Degree OS")
st.sidebar.caption("Your engineering academic workspace")

st.sidebar.divider()

pages = [
    "Dashboard",
    "Semesters 1-8",
    "Courses & Syllabus",
    "University Syllabus",
    "Academic / Leave Calendar",
    "Internal Assessments",
    "Status Tracker",
    "Scorecard",
    "Plan & Checklist",
    "Ask Degree AI",
    "Data Admin"
]

selected_page = st.sidebar.radio(
    "MAIN MENU",
    pages,
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.caption("Academic Overview")

current_semester = 1

if not semesters.empty and "status" in semesters.columns:
    in_progress = semesters[
        semesters["status"].astype(str).str.strip().str.lower()
        == "in progress"
    ]

    if not in_progress.empty:
        current_semester = get_semester_number(
            in_progress.iloc[0].get("semester", 1)
        ) or 1

st.sidebar.metric("Current Semester", f"Semester {current_semester}")

st.sidebar.caption("My Engineering Degree OS · v1.0")


# ============================================================
# COMMON PAGE HEADER
# ============================================================

def page_header(title, description):
    st.markdown(f"# {title}")
    st.markdown(
        f'<div class="subtitle">{description}</div>',
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD
# ============================================================

if selected_page == "Dashboard":

    page_header(
        "Dashboard",
        "Your complete engineering degree at a glance."
    )

    # Degree completion

    total_semesters = 8
    completed_semesters = count_status(semesters, "Completed")

    total_credits = 0
    completed_credits = 0

    if not courses.empty and "credits" in courses.columns:
        credit_values = pd.to_numeric(
            courses["credits"], errors="coerce"
        ).fillna(0)

        total_credits = credit_values.sum()

        if "status" in courses.columns:
            completed_mask = (
                courses["status"].fillna("").astype(str).str.lower()
                == "completed"
            )
            completed_credits = credit_values[completed_mask].sum()

    degree_percentage = (
        completed_semesters / total_semesters * 100
    )

    if total_credits > 0:
        degree_percentage = completed_credits / total_credits * 100

    degree_percentage = min(degree_percentage, 100)

    st.markdown("### Degree Progress")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Current Semester", f"{current_semester} / 8")

    col2.metric(
        "Degree Completion",
        f"{degree_percentage:.1f}%"
    )

    col3.metric(
        "Completed Credits",
        f"{completed_credits:g} / {total_credits:g}"
    )

    col4.metric(
        "Completed Semesters",
        f"{completed_semesters} / 8"
    )

    st.progress(degree_percentage / 100)

    st.divider()

    # Semester progress

    st.markdown("### Semester Progress")

    if semesters.empty:
        show_missing_warning("semesters")
    else:

        for _, row in semesters.iterrows():

            semester_name = row.get("semester", "Unknown")
            status = row.get("status", "Not Started")

            st.markdown(
                f"**{semester_name}** · {status}"
            )

            percentage = {
                "Completed": 100,
                "In Progress": 50,
                "Not Started": 0
            }.get(status, 0)

            st.progress(percentage / 100)

    st.divider()

    # Upcoming events

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Next Assessment")

        if not assessments.empty and "date" in assessments.columns:

            temp = assessments.copy()

            temp["_date"] = pd.to_datetime(
                temp["date"], errors="coerce"
            )

            upcoming = temp[
                temp["_date"].notna()
                & (temp["_date"].dt.date >= date.today())
            ].sort_values("_date")

            if not upcoming.empty:

                item = upcoming.iloc[0]

                st.info(
                    f"**{item.get('title', 'Assessment')}**\n\n"
                    f"Date: {format_date(item['date'])}\n\n"
                    f"Type: {item.get('type', 'Not specified')}"
                )
            else:
                st.caption("No upcoming assessments found.")
        else:
            show_missing_warning("assessments")

    with col2:

        st.markdown("### Next Holiday / Leave")

        if not calendar.empty and "date" in calendar.columns:

            temp = calendar.copy()

            temp["_date"] = pd.to_datetime(
                temp["date"], errors="coerce"
            )

            upcoming = temp[
                temp["_date"].notna()
                & (temp["_date"].dt.date >= date.today())
            ].sort_values("_date")

            holiday_rows = upcoming[
                safe_column(upcoming, "category").astype(str).str.lower()
                .str.contains("holiday|leave", na=False)
            ]

            if not holiday_rows.empty:

                item = holiday_rows.iloc[0]

                st.info(
                    f"**{item.get('title', 'Event')}**\n\n"
                    f"Date: {format_date(item['date'])}"
                )
            else:
                st.caption("No upcoming holidays or leave events found.")
        else:
            show_missing_warning("calendar")

    st.divider()

    # Score summary

    st.markdown("### Score Summary")

    if not scores.empty:

        score_col = "obtained_marks"
        maximum_col = "maximum_marks"

        if score_col in scores.columns and maximum_col in scores.columns:

            obtained = pd.to_numeric(
                scores[score_col], errors="coerce"
            ).sum()

            maximum = pd.to_numeric(
                scores[maximum_col], errors="coerce"
            ).sum()

            if maximum > 0:
                st.metric(
                    "Overall Recorded Percentage",
                    f"{obtained / maximum * 100:.2f}%"
                )
            else:
                st.caption("No valid maximum marks recorded.")
        else:
            st.warning(
                "Scores CSV must contain obtained_marks and maximum_marks."
            )
    else:
        show_missing_warning("scores")


# ============================================================
# SEMESTERS 1-8
# ============================================================

elif selected_page == "Semesters 1-8":

    page_header(
        "Semesters 1-8",
        "Explore your eight semesters and track academic progress."
    )

    semester_filter = st.selectbox(
        "Filter Semester",
        ["All Semesters"] + [f"Semester {i}" for i in range(1, 9)]
    )

    if semesters.empty:

        show_missing_warning("semesters")

    else:

        filtered = semesters.copy()

        if semester_filter != "All Semesters":
            filtered = filtered[
                filtered["semester"].astype(str).str.lower()
                == semester_filter.lower()
            ] if "semester" in filtered.columns else pd.DataFrame()

        if filtered.empty:
            st.info("No semester records found for this selection.")

        for _, row in filtered.iterrows():

            semester_name = row.get("semester", "Semester")
            status = row.get("status", "Not Started")

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.subheader(semester_name)

                    st.caption(
                        f"Credits: {row.get('credits', 'Not specified')}"
                    )

                    st.write(
                        row.get("description", "No description available.")
                    )

                with col2:
                    st.write("**Status**")
                    st.write(status)

                if not courses.empty and "semester" in courses.columns:

                    semester_courses = courses[
                        courses["semester"].astype(str).str.lower()
                        == str(semester_name).lower()
                    ]

                    st.caption(
                        f"Courses: {len(semester_courses)}"
                    )


# ============================================================
# COURSES & SYLLABUS
# ============================================================

elif selected_page == "Courses & Syllabus":

    page_header(
        "Courses & Syllabus",
        "Manage subjects, course credits and syllabus topics."
    )

    if courses.empty:

        show_missing_warning("courses")

    else:

        if "semester" in courses.columns:

            available_semesters = sorted(
                courses["semester"].dropna().astype(str).unique()
            )

            selected_semester = st.selectbox(
                "Select Semester",
                ["All"] + available_semesters
            )

            filtered = courses.copy()

            if selected_semester != "All":
                filtered = filtered[
                    filtered["semester"].astype(str) == selected_semester
                ]

        else:
            filtered = courses.copy()

        st.markdown(f"**Total Courses: {len(filtered)}**")

        display_columns = [
            col for col in [
                "course_code",
                "course_title",
                "credits",
                "semester",
                "syllabus_topics",
                "status"
            ]
            if col in filtered.columns
        ]

        st.dataframe(
            filtered[display_columns],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# UNIVERSITY SYLLABUS
# ============================================================

elif selected_page == "University Syllabus":

    page_header(
        "University Syllabus",
        "Programme-level syllabus and official reference information."
    )

    if university_syllabus.empty:

        show_missing_warning("university_syllabus")

    else:

        if "programme_name" in university_syllabus.columns:

            programme_names = university_syllabus[
                "programme_name"
            ].dropna().unique()

            if len(programme_names) > 0:
                st.subheader(str(programme_names[0]))

        if "description" in university_syllabus.columns:
            st.write(university_syllabus.iloc[0]["description"])

        st.markdown("### Programme Syllabus")

        st.dataframe(
            university_syllabus,
            use_container_width=True,
            hide_index=True
        )

        if "source_reference" in university_syllabus.columns:

            st.markdown("### Official References")

            for reference in university_syllabus[
                "source_reference"
            ].dropna():

                if str(reference).strip():
                    st.markdown(f"- {reference}")


# ============================================================
# ACADEMIC / LEAVE CALENDAR
# ============================================================

elif selected_page == "Academic / Leave Calendar":

    page_header(
        "Academic / Leave Calendar",
        "View academic schedules, holidays, examinations and leave."
    )

    if calendar.empty:

        show_missing_warning("calendar")

    else:

        filtered = calendar.copy()

        col1, col2 = st.columns(2)

        with col1:

            if "academic_year" in filtered.columns:

                years = sorted(
                    filtered["academic_year"].dropna().astype(str).unique()
                )

                selected_year = st.selectbox(
                    "Academic Year",
                    ["All"] + years
                )

                if selected_year != "All":
                    filtered = filtered[
                        filtered["academic_year"].astype(str)
                        == selected_year
                    ]

        with col2:

            if "semester" in filtered.columns:

                semester_options = sorted(
                    filtered["semester"].dropna().astype(str).unique()
                )

                selected = st.selectbox(
                    "Semester",
                    ["All"] + semester_options
                )

                if selected != "All":
                    filtered = filtered[
                        filtered["semester"].astype(str) == selected
                    ]

        if "date" in filtered.columns:

            filtered["_sort_date"] = pd.to_datetime(
                filtered["date"], errors="coerce"
            )

            filtered = filtered.sort_values("_sort_date")

        st.dataframe(
            filtered.drop(columns=["_sort_date"], errors="ignore"),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# INTERNAL ASSESSMENTS
# ============================================================

elif selected_page == "Internal Assessments":

    page_header(
        "Internal Assessments",
        "Track IA1, IA2, assignments, laboratory evaluations and exams."
    )

    if assessments.empty:

        show_missing_warning("assessments")

    else:

        filtered = assessments.copy()

        col1, col2 = st.columns(2)

        with col1:

            if "semester" in filtered.columns:

                options = sorted(
                    filtered["semester"].dropna().astype(str).unique()
                )

                selected = st.selectbox(
                    "Semester",
                    ["All"] + options
                )

                if selected != "All":
                    filtered = filtered[
                        filtered["semester"].astype(str) == selected
                    ]

        with col2:

            if "type" in filtered.columns:

                types = sorted(
                    filtered["type"].dropna().astype(str).unique()
                )

                selected_type = st.selectbox(
                    "Assessment Type",
                    ["All"] + types
                )

                if selected_type != "All":
                    filtered = filtered[
                        filtered["type"].astype(str) == selected_type
                    ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# STATUS TRACKER
# ============================================================

elif selected_page == "Status Tracker":

    page_header(
        "Status Tracker",
        "Monitor the completion status of your courses."
    )

    if courses.empty:

        show_missing_warning("courses")

    else:

        if "status" not in courses.columns:

            st.warning("Courses CSV must contain a status column.")

        else:

            total = len(courses)

            completed = count_status(courses, "Completed")
            in_progress = count_status(courses, "In Progress")
            not_started = count_status(courses, "Not Started")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Courses", total)
            col2.metric("Completed", completed)
            col3.metric("In Progress", in_progress)
            col4.metric("Not Started", not_started)

            progress = completed / total if total else 0

            st.markdown("### Overall Course Progress")

            st.progress(progress)

            st.write(f"{progress * 100:.1f}% completed")

            st.divider()

            if "semester" in courses.columns:

                for semester, group in courses.groupby("semester"):

                    done = count_status(group, "Completed")
                    percentage = done / len(group) if len(group) else 0

                    st.markdown(f"**{semester}**")

                    st.progress(percentage)

                    st.caption(
                        f"{done} of {len(group)} courses completed"
                    )

            st.markdown("### Course Status Details")

            st.dataframe(
                courses,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# SCORECARD
# ============================================================

elif selected_page == "Scorecard":

    page_header(
        "Scorecard",
        "Review your academic marks, grades and semester performance."
    )

    if scores.empty:

        show_missing_warning("scores")

    else:

        required = [
            "semester",
            "course_code",
            "obtained_marks",
            "maximum_marks"
        ]

        missing_columns = [
            col for col in required if col not in scores.columns
        ]

        if missing_columns:

            st.warning(
                "Missing required columns: " + ", ".join(missing_columns)
            )

        else:

            score_data = scores.copy()

            score_data["obtained_marks"] = pd.to_numeric(
                score_data["obtained_marks"], errors="coerce"
            )

            score_data["maximum_marks"] = pd.to_numeric(
                score_data["maximum_marks"], errors="coerce"
            )

            valid = score_data[
                score_data["obtained_marks"].notna()
                & score_data["maximum_marks"].notna()
                & (score_data["maximum_marks"] > 0)
            ].copy()

            valid["percentage"] = (
                valid["obtained_marks"]
                / valid["maximum_marks"]
                * 100
            )

            if valid.empty:

                st.info("No valid score records available.")

            else:

                semester_options = sorted(
                    valid["semester"].dropna().astype(str).unique()
                )

                selected = st.selectbox(
                    "Select Semester",
                    ["All"] + semester_options
                )

                filtered = valid.copy()

                if selected != "All":
                    filtered = filtered[
                        filtered["semester"].astype(str) == selected
                    ]

                obtained = filtered["obtained_marks"].sum()
                maximum = filtered["maximum_marks"].sum()

                overall_percentage = (
                    obtained / maximum * 100 if maximum else 0
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Marks Obtained",
                    f"{obtained:g}"
                )

                col2.metric(
                    "Maximum Marks",
                    f"{maximum:g}"
                )

                col3.metric(
                    "Weighted Recorded Percentage",
                    f"{overall_percentage:.2f}%"
                )

                st.divider()

                st.markdown("### Course-wise Performance")

                st.dataframe(
                    filtered,
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("### Grade Distribution")

                if "grade" in filtered.columns:

                    grades = filtered["grade"].dropna().astype(str)

                    if not grades.empty:

                        grade_counts = grades.value_counts()

                        st.bar_chart(grade_counts)

                st.divider()

                st.markdown("### Semester-wise Performance")

                semester_summary = (
                    valid.groupby("semester")
                    .apply(
                        lambda group: (
                            group["obtained_marks"].sum()
                            / group["maximum_marks"].sum()
                            * 100
                            if group["maximum_marks"].sum() > 0
                            else 0
                        ),
                        include_groups=False
                    )
                    .reset_index(name="percentage")
                )

                st.dataframe(
                    semester_summary,
                    use_container_width=True,
                    hide_index=True
                )

                st.bar_chart(
                    semester_summary.set_index("semester")["percentage"]
                )

                st.caption(
                    "Prototype metric: percentages are calculated from "
                    "recorded obtained marks divided by maximum marks. "
                    "This is not a university CGPA calculation. "
                    "University grading and CGPA rules are not assumed."
                )


# ============================================================
# PLAN & CHECKLIST
# ============================================================

elif selected_page == "Plan & Checklist":

    page_header(
        "Plan & Checklist",
        "Organise your academic goals, tasks and deadlines."
    )

    if checklist.empty:

        checklist = pd.DataFrame(
            columns=[
                "id",
                "task",
                "category",
                "target_date",
                "status",
                "notes"
            ]
        )

    # Add new task

    st.markdown("### Add New Task")

    with st.form("add_checklist_form", clear_on_submit=True):

        task = st.text_input("Task Name")

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "Category",
                [
                    "Academic",
                    "Assignment",
                    "Examination",
                    "Project",
                    "Personal",
                    "Other"
                ]
            )

        with col2:
            target_date = st.date_input(
                "Target Date",
                value=None
            )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Add Task",
            use_container_width=True
        )

        if submitted:

            if not task.strip():

                st.error("Please enter a task name.")

            else:

                new_id = (
                    int(pd.to_numeric(
                        checklist.get("id", pd.Series(dtype=float)),
                        errors="coerce"
                    ).max()) + 1
                    if not checklist.empty
                    and pd.to_numeric(
                        checklist.get("id", pd.Series(dtype=float)),
                        errors="coerce"
                    ).notna().any()
                    else 1
                )

                new_task = pd.DataFrame([{
                    "id": new_id,
                    "task": task.strip(),
                    "category": category,
                    "target_date": (
                        target_date.isoformat()
                        if target_date else ""
                    ),
                    "status": "Not Started",
                    "notes": notes
                }])

                checklist = pd.concat(
                    [checklist, new_task],
                    ignore_index=True
                )

                if save_csv("plan_checklist", checklist):
                    st.success("Task added successfully!")
                    st.rerun()

    st.divider()

    # Checklist overview

    st.markdown("### Checklist Overview")

    total = len(checklist)
    completed = count_status(checklist, "Completed")
    pending = count_status(checklist, "Not Started")
    ongoing = count_status(checklist, "In Progress")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tasks", total)
    col2.metric("Completed", completed)
    col3.metric("In Progress", ongoing)
    col4.metric("Pending", pending)

    if total:
        st.progress(completed / total)

    st.divider()

    # Editable checklist

    st.markdown("### Edit Checklist")

    if not checklist.empty:

        edited_checklist = st.data_editor(
            checklist,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "id": st.column_config.NumberColumn(
                    "ID",
                    disabled=True
                ),
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=STATUS_OPTIONS
                ),
                "target_date": st.column_config.DateColumn(
                    "Target Date",
                    format="DD/MM/YYYY"
                )
            },
            key="checklist_editor"
        )

        if st.button("Save Checklist Changes"):

            if save_csv("plan_checklist", edited_checklist):
                st.success("Checklist saved successfully!")
                st.rerun()

        if st.button("Refresh Checklist"):
            st.rerun()

    else:

        st.info("No checklist tasks yet. Add your first task above.")

    st.caption("Checklist data is stored in data/plan_checklist.csv.")


# ============================================================
# ASK DEGREE AI
# ============================================================

elif selected_page == "Ask Degree AI":

    page_header(
        "Ask Degree AI",
        "Ask questions about your engineering degree and academic records."
    )

    st.markdown("### Degree Assistant")

    st.info(
        "Ask about your courses, semesters, credits, assessments, "
        "syllabus and academic progress. Answers are based on available CSV data."
    )

    question = st.text_area(
        "Enter your question",
        placeholder=(
            "Example: How many courses are there in Semester 3?\n"
            "Example: Which courses are completed?\n"
            "Example: What assessments are coming up?"
        ),
        height=110
    )

    def local_answer(query):

        q = query.lower().strip()

        # Semester information

        if "semester" in q and any(
            word in q for word in ["current", "which", "my"]
        ):
            return (
                f"Your current semester is Semester {current_semester}."
            )

        # Course count

        if "course" in q and any(
            word in q for word in ["how many", "count", "total"]
        ):

            if courses.empty:
                return "Course data is unavailable."

            match = None

            for i in range(1, 9):
                if f"semester {i}" in q:
                    match = i
                    break

            if match and "semester" in courses.columns:

                selected_courses = courses[
                    courses["semester"].apply(get_semester_number)
                    == match
                ]

                return (
                    f"Semester {match} has "
                    f"{len(selected_courses)} recorded courses."
                )

            return f"There are {len(courses)} recorded courses."

        # Course names

        if "course" in q and any(
            word in q for word in ["list", "name", "show"]
        ):

            if courses.empty:
                return "Course data is unavailable."

            name_column = (
                "course_title"
                if "course_title" in courses.columns
                else None
            )

            if not name_column:
                return "Course title information is unavailable."

            match = None

            for i in range(1, 9):
                if f"semester {i}" in q:
                    match = i
                    break

            selected_courses = courses.copy()

            if match and "semester" in courses.columns:
                selected_courses = courses[
                    courses["semester"].apply(get_semester_number)
                    == match
                ]

            return (
                "Recorded courses:\n\n"
                + "\n".join(
                    f"- {name}"
                    for name in selected_courses[name_column].dropna()
                )
            )

        # Credits

        if "credit" in q:

            if courses.empty or "credits" not in courses.columns:
                return "Credit information is unavailable."

            credit_values = pd.to_numeric(
                courses["credits"], errors="coerce"
            ).fillna(0)

            if "completed" in q:

                if "status" not in courses.columns:
                    return "Course status information is unavailable."

                completed_mask = (
                    courses["status"].astype(str).str.lower()
                    == "completed"
                )

                result = credit_values[completed_mask].sum()

                return f"Completed credits: {result:g}."

            return f"Total recorded course credits: {credit_values.sum():g}."

        # Completed courses

        if "completed" in q and "course" in q:

            if courses.empty or "status" not in courses.columns:
                return "Course completion information is unavailable."

            completed_courses = courses[
                courses["status"].astype(str).str.lower()
                == "completed"
            ]

            names = completed_courses.get(
                "course_title",
                pd.Series(dtype=str)
            ).dropna().tolist()

            if names:
                return (
                    "Completed courses:\n\n"
                    + "\n".join(f"- {name}" for name in names)
                )

            return f"{len(completed_courses)} completed courses recorded."

        # Assessments

        if "assessment" in q or "exam" in q or "ia1" in q or "ia2" in q:

            if assessments.empty:
                return "Assessment information is unavailable."

            return (
                f"There are {len(assessments)} recorded assessments.\n\n"
                + assessments.to_string(index=False)
            )

        # Syllabus

        if "syllabus" in q:

            if university_syllabus.empty and courses.empty:
                return "Syllabus information is unavailable."

            if "topic" in q and not courses.empty:
                if "syllabus_topics" in courses.columns:
                    return (
                        "Available syllabus topics:\n\n"
                        + "\n".join(
                            f"- {topic}"
                            for topic in courses["syllabus_topics"].dropna()
                        )
                    )

            return (
                "Programme syllabus information is available in the "
                "University Syllabus section."
            )

        # Calendar

        if any(
            word in q for word in ["holiday", "leave", "calendar"]
        ):

            if calendar.empty:
                return "Calendar information is unavailable."

            return (
                f"There are {len(calendar)} recorded calendar events.\n\n"
                + calendar.to_string(index=False)
            )

        # Scores

        if any(
            word in q for word in ["score", "mark", "percentage", "grade"]
        ):

            if scores.empty:
                return "Score information is unavailable."

            if (
                "obtained_marks" in scores.columns
                and "maximum_marks" in scores.columns
            ):

                obtained = pd.to_numeric(
                    scores["obtained_marks"], errors="coerce"
                ).sum()

                maximum = pd.to_numeric(
                    scores["maximum_marks"], errors="coerce"
                ).sum()

                if maximum > 0:
                    return (
                        f"Recorded marks: {obtained:g}/{maximum:g}\n"
                        f"Prototype percentage: "
                        f"{obtained / maximum * 100:.2f}%"
                    )

            return "Score records are available in the Scorecard section."

        # Degree progress

        if any(
            word in q for word in ["progress", "completion", "degree"]
        ):

            return (
                f"Completed semesters: {completed_semesters}/8.\n"
                f"Degree completion: {degree_percentage:.1f}%.\n"
                f"Completed credits: {completed_credits:g}."
            )

        return None

    if st.button("Ask Question", type="primary"):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            answer = local_answer(question)

            st.markdown("### Answer")

            if answer is not None:

                st.success(answer)

                st.caption("Source: Locally loaded CSV data.")

            else:

                if os.getenv("GEMINI_API_KEY"):

                    st.warning(
                        "Gemini API key detected, but generative API "
                        "integration has not been implemented in this version."
                    )

                else:

                    st.warning(
                        "AI API not connected. This question requires "
                        "generative AI and cannot be answered by the "
                        "local CSV-based assistant."
                    )

    st.divider()

    st.markdown("### Example Questions")

    examples = [
        "How many courses are there?",
        "Which courses are completed?",
        "How many credits have I completed?",
        "What assessments are coming up?",
        "Show my degree progress.",
        "What is my recorded percentage?"
    ]

    for example in examples:

        if st.button(example, key=f"example_{example}"):

            st.session_state["example_question"] = example
            st.rerun()

    if "example_question" in st.session_state:

        st.info(
            f"Selected question: {st.session_state['example_question']}"
        )


# ============================================================
# DATA ADMIN
# ============================================================

elif selected_page == "Data Admin":

    page_header(
        "Data Admin",
        "View, edit and save the CSV files used by your application."
    )

    st.info(
        "Changes made here directly update the corresponding CSV files "
        "inside the data folder."
    )

    for key, path in FILES.items():

        with st.expander(
            f"📁 {key.replace('_', ' ').title()} — {path.name}",
            expanded=False
        ):

            df = load_csv(key)

            if df is None:

                st.warning(
                    f"{path.name} does not exist. "
                    "Create this CSV file with the required columns "
                    "to start managing its data."
                )

            else:

                st.caption(
                    f"Rows: {len(df)} | Columns: {len(df.columns)}"
                )

                edited_df = st.data_editor(
                    df,
                    use_container_width=True,
                    num_rows="dynamic",
                    key=f"editor_{key}"
                )

                if st.button(
                    f"Save {path.name}",
                    key=f"save_{key}"
                ):

                    if save_csv(key, edited_df):
                        st.success(f"{path.name} updated successfully!")
                        st.rerun()

    st.divider()

    st.markdown("### Data Folder")

    st.code(str(DATA_DIR.resolve()), language="text")

    st.caption(
        "All academic records are maintained locally in CSV format."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        My Engineering Degree OS · Academic Management System
        <br>
        Built with Python, Streamlit and Pandas
    </div>
    """,
    unsafe_allow_html=True
)