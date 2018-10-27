from PyQt5.QtGui import QValidator


class AngleValidator(QValidator):
    def __init__(self):
        super(AngleValidator, self).__init__()

    def validate(self, p_str, p_int):
        if p_str == "":
            return (QValidator.Intermediate, p_str, p_int)
        if p_int == 1:
            if p_str in ["+", "-"]:
                return (QValidator.Intermediate, p_str, p_int)
        try:
            value = float(p_str)
        except TypeError:
            return (QValidator.Invalid, p_str, p_int)
        except ValueError:
            return (QValidator.Invalid, p_str, p_int)
        if value >= 360.0 or value < 0.0:
            return (QValidator.Intermediate, p_str, p_int)
        return (QValidator.Acceptable, p_str, p_int)

    def fixup(self, p_str):
        try:
            value = float(p_str)
        except ValueError:
            return "0.0"
        while value >= 360.0 or value < 0.0:
            if value >= 360.0:
                value -= 360.0
            if value < 0.0:
                value += 360.0
        return str(value)