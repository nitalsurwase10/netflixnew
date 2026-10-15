#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import base64
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Netflix Insights", page_icon="N", layout="wide")

DATA_FILES = ("Netflix.csv.csv", "netflix.csv", "Netflix.csv")
PROJECT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_DIR / "assets"
LOGO_PATH = next(
	(path for path in (
		ASSETS_DIR / "netflix_logo.png",
		PROJECT_DIR / "download.png",
		PROJECT_DIR.parent / "download.png",
	) if path.exists()),
	None,
)
BACKGROUND_PATH = next(
	(path for path in (
		ASSETS_DIR / "netflix_background.jpg",
		PROJECT_DIR / "the_netflix_login_background_canada_2024__by_logofeveryt_dh0w8qv-fullview.jpg",
		PROJECT_DIR.parent / "the_netflix_login_background_canada_2024__by_logofeveryt_dh0w8qv-fullview.jpg",
	) if path.exists()),
	None,
)
PALETTE = ["#e50914", "#b20710", "#ff3038", "#8b0000", "#c21824", "#721018", "#a20a0a", "#5c080d"]


def load_data(uploaded_content=None):
	if uploaded_content is not None:
		data = pd.read_csv(BytesIO(uploaded_content))
	else:
		data_path = next(
			(
				path
				for path in (PROJECT_DIR / filename for filename in DATA_FILES)
				if path.exists()
			),
			PROJECT_DIR / "sample_netflix.csv",
		)
		data = pd.read_csv(data_path)

	required_columns = (
		"Customer_ID",
		"Region",
		"Subscription_Plan",
		"Category",
		"Watch_Date",
		"Monthly_Revenue",
		"Rating",
		"Watch_Time_Minutes",
		"Watch_Count",
	)
	missing_columns = [column for column in required_columns if column not in data.columns]
	if missing_columns:
		raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")

	data["Watch_Date"] = pd.to_datetime(data["Watch_Date"], errors="coerce")
	for column in ("Monthly_Revenue", "Rating", "Watch_Time_Minutes", "Watch_Count"):
		data[column] = pd.to_numeric(data[column], errors="coerce")
	return data.drop_duplicates()


def format_currency(value):
	return f"₹{value:,.0f}"


def style_axis(axis, *, horizontal=False):
	axis.set_facecolor("#151515")
	axis.grid(axis="x" if horizontal else "y", color="#383838", linewidth=0.8)
	axis.set_axisbelow(True)
	axis.spines[["top", "right", "left", "bottom"]].set_visible(False)
	axis.tick_params(colors="#eeeeee", length=0, pad=7)


def show_chart(figure):
	figure.patch.set_facecolor("#151515")
	st.pyplot(figure, width="stretch")
	plt.close(figure)


uploaded_file = st.sidebar.file_uploader(
	"Upload your Netflix dataset",
	type="csv",
	help="Your uploaded file is used for this session and is not added to the project.",
)

try:
	if uploaded_file is not None:
		netflix = load_data(uploaded_file.getvalue())
	else:
		netflix = load_data()
		if not any((PROJECT_DIR / filename).exists() for filename in DATA_FILES):
			st.info("Showing synthetic demo data. Upload your own CSV in the sidebar to explore your data.")
except (FileNotFoundError, ValueError, pd.errors.EmptyDataError, pd.errors.ParserError) as error:
	st.error(f"Unable to load the Netflix dataset: {error}")
	st.stop()

background_image = "none"
if BACKGROUND_PATH:
	encoded_background = base64.b64encode(BACKGROUND_PATH.read_bytes()).decode("ascii")
	background_image = f'url("data:image/jpeg;base64,{encoded_background}")'

st.markdown(
	f"""
	<style>
	.stApp {{
		background-color: #090909;
		background-image: linear-gradient(rgba(0, 0, 0, 0.78), rgba(0, 0, 0, 0.96)), {background_image};
		background-position: center top;
		background-size: cover;
		background-attachment: fixed;
		color: #f5f5f5;
	}}
	[data-testid="stSidebar"] {{ background: #090909; border-right: 1px solid #3b1114; }}
	[data-testid="stSidebar"] * {{ color: #f5f5f5; }}
	[data-testid="stMetric"] {{
		background: rgba(17, 17, 17, 0.94); border: 1px solid #383838; border-top: 2px solid #e50914;
		border-radius: 6px; padding: 16px 18px; min-height: 108px;
	}}
	[data-testid="stMetricLabel"] {{ color: #c8c8c8; }}
	[data-testid="stMetricValue"] {{ color: #ffffff; }}
	.stButton > button {{ background: #e50914; color: #ffffff; border: 0; }}
	h1, h2, h3 {{ color: #ffffff; letter-spacing: 0 !important; }}
	h1 {{ border-bottom: 2px solid #e50914; padding-bottom: 0.35rem; }}
	[data-testid="stDataFrame"] {{ border: 1px solid #383838; }}
	</style>
	""",
	unsafe_allow_html=True,
)

