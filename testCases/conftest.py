# testCases/conftest.py
import pytest
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
import allure
from allure_commons.types import AttachmentType
import os


@pytest.fixture(scope="class")
def setup(request):
    # ✅ Use Edge browser (headless for CI)
    edge_options = Options()
    edge_options.add_argument("--headless")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--disable-gpu")

    # Path to your Edge driver (already in repo)
    driver_path = os.path.join(os.getcwd(), "drivers", "msedgedriver.exe")
    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"Edge driver not found at {driver_path}")

    driver = webdriver.Edge(service=EdgeService(driver_path), options=edge_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    request.cls.driver = driver
    yield
    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call' and report.failed:
        try:
            driver = item.cls.driver
            allure.attach(driver.get_screenshot_as_png(),
                          name="screenshot_on_failure",
                          attachment_type=AttachmentType.PNG)
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
