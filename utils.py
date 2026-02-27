import re

def clean_text(text):
    text = text.replace("–", "-")
    text = re.sub(r"\s+", " ", text)
    return text


def extract_patient_info(text):

    name_pattern = r"(Mr\.|Mrs\.|Ms\.)\s+[A-Za-z\s]+"
    age_gender_pattern = r"(\d+)\s*(years|yrs)?\s*/?\s*(Male|Female)"
    date_pattern = r"\d{2}/\d{2}/\d{4}"

    name = re.search(name_pattern, text)
    age_gender = re.search(age_gender_pattern, text)
    date = re.search(date_pattern, text)

    return {
        "name": name.group() if name else "",
        "age": age_gender.group(1) if age_gender else "",
        "gender": age_gender.group(3) if age_gender else "",
        "date": date.group() if date else ""
    }


def extract_parameters(text):

    parameter_pattern = r"""
    ([A-Za-z\s\(\)]+)
    \s+
    ([\d\.]+)
    \s*
    ([a-zA-Z/%\^0-9]+)?
    \s*
    (\d+\s*-\s*\d+)?
    """

    matches = re.findall(parameter_pattern, text, re.VERBOSE)

    parameters = []

    for match in matches:
        parameters.append({
            "parameter": match[0].strip(),
            "value": match[1],
            "unit": match[2] if match[2] else "",
            "reference_range": match[3] if match[3] else ""
        })

    return parameters