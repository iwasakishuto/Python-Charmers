# coding: utf-8
def test__mk_func():
    from pycharmers.utils.templates import _mk_func
    func = _mk_func(fn="base.html", name="base_html")

def test_base_html():
    from pycharmers.utils.templates import base_html
    base_html()

def test_fonts_html():
    from pycharmers.utils.templates import fonts_html
    fonts_html()

def test_render_template():
    import matplotlib
    from pycharmers.utils import render_template
    render_template(
        template_name_or_string="fonts.html", 
        context={"fonts": sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))}
    )

def test_style_html():
    from pycharmers.utils.templates import style_html
    style_html()

