import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import shutil
import time
import signal
import pandas as pd
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from spot_deepfakes import clearDirectories, displayOutput
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
import subprocess
import re

def move_files(src_folder, dest_folder):
    files = os.listdir(src_folder)
    # If there are no files, print a message and return
    if not files:
        print("No files to move.")
        return
    # Get the full paths of each file in the source folder
    file_paths = [os.path.join(src_folder, file) for file in files]
    # Find the latest file based on modification time
    latest_file = max(file_paths, key=os.path.getmtime)
    # Construct the destination path for the latest file
    dest_path = os.path.join(dest_folder, os.path.basename(latest_file))
    # Move the latest file to the destination folder
    shutil.move(latest_file, dest_path)
    print(f"Moved latest file: {os.path.basename(latest_file)}")

clearDirectories("C:/Users/mrman/OneDrive/Desktop/Hackathon/DeepFake_1/DeepFake-Spot/input", r"C:/Users/mrman/OneDrive/Desktop/Hackathon/DeepFake_1/DeepFake-Spot/src/buffer" , r"C:/Users/mrman/OneDrive/Desktop/Hackathon/DeepFake_1/DeepFake-Spot/output" )

def download_clip(url, start_time, duration, output_file):
    output_directory = r"C:\Users\mrman\OneDrive\Desktop\Hackathon\DeepFake_1\DeepFake-Spot\input"
    ydl_cmd = [
        "yt-dlp",
        "-g", url
    ]
    result = subprocess.run(ydl_cmd, capture_output=True, text=True)
    print(result)
    video_urls = re.findall(r'https?://.*', result.stdout)
    if video_urls:
            video_url = video_urls[0]

            # Construct the FFmpeg command
            output_path = os.path.join(output_directory, output_file)
            cmd = [
                "ffmpeg",
                "-ss", start_time,
                "-i", video_url,
                "-t", duration,
                "-c:v", "libx264",
                "-c:a", "aac",
                output_path
            ]

            # Run the command
            subprocess.run(cmd)
    else:
        print("Error: Could not find video URL.")
