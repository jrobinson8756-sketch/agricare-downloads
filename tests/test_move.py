"""The adviser's suggestion (October 2026): move the download page to
Vercel. The page names its Vercel address (the link preview, the address
under the QR code), and its old GitHub Pages address forwards there, so the
QR codes and links shared before the move still work."""

from conftest import SITE

HOME = "https://agricare-umber.vercel.app/"
OLD = "https://jrobinson8756-sketch.github.io/agricare-downloads/"


def test_the_page_names_its_vercel_address(open_page):
    page = open_page()
    assert page.locator('meta[property="og:url"]').get_attribute(
        "content") == HOME
    assert page.locator('meta[property="og:image"]').get_attribute(
        "content") == HOME + "logo.png"
    assert page.locator('link[rel="canonical"]').get_attribute(
        "href") == HOME
    assert page.locator(".url").inner_text() == "agricare-umber.vercel.app"


def test_the_old_github_address_forwards_to_vercel(browser):
    context = browser.new_context()
    page = context.new_page()
    html = (SITE / "index.html").read_text(encoding="utf-8")

    def serve(route):
        route.fulfill(status=200, content_type="text/html", body=html)

    # Both addresses answer with the page itself; GitHub's API stays out.
    page.route(OLD + "**", serve)
    page.route(HOME + "**", serve)
    page.route("https://api.github.com/**", lambda route: route.abort())
    page.goto(OLD + "?from=qr")
    page.wait_for_url(lambda url: url.startswith(HOME))
    # Whatever the old link carried comes along.
    assert page.url == HOME + "?from=qr"
    context.close()
