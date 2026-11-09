"""The panel's note (consult, October 2026): AgriCare needs a downloading
platform, a website where the APKs are downloaded. These drive the page in
Chrome at a phone's size: the buttons get the newest APKs, the page speaks
the phone's language, and it still works when GitHub doesn't answer."""

from conftest import APPS, READABILITY, expect_language, release

LATEST = ("https://github.com/jrobinson8756-sketch/agricare-downloads/"
          "releases/latest/download/")


def _button(page, app):
    return page.locator(f'[data-app="{app}"] a.download')


def _meta(page, app):
    return page.locator(f'[data-app="{app}"] .meta')


def test_buttons_point_to_the_latest_release(open_page):
    page = open_page()
    for app in APPS:
        assert _button(page, app).get_attribute("href") == \
            f"{LATEST}agricare-{app}.apk"


def test_farmer_card_comes_first_and_largest(open_page):
    page = open_page()
    assert page.locator("[data-app]").first.get_attribute("data-app") == \
        "farmer"
    farmer = _button(page, "farmer").bounding_box()
    admin = _button(page, "admin").bounding_box()
    assert farmer["height"] > admin["height"]


HEADLINE = "Know what your farm needs, every day."
HEADLINE_FIL = "Alamin ang kailangan ng bukid mo, araw-araw."


def test_opens_in_filipino_on_a_filipino_phone(open_page):
    assert open_page(locale="fil-PH").locator("h1").inner_text() == \
        HEADLINE_FIL
    assert open_page(locale="en-US").locator("h1").inner_text() == HEADLINE


def test_language_button_switches_every_text(open_page):
    page = open_page()
    expect_language(page, "en")
    page.click("#lang")
    expect_language(page, "fil")
    assert page.evaluate("document.documentElement.lang") == "fil"
    page.click("#lang")
    expect_language(page, "en")


def test_toggle_works_without_storage(open_page):
    # A private tab or blocked site data: storage throws.
    page = open_page(init_script="""
        Object.defineProperty(window, 'localStorage', {
          get() { throw new Error('storage blocked'); }
        });""")
    page.click("#lang")
    assert page.locator("h1").inner_text() == HEADLINE_FIL


# The redesign (November 2026): laid out like a product landing page, a
# big headline over four feature cards, in AgriCare's own colors.
def test_hero_button_jumps_to_the_downloads(open_page):
    page = open_page()
    assert page.locator("a.hero-cta").get_attribute("href") == "#download"
    assert page.locator('#download [data-app="farmer"]').count() == 1


def test_four_feature_cards_say_what_the_app_does(open_page):
    page = open_page()
    titles = page.locator(".feature h3")
    assert titles.all_inner_texts() == [
        "Scan a leaf", "Check your soil", "Weather advice", "Ask for help"]
    page.click("#lang")
    assert titles.all_inner_texts() == [
        "Mag-scan ng dahon", "Tingnan ang lupa", "Payo tungkol sa panahon",
        "Humingi ng tulong"]


def test_keeps_agricare_green(open_page):
    # The app's leaf green (lib/theme/app_theme.dart), not the reference
    # site's colors.
    page = open_page()
    green = "rgb(62, 112, 0)"
    assert page.eval_on_selector(
        ".hero", "e => getComputedStyle(e).backgroundColor") == green
    assert page.eval_on_selector(
        '[data-app="farmer"] a.download',
        "e => getComputedStyle(e).backgroundColor") == green


def test_shows_version_and_size_from_github(open_page):
    page = open_page()
    assert _meta(page, "farmer").inner_text() == "v1.0.0 · 40 MB"


def test_works_when_github_is_unreachable(open_page):
    page = open_page(api=None)
    for app in APPS:
        button = _button(page, app)
        assert button.get_attribute("href") == f"{LATEST}agricare-{app}.apk"
        assert button.get_attribute("aria-disabled") is None
        meta = _meta(page, app).text_content()
        for junk in ("undefined", "NaN", "MB"):
            assert junk not in meta


def test_missing_apk_is_not_offered(open_page):
    page = open_page(api=release("farmer"))
    for app in ("admin", "developer"):
        assert _meta(page, app).inner_text() == "Not available yet"
        assert _button(page, app).get_attribute("aria-disabled") == "true"
        assert _button(page, app).get_attribute("href") is None
    assert _button(page, "farmer").get_attribute("aria-disabled") is None
    # Said in the phone's language too.
    page.click("#lang")
    assert _meta(page, "admin").inner_text() == "Wala pa"


def test_no_release_yet(open_page):
    # GitHub answers 404 before the first release is published.
    page = open_page(api=404)
    for app in APPS:
        assert _meta(page, app).inner_text() == "Not available yet"
        assert _button(page, app).get_attribute("href") is None


def test_install_help_covers_phone_warnings(open_page):
    # Android warns about an APK from outside the Play Store, and Messenger's
    # own browser may not download it: the page says what to tap, so a
    # farmer doesn't stop at the first scary message.
    page = open_page()
    help = page.locator(".warnings").inner_text()
    for words in ("Download anyway", "Install anyway", "Open in Chrome"):
        assert words in help
    page.click("#lang")
    help = page.locator(".warnings").inner_text()
    assert "Ligtas" in help
    for words in ("Download anyway", "Install anyway", "Open in Chrome"):
        assert words in help


def test_install_steps_and_qr(open_page):
    page = open_page()
    assert page.locator("ol.steps li").count() == 4
    assert page.locator('img[src="qr.svg"]').get_attribute("alt")
    assert "Suarez Farm" in page.locator("footer").inner_text()


def test_readable_on_a_small_phone(open_page):
    page = open_page(width=320, height=640)
    assert page.evaluate(READABILITY) == []
    page.click("#lang")
    assert page.evaluate(READABILITY) == []
    # The cards' "not available" state too.
    page = open_page(width=320, height=640, api=release("farmer"))
    assert page.evaluate(READABILITY) == []
