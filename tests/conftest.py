"""Serves the site folder on localhost and opens it in the installed Chrome,
at a phone's size, with GitHub's release information answered by the test
(never the real network)."""

import functools
import http.server
import json
import pathlib
import threading

import pytest
from playwright.sync_api import sync_playwright

SITE = pathlib.Path(__file__).resolve().parent.parent
API = ("https://api.github.com/repos/jrobinson8756-sketch/agricare-downloads/"
       "releases/latest")
APPS = ("farmer", "admin", "developer")
FORTY_MB = 41943040


def release(*apps, tag="v1.0.0", size=FORTY_MB):
    """What GitHub says about the latest release, with an APK for [apps]."""
    return {
        "tag_name": tag,
        "assets": [{"name": f"agricare-{app}.apk", "size": size}
                   for app in apps],
    }


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def site_url():
    handler = functools.partial(_QuietHandler, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}/"
    server.shutdown()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        chrome = playwright.chromium.launch(channel="chrome")
        yield chrome
        chrome.close()


@pytest.fixture
def open_page(browser, site_url):
    """Opens the page. [api] is GitHub's answer: a release (dict), an HTTP
    status (int), or None for no connection."""
    contexts = []

    def _open(width=360, height=800, locale="en-US", api=release(*APPS),
              init_script=None):
        context = browser.new_context(
            viewport={"width": width, "height": height}, locale=locale)
        contexts.append(context)
        if init_script:
            context.add_init_script(init_script)
        page = context.new_page()

        def answer(route):
            if api is None:
                route.abort()
            elif isinstance(api, int):
                route.fulfill(status=api, content_type="application/json",
                              body="{}")
            else:
                route.fulfill(status=200, content_type="application/json",
                              body=json.dumps(api))

        page.route("https://api.github.com/**", answer)
        page.goto(site_url)
        # The page marks <html data-release> once GitHub has answered (or
        # not), so the tests see the finished cards.
        page.wait_for_function(
            "document.documentElement.dataset.release !== 'loading'")
        return page

    yield _open
    for context in contexts:
        context.close()
