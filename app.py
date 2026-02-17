import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Assist Living – Finder", layout="wide")

# ===============================
# LOAD DATA
# ===============================
facilities_url = "https://docs.google.com/spreadsheets/d/1YZHuPnX4BA4IHvvEnLmXm4Rialnf77i9xqCUexYCcfs/export?format=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(facilities_url)
    return df

df = load_data()

# ===============================
# CLEAN COLUMN NAMES
# ===============================
df.columns = df.columns.str.strip()

def find_col(keyword):
    for c in df.columns:
        if keyword in c.lower():
            return c
    return None

name_col = find_col("name") or df.columns[0]
city_col = find_col("city")
units_col = find_col("unit")
beds_col = find_col("bed")

# ===============================
# FORCE NUMERIC (fixes errors)
# ===============================
if units_col:
    df[units_col] = pd.to_numeric(df[units_col], errors="coerce")

if beds_col:
    df[beds_col] = pd.to_numeric(df[beds_col], errors="coerce")

# ===============================
# ESTIMATE COST FUNCTION
# ===============================
def estimate_cost(row):
    base = 2500

    units = row[units_col] if units_col and pd.notnull(row[units_col]) else 50
    beds = row[beds_col] if beds_col and pd.notnull(row[beds_col]) else 50

    try:
        units = float(units)
    except:
        units = 50

    try:
        beds = float(beds)
    except:
        beds = 50

    cost = base + (units * 5) + (beds * 3)

    low = int(cost * 0.9)
    high = int(cost * 1.2)

    return f"${low:,} – ${high:,}"

df["Estimated Monthly Cost"] = df.apply(estimate_cost, axis=1)

# ===============================
# UI HEADER
# ===============================
st.title("🏥 AI Assist Living – Facility Finder (Prototype)")
st.caption("Helping families compare assisted living options with transparent data")

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("Filter Facilities")

filtered_df = df.copy()

# 🔍 Search
search = st.sidebar.text_input("Search facility name")
if search:
    filtered_df = filtered_df[
        filtered_df[name_col].str.contains(search, case=False, na=False)
    ]

# City filter
if city_col:
    cities = sorted(df[city_col].dropna().unique())
    selected_cities = st.sidebar.multiselect("City", cities)
    if selected_cities:
        filtered_df = filtered_df[filtered_df[city_col].isin(selected_cities)]

# Units slider
if units_col:
    max_units = int(filtered_df[units_col].fillna(0).max())
    unit_range = st.sidebar.slider("Units Capacity", 0, max_units, (0, max_units))
    filtered_df = filtered_df[
        (filtered_df[units_col].fillna(0) >= unit_range[0]) &
        (filtered_df[units_col].fillna(0) <= unit_range[1])
    ]

# ===============================
# TOP MATCHES
# ===============================
st.subheader("🔍 Top Matching Facilities")

display_cols = [name_col, "Estimated Monthly Cost"]

if city_col:
    display_cols.insert(1, city_col)

if units_col:
    display_cols.append(units_col)

top_df = filtered_df[display_cols].head(20)

st.dataframe(top_df, use_container_width=True)

# ===============================
# METRICS
# ===============================
col1, col2 = st.columns(2)

col1.metric("Total Facilities", len(filtered_df))

if len(filtered_df):
    col2.metric("Typical Price Range", filtered_df["Estimated Monthly Cost"].mode()[0])
else:
    col2.metric("Typical Price Range", "-")

# ===============================
# DOWNLOAD BUTTON
# ===============================
st.download_button(
    "⬇ Download filtered results as CSV",
    filtered_df.to_csv(index=False),
    file_name="assisted_living_filtered.csv",
    mime="text/csv"
)

# ===============================
# RAW DATA
# ===============================
with st.expander("View raw dataset"):
    st.dataframe(filtered_df, use_container_width=True)

# ===============================
# FOOTER
# ===============================
st.caption("Prototype built by Ajay | Data-driven assisted living decision tool")
