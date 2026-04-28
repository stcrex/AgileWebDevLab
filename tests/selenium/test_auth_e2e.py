"""End-to-end flows against a live dev server (see tests/selenium/conftest.py)."""

from __future__ import annotations

from urllib.parse import urlparse

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.selenium


def test_login_happy_path_reaches_exams_list(selenium_live_server: str, driver) -> None:
    driver.get(f"{selenium_live_server}/login")
    wait = WebDriverWait(driver, 15)

    wait.until(EC.presence_of_element_located((By.ID, "email")))
    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys("alice@lab.local")
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys("labdemo123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.title_contains("Exams"))
    path = urlparse(driver.current_url).path.rstrip("/")
    assert path == "/exams" or path.endswith("/exams")
    wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'My exam sessions')]")))


def test_login_wrong_password_shows_error_and_stays_unauthenticated(selenium_live_server: str, driver) -> None:
    driver.get(f"{selenium_live_server}/login")
    wait = WebDriverWait(driver, 15)

    wait.until(EC.presence_of_element_located((By.ID, "email")))
    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys("alice@lab.local")
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys("wrong-password-for-sure")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-danger")))
    assert "invalid" in driver.find_element(By.CSS_SELECTOR, ".alert-danger").text.lower()

    driver.get(f"{selenium_live_server}/exams")
    wait.until(EC.url_contains("/login"))
