# coding: utf-8
def test_get_chrome_options():
    from pycharmers.utils import get_chrome_options
    # browser == False (default)
    op = get_chrome_options(browser=False)
    op.arguments
    # ['--no-sandbox',
    # '--ignore-certificate-errors',
    # '--disable-dev-shm-usage',
    # '--headless']
    op.experimental_options
    # {}
    # browser == True
    op = get_chrome_options(browser=True)
    op.arguments
    # ['--no-sandbox',
    # '--ignore-certificate-errors',
    # '--disable-dev-shm-usage',
    # '--kiosk-printing']
    op.experimental_options
    # {'prefs': {'profile.default_content_settings.popups': 1,
    # 'download.default_directory': '/Users/iwasakishuto/.pycharmers',
    # 'directory_upgrade': True}}

def test_try_find_element():
    from pycharmers.utils import get_driver, try_find_element
    with get_driver() as driver:
        driver.get("https://www.google.com/")
        e = try_find_element(driver=driver, by="tag name", identifier="img")
    # Succeeded to locate element with tag name=img

