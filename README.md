# Netflix Insights

A Streamlit dashboard for viewing and revenue data.

## Run locally

1. Install dependencies with `pip install -r requirements.txt`.
2. Optionally place your private dataset beside `netflixproject.py` as `Netflix.csv.csv`, `netflix.csv`, or `Netflix.csv`, or upload it in the app's sidebar.
3. Start the app with `streamlit run netflixproject.py`.

The customer dataset is intentionally not included in this repository. Without a private dataset, the app uses the clearly labeled synthetic data in `sample_netflix.csv`. The CSV needs `Customer_ID`, `Region`, `Subscription_Plan`, `Category`, `Watch_Date`, `Monthly_Revenue`, `Rating`, `Watch_Time_Minutes`, and `Watch_Count` columns. Uploaded data is used for the active app session and is not saved to the project.
