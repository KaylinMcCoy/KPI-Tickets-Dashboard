import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="KPI Dashboard", layout="wide")
st.title("📊 KPI Dashboard")

#Phase 1: Data Loading & Cleaning

#Load CSV file from the data/ folder
df = pd.read_csv('data/customer_support_ticket_resolution_satisfaction.csv') 
print(df.to_string())

#Display the first few rows to verify it loaded correctly
print(df.head()) 

#Check the data types
print(df.info()) 

#Convert created_date to datetime format
df['created_date'] = pd.to_datetime(df['created_date'], format='%Y-%m-%d')
print(df['created_date'].dtype)

#Create your experience level groups (junior/mid/senior)
def experience_categories(years):
    if years <= 2:
     return 'Junior'
    elif years >= 3 and years <= 5:
     return 'Mid'
    elif years > 5:
     return 'Senior'    
df['experience_buckets'] = df['agent_experience_years'].apply(experience_categories)

#Phase2:Build Filtering Logic

#Reopened toggle (checkbox to include/exclude reopened tickets)
include_reopened = st.checkbox('Include reopened tickets?')

#Category filter (dropdown for Delivery, Account, Technical, Billing, Other)
selected_categories = st.multiselect('Select Categories',df['issue_category'].unique())

#Experience level filter (dropdown for Junior, Mid, Senior)
selected_experience = st.multiselect(label="Select Experience Levels",options=['Junior', 'Mid', 'Senior'])

# Date range filter (pick start and end dates)
start_date = st.date_input('Start Date')
end_date = st.date_input('End Date')

# Convert to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Create filtered dataframe (apply all filters)
filtered_df = df[
    (df['issue_category'].isin(selected_categories)) &
    (df['experience_buckets'].isin(selected_experience)) &
    (df['created_date'] >= start_date) &
    (df['created_date'] <= end_date)
]
# Handle reopened filter
if not include_reopened:
    filtered_df = filtered_df[filtered_df['reopened'] == 'No']

# Display the filtered data
st.dataframe(filtered_df)

#Phase 3: Calculate KPI Metrics

#converting Hours to Days
filtered_df['resolution_days'] = filtered_df['resolution_time_hours'] / 24

#counting the tickets under the threshhold per day
under_1_day = (filtered_df['resolution_days'] <= 1).sum()
under_2_days = (filtered_df['resolution_days'] <= 2).sum()
under_3_days = (filtered_df['resolution_days'] <= 3).sum()
under_4_days = (filtered_df['resolution_days'] <= 4).sum()
under_5_days = (filtered_df['resolution_days'] <= 5).sum()
under_6_days = (filtered_df['resolution_days'] <= 6).sum()
under_7_days = (filtered_df['resolution_days'] <= 7).sum()

# Calculate all the percentages
pct_under_1_day = (under_1_day / len(filtered_df)) * 100
pct_under_2_days = (under_2_days / len(filtered_df)) * 100
pct_under_3_days = (under_3_days / len(filtered_df)) * 100
pct_under_4_days = (under_4_days / len(filtered_df)) * 100
pct_under_5_days = (under_5_days / len(filtered_df)) * 100
pct_under_7_days = (under_7_days / len(filtered_df)) * 100

# Create dataframe with actual percentages
sla_df = pd.DataFrame({
    'Days': ['1', '2', '3', '4', '5', '7'],
    'Percentage': [pct_under_1_day, pct_under_2_days, pct_under_3_days, pct_under_4_days, pct_under_5_days, pct_under_7_days]
})


st.dataframe(sla_df)

# line chart
fig = px.line(sla_df, x='Days', y='Percentage', markers=True, 
              title='SLA Distribution: % Tickets Resolved',
              labels={'Percentage': 'Percentage (%)', 'Days': 'Resolution Time (Days)'})

st.plotly_chart(fig, use_container_width=True)

# METRIC 2: Speed Metrics
st.subheader("Speed Metrics")

# Overall averages
avg_resolution = filtered_df['resolution_time_hours'].mean()
avg_first_response = filtered_df['first_response_minutes'].mean()

st.write(f"**Average Resolution Time:** {avg_resolution:.2f} hours")
st.write(f"**Average First Response Time:** {avg_first_response:.2f} minutes")

# By Category
st.write("**By Category:**")
by_category = filtered_df.groupby('issue_category')[['resolution_time_hours', 'first_response_minutes']].mean()
st.dataframe(by_category)

