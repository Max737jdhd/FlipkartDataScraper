import pandas as pd
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from datetime import datetime

LOG_FILE = "scraper_log.txt"

# Function to save log with multiple parameters
def save_log(url, total_records, pages_scraped):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | URL: {url} | Pages: {pages_scraped} | Records: {total_records}\n"
    with open(LOG_FILE, "a") as f:
        f.write("---------------------------------------------------------------")
        f.write("\n\n")
        f.write(log_entry)

def load_log():
    try:
        with open(LOG_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No logs found"

def scrape_data(base_url, max_pages=12):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    Product_name, Prices, Description, Reviews = [], [], [], []

    for page_num in range(1, max_pages + 1):
        url = f"{base_url}&page={page_num}"
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")
            box = soup.find("div", class_="DOjaWF gdgoEp")
            
            if not box:
                break

            # Scraping logic remains same
            names = [name.text.strip() for name in box.find_all("div", class_="KzDlHZ")]
            prices = [price.text.strip() for price in box.find_all("div", class_="Nx9bqj _4b5DiR")]
            descriptions = [" | ".join([li.text for li in d.find_all('li')]) or "No description" 
                          for d in box.find_all("ul", class_="G4BRas")]
            reviews = [review.text.strip() or "No rating" 
                      for review in box.find_all("div", class_="XQDdHH")]

            # Padding logic
            max_len = max(len(names), len(prices), len(descriptions), len(reviews))
            Product_name.extend(names + ["N/A"]*(max_len-len(names)))
            Prices.extend(prices + ["N/A"]*(max_len-len(prices)))
            Description.extend(descriptions + ["N/A"]*(max_len-len(descriptions)))
            Reviews.extend(reviews + ["N/A"]*(max_len-len(reviews)))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Page {page_num}: {str(e)}")
            break

    return pd.DataFrame({
        "Product Name": Product_name,
        "Price": Prices,
        "Specifications": Description,
        "Rating": Reviews
    }) if Product_name else None

def save_data(df):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")]
    )
    if file_path:
        try:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))




def start_scraping():
    def process_scraping():
        url = url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter URL")
            return
        
        df = scrape_data(url)
        if df is None:
            messagebox.showerror("Error", "No data scraped")
            return
            
        total_records = len(df)
        pages_scraped = min(12, total_records//20)  # 20 items/page assumption
        save_log(url, total_records, pages_scraped)
        
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, df.to_string(index=False))
        summary_label.config(text=f"Pages: {pages_scraped} | Records: {total_records}")
        save_button.config(command=lambda: save_data(df))

    main_window.withdraw()
    scrape_window = tk.Toplevel()
    scrape_window.title("Scraper")
    scrape_window.geometry("800x700")

    tk.Label(scrape_window, text="Enter URL:").pack(pady=10)
    url_entry = tk.Entry(scrape_window, width=80)
    url_entry.pack()
    tk.Button(scrape_window, text="Clear", command=lambda: url_entry.delete(0, tk.END),width=30).pack(pady=10)
    
    tk.Button(scrape_window, text="Start Scraping", command=process_scraping,width=30).pack(pady=10)
    
    text_box = scrolledtext.ScrolledText(scrape_window,bg="lightblue", wrap=tk.WORD, width=100, height=25)
    text_box.pack(padx=10, pady=10)
    
    summary_label = tk.Label(scrape_window, text="Pages: 0 | Records: 0", fg="blue",width=30)
    summary_label.pack()
    
    save_button = tk.Button(scrape_window, text="Save Excel",width=30,bg="lightgreen")
    save_button.pack(pady=5)
    
    tk.Button(scrape_window, text="Back", command=lambda:[
        scrape_window.destroy(), 
        main_window.deiconify()
    ],width=30,bg="#ff4444").pack()

def view_logs():
    log_window = tk.Toplevel()
    log_window.title("Scraping History")
    log_text = scrolledtext.ScrolledText(log_window, width=70, height=15)
    log_text.pack(padx=10, pady=10)
    log_text.insert(tk.END, load_log())
    tk.Button(log_window, text="Back", command=log_window.destroy,bg="#ff4444").pack()

# Main UI
main_window = tk.Tk()
main_window.title("Web Scraper")
main_window.geometry("400x250")

tk.Label(main_window, text="Main Menu", font=("Arial", 14)).pack(pady=15)
tk.Button(main_window, text="Start Scraping", command=start_scraping, width=20).pack(pady=5)
tk.Button(main_window, text="View History", command=view_logs, width=20).pack(pady=5)
tk.Button(main_window, text="Exit", command=main_window.quit, bg="#ff4444", width=20).pack(pady=5)

main_window.mainloop()
