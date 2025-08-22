import tkinter as tk
from tkinter import messagebox
import threading
import time
import pandas as pd

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# کلاس اصلی برای گرفتن شغل‌ها
class JobScraper:
    def __init__(self, title, count):
        self.title = title
        self.count = int(count)
        self.data = []

        # باز کردن مرورگر Chrome با webdriver-manager
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def open_site(self):
        search = self.title.replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={search}"
        self.driver.get(url)
        time.sleep(5)  # صبر برای لود صفحه

    def get_jobs(self):
        try:
            # Scroll صفحه برای لود بیشتر شغل‌ها
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # پیدا کردن کارت‌های شغلی
            jobs = self.driver.find_elements(By.CLASS_NAME, "base-card")
            for job in jobs[:self.count]:
                try:
                    title = job.find_element(By.CLASS_NAME, "base-search-card__title").text
                    company = job.find_element(By.CLASS_NAME, "base-search-card__subtitle").text
                    loc = job.find_element(By.CLASS_NAME, "job-search-card__location").text
                    link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
                    self.data.append([title, company, loc, link])
                except:
                    continue
        except Exception as e:
            messagebox.showerror("خطا در گرفتن شغل‌ها", str(e))

    def close(self):
        self.driver.quit()

# توابع ذخیره داده‌ها
def save_csv(data):
    df = pd.DataFrame(data, columns=["Title", "Company", "Location", "Link"])
    df.to_csv("jobs.csv", index=False)

def save_pdf(data):
    try:
        import pdfkit
        df = pd.DataFrame(data, columns=["Title", "Company", "Location", "Link"])
        html = df.to_html(index=False)
        pdfkit.from_string(html, "jobs.pdf")
    except:
        pass  # اگر pdfkit نصب نبود فقط CSV ذخیره می‌شود

# تابع اجرای Scraper
def run_scraper(title, count):
    scraper = JobScraper(title, count)
    scraper.open_site()
    scraper.get_jobs()
    scraper.close()

    if scraper.data:
        save_csv(scraper.data)
        save_pdf(scraper.data)
        messagebox.showinfo("موفقیت", f"{len(scraper.data)} شغل ذخیره شد!\nCSV و PDF ساخته شد.")
    else:
        messagebox.showwarning("هشدار", "هیچ شغلی پیدا نشد. ممکن است نیاز به login لینکدین داشته باشید.")

# اجرای Scraper در Thread تا GUI فریز نشه
def start_thread():
    title = title_entry.get()
    count = count_entry.get()
    if not title or not count.isdigit():
        messagebox.showwarning("هشدار", "لطفاً عنوان شغل و تعداد معتبر وارد کنید.")
        return
    threading.Thread(target=run_scraper, args=(title, count)).start()

# ساخت GUI
root = tk.Tk()
root.title("LinkedIn Job Scraper واقعی")
root.geometry("400x220")

tk.Label(root, text="عنوان شغلی:").pack(pady=5)
title_entry = tk.Entry(root, width=40)
title_entry.pack()

tk.Label(root, text="تعداد نتایج:").pack(pady=5)
count_entry = tk.Entry(root, width=40)
count_entry.pack()

tk.Button(root, text="شروع گرفتن شغل‌ها", command=start_thread).pack(pady=20)

root.mainloop()