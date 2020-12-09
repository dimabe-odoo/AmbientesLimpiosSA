import re

class RutHelper:

    @staticmethod
    def format_rut(rut):
        rut = re.sub('\D+(?!$)', '', rut)
        return rut[:-1]+'-'+rut[-1]