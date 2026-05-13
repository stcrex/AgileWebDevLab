"""
Selenium smoke tests for the live StudySync server.

Run the app in one terminal:
    flask --app run.py init-db
    flask --app run.py run

Then run these tests in another terminal:
    RUN_SELENIUM=1 pytest tests/selenium
"""
import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("STUDYSYNC_BASE_URL", "http://127.0.0.1:5000")
pytestmark = pytest.mark.skipif(os.environ.get("RUN_SELENIUM") != "1", reason="Set RUN_SELENIUM=1 to run browser tests")


@pytest.fixture()
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


def do_login(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.NAME, "login-email").send_keys("you@student.uwa.edu.au")
    driver.find_element(By.NAME, "login-password").send_keys("password123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Timetable"))


def test_login_page_loads(driver):
    driver.get(f"{BASE_URL}/login")
    assert "Your campus life" in driver.page_source
    assert "Create Account" in driver.page_source


def test_user_can_login_and_view_timetable(driver):
    do_login(driver)
    assert "CITS3403 Laboratory" in driver.page_source
    assert "Create Event" in driver.page_source


def test_exam_detail_page_has_topics_and_progress(driver):
    do_login(driver)
    driver.get(f"{BASE_URL}/exams/1")
    assert "Revision Progress" in driver.page_source
    assert "SQLAlchemy models" in driver.page_source


def test_ai_planner_chat_returns_reply(driver):
    do_login(driver)
    driver.get(f"{BASE_URL}/ai-planner")
    input_box = driver.find_element(By.ID, "chatText")
    input_box.send_keys("Make me a 2 hour study plan")
    input_box.send_keys(Keys.ENTER)
    WebDriverWait(driver, 8).until(EC.text_to_be_present_in_element((By.ID, "chatMessages"), "STUDY PLAN"))
    assert "Flask" in driver.page_source or "SQLAlchemy" in driver.page_source


def test_group_page_displays_shared_user_data(driver):
    do_login(driver)
    driver.get(f"{BASE_URL}/group")
    assert "Tom Liu" in driver.page_source
    assert "Project Tasks" in driver.page_source
    assert "Common Free Slots" in driver.page_source


def test_messenger_sends_message(driver):
    do_login(driver)
    driver.get(f"{BASE_URL}/messages")
    assert "Messenger" in driver.page_source
    assert "Tom Liu" in driver.page_source
    input_box = driver.find_element(By.ID, "messageBody")
    input_box.send_keys("Selenium demo message")
    input_box.send_keys(Keys.ENTER)
    WebDriverWait(driver, 8).until(EC.text_to_be_present_in_element((By.ID, "messageThread"), "Selenium demo message"))



def test_group_chat_sends_message(driver):
    do_login(driver)
    driver.get(f"{BASE_URL}/group-chat")
    assert "Group Chat" in driver.page_source
    input_box = driver.find_element(By.ID, "groupChatBody")
    input_box.send_keys("Selenium group chat update")
    input_box.send_keys(Keys.ENTER)
    WebDriverWait(driver, 8).until(EC.text_to_be_present_in_element((By.ID, "groupChatThread"), "Selenium group chat update"))



def test_profile_page_ajax_save(driver):
    do_login(driver)
    driver.get(f"{BASE_URL}/profile")
    assert "My Student Profile" in driver.page_source
    bio = driver.find_element(By.ID, "profile-bio")
    bio.clear()
    bio.send_keys("Selenium updated profile bio")
    driver.find_element(By.ID, "ajax-save-profile").click()
    WebDriverWait(driver, 8).until(EC.text_to_be_present_in_element((By.ID, "profile-save-status"), "Saved with AJAX"))


def test_students_directory_search(driver):
    do_login(driver)
    driver.get(f"{BASE_URL}/students")
    assert "Student Profiles" in driver.page_source
    search = driver.find_element(By.ID, "student-search")
    search.send_keys("Frontend")
    time.sleep(0.3)
    assert "Tom Liu" in driver.page_source


def test_logout_page_confirms_before_signing_out(driver):
    do_login(driver)
    driver.get(f"{BASE_URL}/logout")
    assert "Log out of StudySync" in driver.page_source
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Welcome back"))
