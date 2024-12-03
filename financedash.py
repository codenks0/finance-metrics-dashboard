from faker import Faker
import streamlit as st
import pandas as pd
import random
import sqlite3
import plotly.express as px

fake = Faker()

# Create or reset the database
def create_database():
    connection = sqlite3.connect('statement.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS invoices(
        invoice_id TEXT PRIMARY KEY,
        client_name TEXT,
        amount_due REAL,
        due_date TEXT,
        category TEXT,
        status TEXT)''')
    connection.commit()
    connection.close()

# Insert data into the database
def insert_invoices(invoice_count=25):
    connection = sqlite3.connect('statement.db')
    cursor = connection.cursor()
    for i in range(invoice_count):
        invoice = {
            'invoice_id': fake.uuid4(),
            'client_name': fake.company(),
            'amount_due': round(random.uniform(100, 5000), 2),
            'due_date': fake.date_this_month(),
            'category': random.choice(['Receivable', 'Payable']),
            'status': random.choice(['Paid', 'Pending', 'Overdue'])
        }
        cursor.execute('''INSERT INTO invoices (invoice_id, client_name, amount_due, due_date, category, status) 
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (invoice['invoice_id'], invoice['client_name'], invoice['amount_due'], 
                        invoice['due_date'], invoice['category'], invoice['status']))
    connection.commit()
    connection.close()

# Fetch all invoices
@st.cache_data
def get_invoices():
    connection = sqlite3.connect('statement.db')
    query = "SELECT * FROM invoices"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Main App
create_database()
insert_invoices()

# Title and Header
st.markdown("""
# 📊 **Invoice Metrics Dashboard**
*By Nana Asare*
---
""")

invoice_df = get_invoices()

# Tabs for different views
tab1, tab2, tab3 = st.tabs(['All Invoices', 'Accounts Receivable', 'Accounts Payable'])

# Tab: All Invoices
with tab1:
    st.markdown("### All Invoices Overview")
    st.write("Below is a complete list of all invoices:")
    # Using DataFrame with styling
    st.dataframe(invoice_df.style.format({'amount_due': "${:,.2f}"}).set_properties(subset=['invoice_id'], **{'width': '200px'}))

# Tab: Accounts Receivable
with tab2:
    st.markdown("### Accounts Receivable")
    receivables = invoice_df[invoice_df['category'] == 'Receivable']
    st.write("Invoices categorized as Receivables:")
    
    # Display Receivables Data with Styling
    st.dataframe(receivables.style.format({'amount_due': "${:,.2f}"}).set_properties(subset=['invoice_id'], **{'width': '200px'}))
    
    # Pie chart for receivables by status with improved color scheme
    receivable_status_counts = receivables['status'].value_counts().reset_index()
    receivable_status_counts.columns = ['Status', 'Count']
    pie_chart = px.pie(receivable_status_counts, values='Count', names='Status', 
                       title="Receivables Status Distribution", 
                       color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(pie_chart)

# Tab: Accounts Payable
with tab3:
    st.markdown("### Accounts Payable")
    payables = invoice_df[invoice_df['category'] == 'Payable']
    st.write("Invoices categorized as Payables:")
    
    # Display Payables Data with Styling
    st.dataframe(payables.style.format({'amount_due': "${:,.2f}"}).set_properties(subset=['invoice_id'], **{'width': '200px'}))
    
    # Pie chart for payables by status with improved color scheme
    payable_status_counts = payables['status'].value_counts().reset_index()
    payable_status_counts.columns = ['Status', 'Count']
    pie_chart = px.pie(payable_status_counts, values='Count', names='Status', 
                       title="Payables Status Distribution", 
                       color_discrete_sequence=px.colors.sequential.Reds)
    st.plotly_chart(pie_chart)

# Footer with Name
st.markdown("""
---
 **Dashboard by Nana Asare**  
Data generated using external library.
""")
