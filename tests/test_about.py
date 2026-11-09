"""The About page (November 2026): the top bar's "Download" duplicated the
big download button, so it became "About", which opens a page saying why
AgriCare was built, in English and Filipino like the rest of the site. Its
words follow the team's capstone paper: the farm's problems from the client
interview (Project Context), what AgriCare does (Objectives), its three
apps (Scope) and the paper's own title."""

from conftest import READABILITY, expect_language

PAPER_TITLE = ("AgriCare: An IoT-Based Mobile System for Crop Health "
               "Monitoring Using Image Recognition and Soil Quality Analysis "
               "at Suarez Farm")


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
    assert page.locator("h2").all_inner_texts() == [
        "Why we built it", "What AgriCare does", "Who it's for",
        "Our capstone"]
    text = page.locator(".about-text").inner_text()
    for words in ("Suarez Farm", "STI College San Jose Del Monte"):
        assert words in text


def test_about_page_follows_the_paper(open_page):
    page = open_page(path="about.html")
    text = page.locator(".about-text")
    # The paper's objectives, as things a farmer does.
    assert text.locator("ol.steps > li strong").all_inner_texts() == [
        "Scan a leaf.", "Check the soil.", "Plan around the weather.",
        "Get alerts."]
    # Its Scope: one app for each kind of user.
    assert text.locator("ul.who > li strong").all_inner_texts() == [
        "Farmer", "Admin", "Developer"]
    assert text.locator("cite").inner_text() == PAPER_TITLE
    # The title stays as the paper has it, in English, on the Filipino page.
    page.click("#lang")
    expect_language(page, "fil")
    assert text.locator("cite").inner_text() == PAPER_TITLE
    assert text.locator("cite").get_attribute("lang") == "en"


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