#previous download test line
class SeleniumPhases:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("user-data-dir=/path/to/your/chrome/profile")  # Replace with your actual profile path
        self.driver = webdriver.Chrome(options=chrome_options)
        self.trigger = False
        self.mention_url = None
        self.video_tweets = []
        self.processed_notifications = set()
        self.max_urls = 20

    def load_processed_notifications(self):
        file_path = "processed_notifications.txt"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                notifications = file.read().splitlines()
                self.processed_notifications = set(notifications)

    def save_processed_notifications(self):
        file_path = "processed_notifications.txt"
        with open(file_path, "w") as file:
            for notification in self.processed_notifications:
                file.write(notification + "\n")

    def handle_interrupt(self, signum, frame):
        print("Manual interruption detected. Saving data and closing.")
        self.save_processed_notifications()
        self.phase_4_closing()

    def phase_1_initialize(self):
        # Initialize and log into the website and goes to notification tab - should occur only once.

        self.driver.get("https://x.com")
        time.sleep(1)
        close_button = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='xMigrationBottomBar']"))  # Or By.CSS_SELECTOR
        )
        close_button.click()
        close_ad_button = self.driver.find_element(By.XPATH, '//button[@data-testid="xMigrationBottomBar"]')
        close_ad_button.click()

        signin_present = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[text()="Sign in"]'))
        )

        sign_in_button = self.driver.find_element(By.XPATH, '//span[text()="Sign in"]')
        sign_in_button.click()

        username_present = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'r-30o5oe'))
        )
        username_input = self.driver.find_element(By.CLASS_NAME, 'r-30o5oe')
        username_input.send_keys('@Username') #add your username here

        next_button = self.driver.find_element(By.XPATH, '//span[text()="Next"]')
        next_button.click()

        pwd_present = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        password_input = self.driver.find_element(By.NAME, 'password')
        password_input.send_keys('Password') #add your password here

        login_button = self.driver.find_element(By.XPATH, '//span[text()="Log in"]')
        login_button.click()

        time.sleep(3)



    def phase_2_standby(self):
        c=0
        k=0
        self.trigger = False
        # Stay on the page until the trigger occurs
        while not self.trigger:
            # Your standby logic, e.g., waiting for user input or monitoring conditions
            # Initialize a set to store processed notification URLs
            # Set the maximum number of URLs to store
            notify_url = self.driver.find_element(By.XPATH,'//a[@href="/notifications"]')
            notify_url.click()
            notifs_present = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH,'//div[@data-testid="cellInnerDiv"]//a'))
            )
            notifs=self.driver.find_elements(By.XPATH,'//div[@data-testid="cellInnerDiv"]//a')

            for n in notifs:
                txt = n.text
                if c == 6 * k + 2:
                    print(txt + " ", k)
                    k += 1
                c += 1
                notif_html = n.get_attribute("outerHTML")

                soup = BeautifulSoup(notif_html, 'html.parser')

                status_link = soup.find('a', href=lambda href: href and 'status' in href)
                mention_urls = []

                if status_link:
                    self.mention_url = "https://www.x.com" + str(status_link['href'])

                    # Check if the notification has already been processed
                    if self.mention_url in self.processed_notifications:
                        print(f"Skipping already processed notification: {self.mention_url}")
                        continue
                    else:
                        self.trigger=True
                        break
                    

            # ...

            # Optional: Add a delay to wait before checking for new notifications again
            time.sleep(20)  # Adjust the delay time as needed

    def phase_3_processing(self):
        # Process based on the trigger
        print(self.mention_url)

        self.driver.get(self.mention_url)

        link_present = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/status/"][dir="ltr"]'))
        )

        anchor_tag = self.driver.find_element(By.CSS_SELECTOR, 'a[href*="/status/"][dir="ltr"]')

        self.video_tweets.append(anchor_tag.get_attribute('href'))
        print(self.video_tweets)

        # Add the processed notification URL to the set
        self.processed_notifications.add(self.mention_url)

        # Check if the set exceeds the maximum number of URLs
        if len(self.processed_notifications) > self.max_urls:
            # Remove the oldest URLs to maintain the limit
            oldest_urls = list(self.processed_notifications)[:len(self.processed_notifications) - self.max_urls]
            self.processed_notifications.difference_update(oldest_urls)
        
        download_clip(self.video_tweets[0], '00:00:00', '00:00:15', 'video.mp4')

        time.sleep(10)
        displayOutput(False)
        #Working with the Output Result
        df = pd.read_csv(r'C:/Users/mrman/OneDrive/Desktop/Hackathon/DeepFake_1/DeepFake-Spot/src/predictions.csv')
        classification = df['prediction'].iloc[-1].split()[-1]

        #Finding the Reply Area in the post, typing our result and sending it.
        reply_input = self.driver.find_element(By.XPATH, '//div[@data-testid="tweetTextarea_0"]')
        reply_input.send_keys("the video posted above is ", classification)
        time.sleep(1)
        tweet_button = self.driver.find_element(By.XPATH, '//span[text()="Reply"]')
        tweet_button.click()
        time.sleep(3)

    def phase_4_closing(self):
        try:
            if self.driver:
                # Quit the WebDriver instance
                self.driver.quit()

            quit()

        except WebDriverException:
            # Handle the case where the browser window is already closed
            quit()

        finally:
            # If the script doesn't exit fast enough, try terminating it forcefully
            os._exit(0)


    def run_script(self):
        try:
            self.load_processed_notifications()
            # Register the signal handler for Ctrl+C
            signal.signal(signal.SIGINT, self.handle_interrupt)

            self.phase_1_initialize()

            while not self.trigger:
                self.phase_2_standby()
                self.phase_3_processing()

        except TimeoutException as te:
            print(f"Timeout Exception: {te}")
            print("Manual interruption detected. Saving data and closing.")
            self.save_processed_notifications()
            self.phase_4_closing()
            sys.exit()  # Exit the script

        except KeyboardInterrupt:
            print("Manual interruption detected. Saving data and closing.")
            #self.save_data()
            self.save_processed_notifications()
            sys.exit()
            self.phase_4_closing()
            quit()

        except Exception as e:
            print(f"Exception: {e}")
            # Handle other exceptions

        finally:
            self.save_processed_notifications()
            self.phase_4_closing()
            sys.exit()

# Example usage:
selenium_script = SeleniumPhases()
selenium_script.run_script()