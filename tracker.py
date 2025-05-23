import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import streamlit as st

# Ensure the output directory
OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "Instagram Reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# PDF generation
def generate_pdf_report(chart_file, top_posts, engagement_by_type, output_path):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Instagram Engagement Report", ln=True, align="C")
    pdf.image(chart_file, x=10, y=30, w=180)
    pdf.ln(105)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Average Engagement Rate by Post Type:", ln=True)
    pdf.set_font("Arial", "", 11)
    for post_type, rate in engagement_by_type.items():
        pdf.cell(0, 8, f"{post_type}: {rate:.4f}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Top 5 Posts by Engagement Rate:", ln=True)
    pdf.set_font("Arial", "", 10)
    for _, row in top_posts.iterrows():
        post_time = row['Publish time'].strftime('%Y-%m-%d')
        post_type = row['Post type']
        reach = int(row['Reach'])
        rate = f"{row['Engagement Rate']:.4f}"
        pdf.multi_cell(0, 6, f"- {post_time} | {post_type} | Reach: {reach} | Rate: {rate}")

    pdf.output(output_path)

# Analysis function
def analyze_data(file):
    df = pd.read_csv(file)
    df['Publish time'] = pd.to_datetime(df['Publish time'])

    df['Engagement Rate'] = (
        df[['Likes', 'Shares', 'Comments', 'Saves']].fillna(0).sum(axis=1)
    ) / df['Reach'].replace(0, pd.NA)

    df = df.sort_values('Publish time')
    df['Rolling Engagement Rate'] = df['Engagement Rate'].rolling(window=5).mean()

    df['Day of Week'] = df['Publish time'].dt.day_name()
    df['Hour'] = df['Publish time'].dt.hour

    engagement_by_type = df.groupby('Post type')['Engagement Rate'].mean()
    engagement_by_day = df.groupby('Day of Week')['Engagement Rate'].mean().sort_values(ascending=False)
    engagement_by_hour = df.groupby('Hour')['Engagement Rate'].mean().sort_index()
    top_posts = df.sort_values('Engagement Rate', ascending=False).head(5)

    chart_file = os.path.join(OUTPUT_DIR, "engagement_trend_chart.png")
    pdf_file = os.path.join(OUTPUT_DIR, "instagram_report.pdf")

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(df['Publish time'], df['Engagement Rate'], label='Daily Engagement')
    plt.plot(df['Publish time'], df['Rolling Engagement Rate'], linestyle='--', label='5-Day Rolling Avg')
    plt.xlabel('Date')
    plt.ylabel('Engagement Rate')
    plt.title('Instagram Engagement Trend')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(chart_file)
    plt.close()

    generate_pdf_report(chart_file, top_posts, engagement_by_type, pdf_file)

    return df, engagement_by_type, engagement_by_day, engagement_by_hour, top_posts, chart_file, pdf_file

# Streamlit App
st.set_page_config(page_title="Instagram Tracker", layout="centered")
st.title("📊 Instagram Engagement Analyzer")

file = st.file_uploader("Upload Instagram CSV File", type="csv")

if file is not None:
    with st.spinner("Analyzing data..."):
        try:
            df, engagement_by_type, engagement_by_day, engagement_by_hour, top_posts, chart_file, pdf_file = analyze_data(file)

            st.success("✅ Analysis complete!")
            st.image(chart_file, caption="Engagement Trend")

            st.subheader("📌 Average Engagement Rate by Post Type")
            st.dataframe(engagement_by_type.reset_index().rename(columns={0: 'Engagement Rate'}))

            st.subheader("📆 Engagement Rate by Day of the Week")
            st.bar_chart(engagement_by_day)

            st.subheader("⏰ Engagement Rate by Hour of Day")
            st.line_chart(engagement_by_hour)

            st.subheader("🔥 Top 5 Posts by Engagement Rate")
            st.dataframe(top_posts[['Publish time', 'Post type', 'Reach', 'Likes', 'Comments', 'Shares', 'Saves', 'Engagement Rate']])

            with open(pdf_file, "rb") as f:
                st.download_button("📄 Download PDF Report", f, file_name="instagram_report.pdf")

        except Exception as e:
            st.error(f"Something went wrong: {e}")








