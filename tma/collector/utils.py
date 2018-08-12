# -*- coding: UTF-8 -*-

import requests


def save_pdf(url, pdf_name):
    response = requests.get(url)
    with open(pdf_name, "wb") as pdf:
        for content in response.iter_content():
            pdf.write(content)
