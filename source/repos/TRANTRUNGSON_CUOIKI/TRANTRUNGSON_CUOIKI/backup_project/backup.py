import os
import shutil
import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import schedule
import time

# Load environment variables from .env file
load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
BACKUP_DIR = os.getenv("BACKUP_DIR")

def backup_database():
    """Tìm kiếm và sao lưu các file database (.sql hoặc .sqlite3)."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    success_files = []
    failed_files = []

    # Đảm bảo thư mục backup tồn tại
    os.makedirs(BACKUP_DIR, exist_ok=True)

    for filename in os.listdir('.'):  # Tìm kiếm trong thư mục hiện tại
        if filename.endswith(".sql") or filename.endswith(".sqlite3"):
            source_path = filename
            destination_path = os.path.join(BACKUP_DIR, f"{filename}_{timestamp}")
            try:
                shutil.copy2(source_path, destination_path)  # copy2 giữ lại metadata
                success_files.append(filename)
                print(f"Đã backup thành công: {filename} -> {destination_path}")
            except Exception as e:
                failed_files.append(filename)
                print(f"Lỗi khi backup {filename}: {e}")

    return success_files, failed_files

def send_email(subject, body):
    """Gửi email thông báo."""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Đã gửi email thông báo thành công.")
        return True
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")
        return False

def main():
    """Thực hiện backup và gửi email thông báo."""
    success_files, failed_files = backup_database()

    if success_files or failed_files:
        subject = f"Kết quả Backup Database ngày {datetime.date.today()}"
        body = ""
        if success_files:
            body += "Các file database đã được backup thành công:\n"    
            for file in success_files:
                body += f"- {file}\n"
        if failed_files:
            body += "\nCác file database backup thất bại:\n"
            for file in failed_files:
                body += f"- {file}\n"

        send_email(subject, body)
    else:
        print("Không tìm thấy file database nào để backup.")
        send_email(f"Thông báo Backup Database ngày {datetime.date.today()}",
                   "Không có file database (.sql hoặc .sqlite3) nào được tìm thấy để backup.")

def run_daily_backup():
    """Lên lịch chạy backup hàng ngày vào lúc 00:00."""
    schedule.every().day.at("12:00").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("Chương trình backup database hàng ngày đã được khởi động.")
    run_daily_backup()