logo_column, title_column = st.columns([0.12, 0.88], vertical_alignment="center")
with logo_column:
	if LOGO_PATH:
		st.image(str(LOGO_PATH), width=72)
with title_column:
	st.title("Netflix Insights")
st.caption("A viewing and revenue snapshot from your Netflix dataset")

with st.sidebar:
	st.header("Filters")
	regions = st.multiselect("Region", sorted(netflix["Region"].dropna().unique()), default=sorted(netflix["Region"].dropna().unique()))
	plans = st.multiselect(
		"Subscription plan",
		sorted(netflix["Subscription_Plan"].dropna().unique()),
		default=sorted(netflix["Subscription_Plan"].dropna().unique()),
	)
	categories = st.multiselect(
		"Category", sorted(netflix["Category"].dropna().unique()), default=sorted(netflix["Category"].dropna().unique())
	)
	valid_dates = netflix["Watch_Date"].dropna()
	if not valid_dates.empty:
		date_range = st.date_input(
			"Watch date",
			value=(valid_dates.min().date(), valid_dates.max().date()),
			min_value=valid_dates.min().date(),
			max_value=valid_dates.max().date(),
		)
	else:
		date_range = ()

filtered = netflix[
	netflix["Region"].isin(regions)
	& netflix["Subscription_Plan"].isin(plans)
	& netflix["Category"].isin(categories)
].copy()
if len(date_range) == 2:
	start_date, end_date = date_range
	filtered = filtered[filtered["Watch_Date"].dt.date.between(start_date, end_date)]

if filtered.empty:
	st.info("No titles match these filters. Adjust the selections in the sidebar.")
	st.stop()

revenue = filtered["Monthly_Revenue"].sum()
customers = filtered["Customer_ID"].nunique()
average_rating = filtered["Rating"].mean()
watch_hours = filtered["Watch_Time_Minutes"].sum() / 60

metric_columns = st.columns(4)
metric_columns[0].metric("Total revenue", format_currency(revenue))
metric_columns[1].metric("Customers", f"{customers:,}")
metric_columns[2].metric("Average rating", f"{average_rating:.2f} / 5" if pd.notna(average_rating) else "N/A")
metric_columns[3].metric("Watch time", f"{watch_hours:,.0f} hrs")

st.subheader("Revenue and viewing")
left, right = st.columns(2)

with left:
	st.markdown("**Revenue by region**")
	region_revenue = filtered.groupby("Region")["Monthly_Revenue"].sum().sort_index()
	figure, axis = plt.subplots(figsize=(7, 3.6))
	axis.bar(region_revenue.index, region_revenue.values, color=PALETTE[0], width=0.62)
	axis.set_ylabel("Monthly revenue (INR)", color="#5e5e5e")
	style_axis(axis)
	show_chart(figure)

with right:
	st.markdown("**Subscription-wise rating**")
	plan_ratings = filtered.groupby("Subscription_Plan")["Rating"].sum()
	figure, axis = plt.subplots(figsize=(7, 3.6))
	axis.pie(
		plan_ratings.values,
		labels=plan_ratings.index,
		colors=PALETTE[: len(plan_ratings)],
		startangle=90,
		textprops={"color": "#f5f5f5"},
	)
	axis.axis("equal")
	show_chart(figure)

left, right = st.columns(2)
with left:
	st.markdown("**Revenue by category**")
	category_revenue = filtered.groupby("Category")["Monthly_Revenue"].sum().sort_index()
	figure, axis = plt.subplots(figsize=(7, 4.2))
	axis.bar(category_revenue.index, category_revenue.values, color=PALETTE[2], width=0.62)
	axis.set_ylabel("Monthly revenue (INR)", color="#5e5e5e")
	axis.tick_params(axis="x", labelrotation=35)
	style_axis(axis)
	show_chart(figure)

with right:
	st.markdown("**Revenue over time**")
	monthly_revenue = filtered.dropna(subset=["Watch_Date"]).set_index("Watch_Date").resample("MS")["Monthly_Revenue"].sum()
	figure, axis = plt.subplots(figsize=(7, 4.2))
	axis.plot(monthly_revenue.index, monthly_revenue.values, color=PALETTE[0], linewidth=2.5, marker="o", markersize=5)
	axis.set_ylabel("Revenue (INR)", color="#5e5e5e")
	style_axis(axis)
	figure.autofmt_xdate(rotation=0)
	show_chart(figure)

with st.expander("View filtered records"):
	st.dataframe(filtered, width="stretch", hide_index=True)
