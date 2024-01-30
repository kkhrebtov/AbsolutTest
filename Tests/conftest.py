########################
####  WEB Fixtures  ####
########################
import json
import os
import time
from typing import Dict, Callable

import allure
import pytest
from playwright.sync_api import Browser, BrowserType, BrowserContext


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1600, "height": 900},
        "accept_downloads": True,
    }


@pytest.fixture(scope="session")
def context(
        browser: Browser,
        browser_context_args: Dict,
):

    context = browser.new_context(**browser_context_args, ignore_https_errors=True,
                                  # http_credentials={"username": "admin", "password": "admin"}
                                  )
    context.set_default_timeout(10000)
    context.grant_permissions(["clipboard-read", 'accessibility-events', 'clipboard-write'])
    yield context
    context.close()


@pytest.fixture(scope="session")
def launch_browser(
        browser_type_launch_args: Dict,
        browser_type: BrowserType,
) -> Callable[..., Browser]:
    def launch(**kwargs: Dict) -> Browser:
        launch_options = {
            **browser_type_launch_args, **kwargs}
        browser = browser_type.launch(**launch_options)
        return browser

    return launch


@pytest.fixture
def page(
        # browser_type: BrowserType,
        context: BrowserContext
):
    page = context.new_page()

    page.goto("https://old.absolutins.ru/kupit-strahovoj-polis/strahovanie-zhizni-i-zdorovya/zashchita-ot-virusa/",
              timeout=15000)

    page.on("requestfailed", lambda request: allure.attach(f"""\nURL: {request.url}
    \nFailure: {request.failure}
     \nBody: {json.dumps(request.post_data)}""", name=" !!!!!Request Failure!!!!"))

    yield page
    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.failed or call.excinfo:
        try:
            if any(p in item.fixturenames for p in ["page"]):
                for p in item.funcargs["browser"].contexts[0].pages:
                    ts = time.time() * 1000000
                    screenshot_path = os.path.join(os.getcwd(), f"allure-results/{ts}_screenshot.png")
                    allure.attach(
                        p.screenshot(path=screenshot_path, full_page=True), p.url, allure.attachment_type.PNG
                    )
                    print(f"Screenshot for failed test: file://{screenshot_path}")
            else:
                return  # This test does not use browser and we do need screenshot for it

        except Exception as e:
            print("Exception while screen-shot creation: {}".format(e))