# By Priority
st.write("**By Priority:**")
by_priority = filtered_df.groupby('priority')[['resolution_time_hours', 'first_response_minutes']].mean()
st.dataframe(by_priority)

# METRIC 3: Volume Metrics
st.subheader("Volume Metrics")

# Ticket count and avg resolution by category
st.write("**Tickets by Category:**")
volume_by_category = filtered_df.groupby('issue_category').agg({
    'ticket_id': 'count',
    'resolution_time_hours': 'mean'
}).rename(columns={'ticket_id': 'Count', 'resolution_time_hours': 'Avg Resolution (hours)'})
st.dataframe(volume_by_category)

# METRIC 4: Agent Performance
st.subheader("Agent Performance")

# By experience level
st.write("**By Experience Level:**")
agent_performance = filtered_df.groupby('experience_buckets').agg({
    'ticket_id': 'count',
    'resolution_time_hours': 'mean'
}).rename(columns={'ticket_id': 'Count', 'resolution_time_hours': 'Avg Resolution (hours)'})
st.dataframe(agent_performance)

# By Category - Resolution Time (BAR CHART)
by_category_resolution = filtered_df.groupby('issue_category')['resolution_time_hours'].mean().reset_index()
fig_category_resolution = px.bar(by_category_resolution, x='issue_category', y='resolution_time_hours',
                                  title='Avg Resolution Time by Category',
                                  labels={'issue_category': 'Category', 'resolution_time_hours': 'Hours'})
st.plotly_chart(fig_category_resolution, use_container_width=True)

# Convert "By Category" first response time to a bar chart
by_category_first_response = filtered_df.groupby('issue_category')['first_response_minutes'].mean().reset_index()
fig_category_first_response = px.bar(by_category_first_response, x='issue_category', y='first_response_minutes',
                                      title='Avg First Response Time by Category',
                                      labels={'issue_category': 'Category', 'first_response_minutes': 'Minutes'})
st.plotly_chart(fig_category_first_response, use_container_width=True)

# Convert "By Priority" 
# By Priority - Resolution Time
by_priority_resolution = filtered_df.groupby('priority')['resolution_time_hours'].mean().reset_index()
fig_priority_resolution = px.bar(by_priority_resolution, x='priority', y='resolution_time_hours',
                                  title='Avg Resolution Time by Priority',
                                  labels={'priority': 'Priority', 'resolution_time_hours': 'Hours'})
st.plotly_chart(fig_priority_resolution, use_container_width=True)

# By Priority - First Response Time
by_priority_first_response = filtered_df.groupby('priority')['first_response_minutes'].mean().reset_index()
fig_priority_first_response = px.bar(by_priority_first_response, x='priority', y='first_response_minutes',
                                      title='Avg First Response Time by Priority',
                                      labels={'priority': 'Priority', 'first_response_minutes': 'Minutes'})
st.plotly_chart(fig_priority_first_response, use_container_width=True)

# Convert "Tickets by Category" to a bar chart
volume_by_category = filtered_df.groupby('issue_category')['ticket_id'].count().reset_index()
fig_volume_by_category = px.bar(volume_by_category, x='issue_category', y='ticket_id',
                                 title='Volume of Tickets by Category',
                                 labels={'issue_category': 'Category', 'ticket_id': 'Ticket Count'})
st.plotly_chart(fig_volume_by_category, use_container_width=True)

# Convert "Agent Performance" to a bar chart
# Agent Performance - Ticket Count
agent_count = filtered_df.groupby('experience_buckets')['ticket_id'].count().reset_index()
fig_agent_count = px.bar(agent_count, x='experience_buckets', y='ticket_id',
                          title='Ticket Count by Experience Level',
                          labels={'experience_buckets': 'Experience Level', 'ticket_id': 'Ticket Count'})
st.plotly_chart(fig_agent_count, use_container_width=True)

# Agent Performance - Avg Resolution Time
agent_resolution = filtered_df.groupby('experience_buckets')['resolution_time_hours'].mean().reset_index()
fig_agent_resolution = px.bar(agent_resolution, x='experience_buckets', y='resolution_time_hours',
                               title='Avg Resolution Time by Experience Level',
                               labels={'experience_buckets': 'Experience Level', 'resolution_time_hours': 'Hours'})
st.plotly_chart(fig_agent_resolution, use_container_width=True)