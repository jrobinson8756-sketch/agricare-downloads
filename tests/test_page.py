"""The panel's note (consult, October 2026): AgriCare needs a downloading
platform, a website where the APKs are downloaded. These drive the page in
Chrome at a phone's size: the buttons get the newest APKs, the page speaks
the phone's language, and it still works when GitHub doesn't answer."""

from conftest import APPS, release

LATEST = ("https://github.com/jrobinson8756-sketch/agricare-downloads/"
          "releases/latest/download/")


def _button(page, app):
    return page.locator(f'[data-app="{app}"] a.download')


def _meta(page, app):
    return page.locator(f'[data-app="{app}"] .meta')


def _expect_language(page, lang):
    """Every translated text shows in [lang] ("en" or "fil")."""
    shown = page.eval_on_selector_all(
        "[data-fil]",
        f"els => els.map(e => [e.textContent.trim(), e.dataset.{lang}])")
    assert shown, "no translated text found"
    for text, wanted in shown:
        assert text == wanted


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


def test_opens_in_filipino_on_a_filipino_phone(open_page):
    assert open_page(locale="fil-PH").locator("h1").inner_text() == \
        "I-download ang AgriCare"
    assert open_page(locale="en-US").locator("h1").inner_text() == \
        "Download AgriCare"


def test_language_button_switches_every_text(open_page):
    page = open_page()
    _expect_language(page, "en")
    page.click("#lang")
    _expect_language(page, "fil")
    assert page.evaluate("document.documentElement.lang") == "fil"
    page.click("#lang")
    _expect_language(page, "en")


def test_toggle_works_without_storage(open_page):
    # A private tab or blocked site data: storage throws.
    page = open_page(init_script="""
        Object.defineProperty(window, 'localStorage', {
          get() { throw new Error('storage blocked'); }
        });""")
    page.click("#lang")
    assert page.locator("h1").inner_text() == "I-download ang AgriCare"


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


_READABILITY = r"""
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


def test_readable_on_a_small_phone(open_page):
    page = open_page(width=320, height=640)
    assert page.evaluate(_READABILITY) == []
    page.click("#lang")
    assert page.evaluate(_READABILITY) == []
    # The cards' "not available" state too.
    page = open_page(width=320, height=640, api=release("farmer"))
    assert page.evaluate(_READABILITY) == []
