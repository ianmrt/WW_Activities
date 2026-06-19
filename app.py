
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Adventurous Activities Dashboard", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_excel("data.xlsx")

    df["Activity"] = df["Activity"].fillna("").astype(str).str.strip().str.title()
    df["Group"] = df["Group"].fillna("Unknown")

    def approval_status(v):
        if pd.isna(v) or str(v).strip() == "":
            return "Awaiting Approval"
        v = str(v).strip().lower()
        if v in ["yes", "approved", "y"]:
            return "Approved"
        if v in ["no", "rejected", "n"]:
            return "Not Approved"
        return str(v)

    df["Approval Status"] = df["Approved "].apply(approval_status)

    try:
        df["Event Date"] = pd.to_datetime(df["Date of Event (start date)"], errors="coerce")
    except Exception:
        df["Event Date"] = pd.NaT

    return df

df = load_data()

st.title("Adventurous Activities Approval Dashboard")

groups = sorted(df["Group"].dropna().unique())
activities = sorted(df["Activity"].dropna().unique())

c1, c2 = st.columns(2)
selected_groups = c1.multiselect("Group", groups)
selected_activities = c2.multiselect("Activity", activities)

filtered = df.copy()

if selected_groups:
    filtered = filtered[filtered["Group"].isin(selected_groups)]

if selected_activities:
    filtered = filtered[filtered["Activity"].isin(selected_activities)]

total = len(filtered)
approved = (filtered["Approval Status"] == "Approved").sum()
awaiting = (filtered["Approval Status"] == "Awaiting Approval").sum()
not_approved = (filtered["Approval Status"] == "Not Approved").sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Activities", total)
k2.metric("Approved", approved)
k3.metric("Awaiting Approval", awaiting)
k4.metric("Not Approved", not_approved)

st.divider()

left, right = st.columns(2)

with left:
    grp = filtered.groupby("Group").size().reset_index(name="Count").sort_values("Count", ascending=False)
    st.subheader("Activities by Group")
    st.plotly_chart(px.bar(grp, x="Group", y="Count"), use_container_width=True)

with right:
    act = filtered.groupby("Activity").size().reset_index(name="Count").sort_values("Count", ascending=False).head(20)
    st.subheader("Top Activities")
    st.plotly_chart(px.bar(act, x="Activity", y="Count"), use_container_width=True)

status = filtered.groupby("Approval Status").size().reset_index(name="Count")
st.subheader("Approval Status")
st.plotly_chart(px.pie(status, names="Approval Status", values="Count", hole=0.5), use_container_width=True)

if filtered["Event Date"].notna().any():
    trend = filtered.dropna(subset=["Event Date"]).groupby(pd.Grouper(key="Event Date", freq="M")).size().reset_index(name="Count")
    st.subheader("Activities Over Time")
    st.plotly_chart(px.line(trend, x="Event Date", y="Count"), use_container_width=True)

st.subheader("Activity Records")
st.dataframe(filtered, use_container_width=True)

st.download_button(
    "Download Filtered Data",
    filtered.to_csv(index=False),
    file_name="activities_filtered.csv",
    mime="text/csv"
)
