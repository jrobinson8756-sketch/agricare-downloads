"""The adviser's suggestion (October 2026): move the download page to
Vercel. The page names its Vercel address (the link preview, the address
under the QR code), and its old GitHub Pages address forwards there, so the
QR codes and links shared before the move still work."""

from conftest import SITE

HOME = "https://agricare-suarez.vercel.app/"
OLD = "https://jrobinson8756-sketch.github.io/agricare-downloads/"
# The address Vercel gave first, before the project took its own name.
FIRST = "https://agricare-umber.vercel.app/"


def test_the_page_names_its_vercel_address(open_page):
    page = open_page()
    assert page.locator('meta[property="og:url"]').get_attribute(
        "content") == HOME
    assert page.locator('meta[property="og:image"]').get_attribute(
        "content") == HOME + "logo.png"
    assert page.locator('link[rel="canonical"]').get_attribute(
        "href") == HOME
    assert page.locator(".url").inner_text() == "agricare-suarez.vercel.app"


def _forwards(browser, old):
    """Opens [old] and returns where the page ends up."""
    context = browser.new_context()
    page = context.new_page()
    html = (SITE / "index.html").read_text(encoding="utf-8")

    def serve(route):
        route.fulfill(status=200, content_type="text/html", body=html)

    # Every address answers with the page itself; GitHub's API stays out.
    for address in (OLD, FIRST, HOME):
        page.route(address + "**", serve)
    page.route("https://api.github.com/**", lambda route: route.abort())
    page.goto(old + "?from=qr")
    page.wait_for_url(lambda url: url.startswith(HOME))
    landed = page.url
    context.close()
    return landed


def test_the_old_github_address_forwards_to_vercel(browser):
    # Whatever the old link carried comes along.
    assert _forwards(browser, OLD) == HOME + "?from=qr"


def test_the_first_vercel_address_forwards_too(browser):
    assert _forwards(browser, FIRST) == HOME + "?from=qr"
