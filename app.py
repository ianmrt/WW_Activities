import pandas as pd
import streamlit as st
import plotly.express as px
import re

st.set_page_config(
    page_title="Adventurous Activities Dashboard",
    layout="wide"
)


@st.cache_data(ttl=300)
def load_data():

# --------------------------------------------------
# Read Excel
# --------------------------------------------------

df = pd.read_excel("data.xlsx")

# --------------------------------------------------
# Normalise Activity Names
# --------------------------------------------------

df["Activity"] = (
    df["Activity"]
    .fillna("")
    .astype(str)
    .str.replace(";", "", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    .str.title()
)

# --------------------------------------------------
# Normalise Group Names
# --------------------------------------------------

def normalise_group(group):

    if pd.isna(group):
        return "Unknown"

    group = str(group)

    # Replace semicolons with spaces
    group = group.replace(";", " ")

    # Remove duplicate spaces
    group = re.sub(r"\s+", " ", group).strip()

    words = []

    for word in group.split():

        match = re.match(
            r"^(\d+)(st|nd|rd|th)$",
            word.lower()
        )

        if match:
            words.append(
                match.group(1) + match.group(2)
            )
        else:
            words.append(word.capitalize())

    return " ".join(words)

df["Group"] = df["Group"].apply(normalise_group)

# --------------------------------------------------
# Approval Status
# --------------------------------------------------

def approval_status(value):

    if pd.isna(value) or str(value).strip() == "":
        return "Awaiting Approval"

    value = str(value).strip().lower()

    if value in ["yes", "approved", "y"]:
        return "Approved"

    if value in ["no", "rejected", "n"]:
        return "Not Approved"

    return str(value)

df["Approval Status"] = df["Approved "].apply(
    approval_status
)

# --------------------------------------------------
# Event Date
# --------------------------------------------------

try:
    df["Event Date"] = pd.to_datetime(
        df["Date of Event (start date)"],
        errors="coerce"
    )
except Exception:
    df["Event Date"] = pd.NaT

# --------------------------------------------------
# Filter to 2024 onwards
# --------------------------------------------------

df = df[
    df["Event Date"].notna()
    & (df["Event Date"] >= pd.Timestamp("2024-01-01"))
]

return df



# --------------------------------------------------
# Filter to 2024 onwards
# --------------------------------------------------

if "Event Date" in df.columns:
    df = df[
        df["Event Date"].notna()
        & (df["Event Date"] >= pd.Timestamp("2024-01-01"))
    ]

    df = pd.read_excel("data.xlsx")

    # --------------------------------------------------
    # Normalise Activity Names
    # --------------------------------------------------

    df["Activity"] = (
        df["Activity"]
        .fillna("")
        .astype(str)
        .str.replace(";", "", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.title()
    )

    # --------------------------------------------------
    # Normalise Group Names
    # --------------------------------------------------

    def normalise_group(group):

        if pd.isna(group):
            return "Unknown"

        group = str(group)

        # Replace semicolons with spaces
        group = group.replace(";", " ")

        # Remove duplicate spaces
        group = re.sub(r"\s+", " ", group).strip()

        words = []

        for word in group.split():

            match = re.match(
                r"^(\d+)(st|nd|rd|th)$",
                word.lower()
            )

            if match:
                words.append(
                    match.group(1) + match.group(2)
                )
            else:
                words.append(word.capitalize())

        return " ".join(words)

    df["Group"] = df["Group"].apply(normalise_group)

    # --------------------------------------------------
    # Approval Status
    # --------------------------------------------------

    def approval_status(value):

        if pd.isna(value) or str(value).strip() == "":
            return "Awaiting Approval"

        value = str(value).strip().lower()

        if value in ["yes", "approved", "y"]:
            return "Approved"

        if value in ["no", "rejected", "n"]:
            return "Not Approved"

        return str(value)

    df["Approval Status"] = df["Approved "].apply(
        approval_status
    )

    # --------------------------------------------------
    # Event Date
    # --------------------------------------------------

    try:
        df["Event Date"] = pd.to_datetime(
            df["Date of Event (start date)"],
            errors="coerce"
        )

    except Exception:
        df["Event Date"] = pd.NaT

    return df


# ======================================================
# Load Data
# ======================================================

df = load_data()

st.title("Adventurous Activities Approval Dashboard")

# ======================================================
# Filters
# ======================================================

groups = sorted(df["Group"].dropna().unique())
activities = sorted(df["Activity"].dropna().unique())

col1, col2 = st.columns(2)

selected_groups = col1.multiselect(
    "Group",
    groups
)

selected_activities = col2.multiselect(
    "Activity",
    activities
)

filtered = df.copy()

if selected_groups:
    filtered = filtered[
        filtered["Group"].isin(selected_groups)
    ]

if selected_activities:
    filtered = filtered[
        filtered["Activity"].isin(selected_activities)
    ]

# ======================================================
# KPI Cards
# ======================================================

total = len(filtered)

approved = (
    filtered["Approval Status"] == "Approved"
).sum()

awaiting = (
    filtered["Approval Status"] == "Awaiting Approval"
).sum()

not_approved = (
    filtered["Approval Status"] == "Not Approved"
).sum()

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Activities", total)
k2.metric("Approved", approved)
k3.metric("Awaiting Approval", awaiting)
k4.metric("Not Approved", not_approved)

st.divider()

# ======================================================
# Charts
# ======================================================

left, right = st.columns(2)

with left:

    grp = (
        filtered.groupby("Group")
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=True)
    )

    st.subheader("Activities by Group")

    fig = px.bar(
        grp,
        x="Count",
        y="Group",
        orientation="h"
    )

    fig.update_layout(
        height=max(500, len(grp) * 25)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    act = (
        filtered.groupby("Activity")
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
        .head(20)
    )

    st.subheader("Top Activities")

    st.plotly_chart(
        px.bar(
            act,
            x="Activity",
            y="Count"
        ),
        use_container_width=True
    )

# ======================================================
# Approval Status
# ======================================================

status = (
    filtered.groupby("Approval Status")
    .size()
    .reset_index(name="Count")
)

st.subheader("Approval Status")

st.plotly_chart(
    px.pie(
        status,
        names="Approval Status",
        values="Count",
        hole=0.5
    ),
    use_container_width=True
)

# ======================================================
# Activities Over Time
# ======================================================

if (
    "Event Date" in filtered.columns
    and filtered["Event Date"].notna().any()
):

    trend_df = filtered.dropna(
        subset=["Event Date"]
    ).copy()

    trend_df["Month"] = (
        trend_df["Event Date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    trend = (
        trend_df.groupby("Month")
        .size()
        .reset_index(name="Count")
    )

    st.subheader("Activities Over Time")

    st.plotly_chart(
        px.line(
            trend,
            x="Month",
            y="Count",
            markers=True
        ),
        use_container_width=True
    )

# ======================================================
# Activity Records Table
# ======================================================

st.subheader("Activity Records")

display_columns = [
    "Group",
    "Activity",
    "Event Date",
    "Approval Status"
]

available_columns = [
    col
    for col in display_columns
    if col in filtered.columns
]

table_df = filtered[available_columns].rename(
    columns={
        "Group": "Scout Group",
        "Activity": "Activity Type",
        "Event Date": "Activity Date",
        "Approval Status": "Status"
    }
)

st.dataframe(
    table_df,
    use_container_width=True
)

# ======================================================
# Download CSV
# ======================================================

st.download_button(
    "Download Filtered Data",
    filtered.to_csv(index=False),
    file_name="activities_filtered.csv",
    mime="text/csv"
)
