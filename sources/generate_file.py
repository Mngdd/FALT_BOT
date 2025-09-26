import os
import re

from docxtpl import DocxTemplate


def parse_string(s):
    pattern = r'^(Пользователь|Дата|Комментарий)\s*:\s*(.*?)(?=\n\w+\s*:|\Z)'
    matches = re.findall(pattern, s, re.DOTALL | re.MULTILINE)
    result = [i[1] for i in matches]
    return result


async def generate_file(text):
    doc = DocxTemplate(f"{os.getcwd()}\\sources\studyroom_booked_template.docx")
    username, date, comment = parse_string(text)
    context = {
        "username": username,
        "date": date,
        "comment": comment
    }
    doc.render(context)
    path = f"{os.getcwd()}\\files\Бронирование_боталки_{''.join([i if i.isalnum() else '_' for i in date]).replace('___', '_')}.docx"
    doc.save(path)
    return path
