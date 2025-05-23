# SPLASH FIRST, NO HEAVY IMPORTS
import tkinter as tk
import sys
sys.modules['jaraco.text'] = None


def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.configure(bg="white")
    width, height = 300, 100
    x = (splash.winfo_screenwidth() // 2) - (width // 2)
    y = (splash.winfo_screenheight() // 2) - (height // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")

    label = tk.Label(splash, text="📊 Loading Instagram Tracker...", font=("Arial", 12), bg="white")
    label.pack(expand=True)

    splash.update()
    splash.after(2000, splash.destroy)
    splash.mainloop()

show_splash()  # Show splash before anything else

# NOW IMPORT EVERYTHING ELSE
import os
import time 
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from tkinter import filedialog, messagebox

# PDF GENERATION FUNCTION
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
    print(f"\n✅ PDF report saved as: {output_path}")

# ANALYSIS FUNCTION
def analyze_instagram_data(file_path):
    output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Instagram Reports")
    os.makedirs(output_dir, exist_ok=True)

    summary_file = os.path.join(output_dir, "engagement_summary.csv")
    top_posts_file = os.path.join(output_dir, "top_engagement_posts.csv")
    chart_file = os.path.join(output_dir, "engagement_trend_chart.png")
    pdf_file = os.path.join(output_dir, "instagram_report.pdf")

    df = pd.read_csv(file_path)
    df['Publish time'] = pd.to_datetime(df['Publish time'])

    df['Engagement Rate'] = (
        df[['Likes', 'Shares', 'Comments', 'Saves']].fillna(0).sum(axis=1)
    ) / df['Reach'].replace(0, pd.NA)

    df = df.sort_values('Publish time')
    df['Rolling Engagement Rate'] = df['Engagement Rate'].rolling(window=5).mean()

    engagement_by_type = df.groupby('Post type')['Engagement Rate'].mean()
    top_posts = df.sort_values('Engagement Rate', ascending=False).head(5)

    engagement_by_type.to_csv(summary_file)
    top_posts.to_csv(top_posts_file, index=False)

    plt.figure(figsize=(12, 6))
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

    #generate_pdf_report(chart_file, top_posts, engagement_by_type, pdf_file)

    print("\nAverage Engagement by Post Type:")
    print(engagement_by_type.sort_values(ascending=False))

    print("\nTop 5 Posts by Engagement Rate:")
    print(top_posts[['Publish time', 'Post type', 'Reach', 'Likes', 'Comments', 'Shares', 'Saves', 'Engagement Rate']])

    print(f"\n✅ All files saved to: {output_dir}")

# GUI FILE PICKER
def select_file_gui():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Instagram CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    print(f"📂 You selected: {file_path}")
    return file_path

# MAIN EXECUTION BLOCK
if __name__ == "__main__":
    print("✅ Script started")

    file_path = select_file_gui()
    time.sleep(1)

    if not file_path or not os.path.isfile(file_path):
        messagebox.showerror("Error", "❌ No valid file selected or provided.")
    else:
        print(f"📊 Analyzing file: {file_path}")
        try:
            analyze_instagram_data(file_path)
            print("✅ Analysis completed successfully.")
            messagebox.showinfo("Success", "✅ Analysis completed successfully.\nCheck your Desktop under 'Instagram Reports'.")
        except Exception as e:
            messagebox.showerror("Analysis Failed", f"❌ Something went wrong:\n\n{e}")
            print(f"❌ Analysis failed: {e}")







