@staticmethod
def parse_code(code: str) -> list:
    parsed_code = {"subject" : "E1",
                   "topic" : "zzz",
                   "section" : "ZG",
                   "number" : "999999"}
    parsed_code["subject"] = code[0:2]
    parsed_code["topic"] = code[2:5]
    parsed_code["section"] = code[5:7]
    parsed_code["number"] = code[7:13]
    return parsed_code