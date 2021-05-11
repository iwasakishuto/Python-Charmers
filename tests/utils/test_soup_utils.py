# coding: utf-8
def test_find_all_target_text():
    from bs4 import BeautifulSoup
    from pycharmers.utils import find_all_target_text
    section = BeautifulSoup("""
    <div>
      <p class="lang en">Hello</p>
      <p class="lang zh-CN">你好</p>
      <p class="lang es">Hola</p>
      <p class="lang fr">Bonjour</p>
      <p class="lang ja">こんにちは</p>
    </div>
    """)
    find_all_target_text(soup=section, name="p", class_="lang", joint=", ")
    # 'Hello, 你好, Hola, Bonjour, こんにちは'
    find_all_target_text(soup=section, name="p", class_="es", joint=", ")
    # 'Hola'

def test_find_target_id():
    from bs4 import BeautifulSoup
    from pycharmers.utils import find_target_id
    section = BeautifulSoup("""
    <h2>IMAGE</h2>
    <div>
      <img id="apple-touch-icon" src="https://iwasakishuto.github.io/images/apple-touch-icon/Python-Charmers.png">
    </div>
    """)
    find_target_id(soup=section, name="img", key="id")
    # 'apple-touch-icon'
    find_target_id(soup=section, name="img", key="src")
    # 'https://iwasakishuto.github.io/images/apple-touch-icon/Python-Charmers.png'

def test_find_target_text():
    from bs4 import BeautifulSoup
    from pycharmers.utils import find_target_text
    section = BeautifulSoup("""
    <h2>AAA</h2>
    <div> <p>aaaaaaaaaaaaaaaaaaaaaa</p></div>
    """)
    find_target_text(soup=section, name="div")
    # 'aaaaaaaaaaaaaaaaaaaaaa'
    find_target_text(soup=section, name="div", strip=False)
    # ' aaaaaaaaaaaaaaaaaaaaaa '
    find_target_text(soup=section, name="divdiv", default="not found")
    # 'not found'

def test_group_soup_with_head():
    from bs4 import BeautifulSoup
    from pycharmers.utils import group_soup_with_head
    section = BeautifulSoup("""
    <h2>AAA</h2>
    <div>
      <p>aaaaaaaaaaaaaaaaaaaaaa</p>
    </div>
    <h2>BBB</h2>
    <div>
      <p>bbbbbbbbbbbbbbbbbbbbbb</p>
    </div>
    """)
    sections = group_soup_with_head(section, name="h2")
    len(sections)
    # 2
    sections
    # [<section><h2>AAA</h2><div>
    # <p>aaaaaaaaaaaaaaaaaaaaaa</p>
    # </div>
    # </section>,
    # <section><h2>BBB</h2><div>
    # <p>bbbbbbbbbbbbbbbbbbbbbb</p>
    # </div>
    # </section>]

def test_replace_soup_tag():
    from bs4 import BeautifulSoup
    from pycharmers.utils import replace_soup_tag
    section = BeautifulSoup("""
    <h2>AAA</h2>
    <div>
      <p>aaaaaaaaaaaaaaaaaaaaaa</p>
    </div>
    <h3>BBB</h3>
    <div>
      <p>bbbbbbbbbbbbbbbbbbbbbb</p>
    </div>
    """)
    section = replace_soup_tag(soup=section, old_name="h3", new_name="h2")
    section
    # <html><body><h2>AAA</h2>
    # <div>
    # <p>aaaaaaaaaaaaaaaaaaaaaa</p>
    # </div>
    # <h2>BBB</h2>
    # <div>
    # <p>bbbbbbbbbbbbbbbbbbbbbb</p>
    # </div>
    # </body></html>

def test_split_section():
    from bs4 import BeautifulSoup
    from pycharmers.utils import split_section
    section = BeautifulSoup("""
    <section>
      <div>
        <h2>Title</h2>
        <div>
        <p>aaaaaaaaaaaaaaaaaaaaaa</p>
        <div>
        <img/>
        </div>
        <p>bbbbbbbbbbbbbbbbbbbbbb</p>
        </div>
      </div>
    </section>
    """)
    len(split_section(section, name="img"))
    # 3
    split_section(section, name="img")
    # [<section>
    # <div>
    # <h2>Title</h2>
    # <div>
    # <p>aaaaaaaaaaaaaaaaaaaaaa</p>
    # <div>
    # </div></div></div></section>,
    # <img/>,
    # <p>bbbbbbbbbbbbbbbbbbbbbb</p>
    # ]

def test_str2soup():
    from pycharmers.utils import str2soup
    string = "<title>Python-Charmers</title>"
    type(string)
    # str
    soup = str2soup(string)
    soup
    # <title>Python-Charmers</title>
    type(soup)
    # bs4.BeautifulSoup
    from bs4 import BeautifulSoup
    BeautifulSoup(string)
    # <html><head><title>Python-Charmers</title></head></html>

