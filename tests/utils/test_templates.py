# coding: utf-8
def test_def_html():









def test_render_template():
    import matplotlib
    from pycharmers.utils import render_template
    render_template(
        template_name_or_string="fonts.html", 
        context={"fonts": sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))}
    )
    #     <h1>Available Fonts</h1>
    #     <ul>
    #     <li>.Aqua Kana: <span style='font-family:.Aqua Kana; font-size: 2em;'>.Aqua Kana</li>
    #     <li>.Arabic UI Display: <span style='font-family:.Arabic UI Display; font-size: 2em;'>.Arabic UI Display</li>
    #     : 

