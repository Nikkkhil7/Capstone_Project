import pytest
import allure
from allure_commons.types import AttachmentType
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.firefox import GeckoDriverManager
import os


def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="firefox",
        help="Browser to run tests on: firefox or edge"
    )


@pytest.fixture(scope="class")
def setup(request):
    browser_name = request.config.getoption("browser").lower()

    # ✅ Firefox (for GitHub Actions)
    if browser_name == "firefox":
        from selenium.webdriver.firefox.options import Options
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-gpu")
        firefox_options.binary_location = "/usr/bin/firefox"  # Use system Firefox
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=firefox_options
        )


    # ✅ Edge (for local use only, not in CI)
    elif browser_name == "edge":
        edge_driver_path = "./drivers/msedgedriver.exe"
        if not os.path.exists(edge_driver_path):
            raise FileNotFoundError("Edge driver not found at ./drivers/msedgedriver.exe")
        service = EdgeService(executable_path=edge_driver_path)
        driver = webdriver.Edge(service=service)

    else:
        raise pytest.UsageError("--browser option is invalid. Choose from firefox or edge")

    driver.implicitly_wait(10)
    driver.maximize_window()
    request.cls.driver = driver
    yield
    driver.quit()


# ✅ Attach screenshots to Allure report on test failure
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        try:
            driver = getattr(item.cls, "driver", None)
            if driver:
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="screenshot_on_failure",
                    attachment_type=AttachmentType.PNG
                )
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
