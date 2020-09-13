class C3():
    """ Color Code Converter """
    def __init__(self, color, max_val=1, color_code=None):
        self.color = color
        self.max_val = max_val
        self._init(color_code=color_code)

    @property
    def _supported_color_codes(self):
        return ["rgba", "rgb", "hex"]

    def _init(self, color_code=None):
        if (color_code is None) or (color_code not in self._supported_color_codes):
            color_code = self.detect_color_code(color)
        self.color_code = color_code

    def detect_color_code(self, color):
        if isinstance(color, str):
            color_code = "hex"
        elif isinstance(color, tuple) or isinstance(color, list):
            color_code = {
                3: "rgb",
                4: "rgba",
            }.get(len(color))
        else:
            raise TypeError(f"{toBLUE('color')} must be {toGREEN('str')} or {toGREEN('tuple')}, not {toRED(type())}")
        return color_code

    @staticmethod
    def rgb2hex(rgb, max_val=1):
        return "#"+"".join([format(int(255/max_val*e), '02x') for e in rgb]).upper()

    @staticmethod
    def rgba2rgb(rgba, max_val=1):
        alpha = rgba[-1]
        rgb = rgba[:-1]
        type_ = int if max_val==255 else float
        # compute the color as alpha against white
        return tuple([type_(alpha*e+(1-alpha)*max_val) for e in rgb])

    @staticmethod
    def hex2rgb(hex, max_val=1):
        tuple([int(hex[-6:][i*2:(i+1)*2], 16)/255*max_val for i in range(3)])

def choose_text_color(color, ctype="rgb", max_val=1):
    color = {
        "rgb"  : color,
        "hex"  : 1,
        "rgba" : rgba2rgb
    }.get(ctype)
    # Ref: WCAG (https://www.w3.org/TR/WCAG20/)
    R,G,B = [e/max_val for e in rgb]
    # Relative Brightness BackGround.
    Lbg = 0.2126*R + 0.7152*G + 0.0722*B

    Lw = 1 # Relative Brightness of White
    Lb = 0 # Relative Brightness of Black

    Cw = (Lw + 0.05) / (Lbg + 0.05)
    Cb = (Lbg + 0.05) / (Lb + 0.05)
    return (0,0,0) if Cb>Cw else (max_val,max_val,max_val)