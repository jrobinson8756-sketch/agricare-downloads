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
    status (int), or None for no connection. [path] opens another page of
    the site, such as "about.html"."""
    contexts = []

    def _open(width=360, height=800, locale="en-US", api=release(*APPS),
              init_script=None, path=""):
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
        page.goto(site_url + path)
        # The page marks <html data-release> once GitHub has answered (or
        # not), so the tests see the finished cards. A page without the
        # cards has no mark, so it counts as finished at once.
        page.wait_for_function(
            "document.documentElement.dataset.release !== 'loading'")
        return page

    yield _open
    for context in contexts:
        context.close()


def expect_language(page, lang):
    """Every translated text shows in [lang] ("en" or "fil")."""
    shown = page.eval_on_selector_all(
        "[data-fil]",
        f"els => els.map(e => [e.textContent.trim(), e.dataset.{lang}])")
    assert shown, "no translated text found"
    for text, wanted in shown:
        assert text == wanted


# Text at least 13 px and 4.5:1, buttons and links at least 48 dp, and no
# sideways scrolling: the checks every page of the site passes.
READABILITY = r"""
() => {
  const problems = [];
  const channel = v => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  };
  const luminance = ([r, g, b]) =>
    0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
  const rgba = s => (s.match(/[\d.]+/g) || []).map(Number);
  const backgroundOf = el => {
    for (let e = el; e; e = e.parentElement) {
      const c = rgba(getComputedStyle(e).backgroundColor);
      if (c.length >= 3 && (c.length < 4 || c[3] > 0)) return c.slice(0, 3);
    }
    return [255, 255, 255];
  };
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const text = n.textContent.trim();
    if (!text) continue;
    const el = n.parentElement;
    const box = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    if (box.width === 0 || box.height === 0 || style.visibility === 'hidden') continue;
    const size = parseFloat(style.fontSize);
    if (size < 13) problems.push(`"${text}" is ${size}px`);
    const fg = rgba(style.color);
    if (fg.length === 4 && fg[3] < 1) problems.push(`"${text}" is see-through`);
    const a = luminance(fg.slice(0, 3)), b = luminance(backgroundOf(el));
    const ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
    if (ratio < 4.5) problems.push(`"${text}" has contrast ${ratio.toFixed(2)}`);
  }
  for (const el of document.querySelectorAll('a, button')) {
    const box = el.getBoundingClientRect();
    if (box.width === 0) continue;
    if (box.width < 48 || box.height < 48) {
      problems.push(`"${el.textContent.trim()}" is ${box.width}x${box.height}`);
    }
  }
  const width = document.documentElement.scrollWidth;
  if (width > window.innerWidth) problems.push(`the page is ${width}px wide`);
  return problems;
}
"""
