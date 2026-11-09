"""The About page (November 2026): the top bar's "Download" duplicated the
big download button, so it became "About", which opens a page saying why
AgriCare was built, in English and Filipino like the rest of the site."""

from conftest import READABILITY, expect_language


def test_top_bar_links_to_the_about_page(open_page):
    page = open_page()
    about = page.locator("a.top-about")
    assert about.get_attribute("href") == "about.html"
    assert about.inner_text() == "About"
    # The big hero button already downloads; the top bar no longer does.
    assert page.locator(".top-download").count() == 0
    page.click("#lang")
    assert about.inner_text() == "Tungkol"


def test_about_page_says_why_we_built_it(open_page):
    page = open_page(path="about.html")
    assert page.locator("h1").inner_text() == "About AgriCare"
    assert page.locator("h2").first.inner_text() == "Why we built it"
    text = page.locator(".about-text")
    assert text.locator("p").count() == 3
    for words in ("Suarez Farm", "STI College San Jose Del Monte"):
        assert words in text.inner_text()


def test_about_page_speaks_filipino(open_page):
    page = open_page(path="about.html", locale="fil-PH")
    assert page.locator("h1").inner_text() == "Tungkol sa AgriCare"
    expect_language(page, "fil")
    page.click("#lang")
    expect_language(page, "en")
    assert page.title() == "About AgriCare"


def test_language_choice_carries_over(open_page, site_url):
    page = open_page()
    page.click("#lang")
    page.goto(site_url + "about.html")
    assert page.locator("h1").inner_text() == "Tungkol sa AgriCare"


def test_about_page_leads_back_to_the_downloads(open_page):
    page = open_page(path="about.html")
    assert page.locator("a.back").get_attribute("href") == "./"
    assert page.locator("a.get-app").get_attribute("href") == "./#download"


def test_about_page_readable_on_a_small_phone(open_page):
    page = open_page(path="about.html", width=320, height=640)
    assert page.evaluate(READABILITY) == []
    page.click("#lang")
    assert page.evaluate(READABILITY) == []
