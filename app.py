import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. Page Configuration
st.set_page_config(page_title="Omega 3 Price Dashboard", layout="wide")
st.title(" Omega 3 Market Price Analyzer (Jumia)")

# 2. Connect to SQL Server and Fetch Data
@st.cache_data # This keeps the app fast by caching data
def load_data():
    server_name = "localhost"
    database_name = "Company_SD"
    connection_string = f"mssql+pyodbc://@{server_name}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server"
    engine = create_engine(connection_string)
    
    # We will use a simplified query for pandas, or you can paste the long smart query here
    query = "SELECT * FROM dbo.Omega" 
    df = pd.read_sql(query, con=engine)
    return df

try:
    df = load_data()

    # 3. Sidebar Filters
    st.sidebar.header("Filter Options")
    search_query = st.sidebar.text_input("Search Product Name:", "")

    if search_query:
        df = df[df['Product_Name'].str.contains(search_query, case=False)]

    # 4. Display Key Metrics (KPIs)
    st.subheader("Market Summary")
    col1, col2 = st.columns(2)
    col1.metric(label="Total Products Found", value=len(df))
    col2.metric(label="Average Total Price", value=f"{round(df['Price'].str.extract(r'(\d+)').astype(float).mean()[0], 2)} EGP" if not df.empty else "N/A")

    # 5. Display Data Table
    st.subheader("Product List & Live Links")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error connecting to SQL Server: {e}")
    st.info("Make sure your SQL Server is running and server names are correct.")