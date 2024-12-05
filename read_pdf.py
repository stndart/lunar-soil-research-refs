# Для считывания PDF
import PyPDF2
# Для анализа структуры PDF и извлечения текста
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# Для извлечения текста из таблиц в PDF
import pdfplumber
# Для извлечения изображений из PDF
from PIL import Image
from pdf2image import convert_from_path
# Для удаления дополнительно созданных файлов
import os

# Создаём функцию для извлечения текста

def text_extraction(element):
    # Извлекаем текст из вложенного текстового элемента
    line_text = element.get_text()
    
    # Находим форматы текста
    # Инициализируем список со всеми форматами, встречающимися в строке текста
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            # Итеративно обходим каждый символ в строке текста
            for character in text_line:
                if isinstance(character, LTChar):
                    # Добавляем к символу название шрифта
                    line_formats.append(character.fontname)
                    # Добавляем к символу размер шрифта
                    line_formats.append(character.size)
    # Находим уникальные размеры и названия шрифтов в строке
    format_per_line = list(set(line_formats))
    
    # Возвращаем кортеж с текстом в каждой строке вместе с его форматом
    return (line_text, format_per_line)

def extract_lines_from_pdf(pdf_path):
    # создаём объект файла PDF
    pdfFileObj = open(pdf_path, 'rb')
    # создаём объект считывателя PDF
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)

    # Создаём словарь для извлечения текста из каждого изображения
    text_per_page = {}
    # Извлекаем страницы из PDF
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        
        # Инициализируем переменные, необходимые для извлечения текста со страницы
        pageObj = pdfReaded.pages[pagenum]
        page_text = []
        line_format = []
        text_from_images = []
        text_from_tables = []
        page_content = []
        # Инициализируем количество исследованных таблиц
        table_num = 0
        first_element= True
        table_extraction_flag= False
        # Открываем файл pdf
        pdf = pdfplumber.open(pdf_path)
        # Находим исследуемую страницу
        page_tables = pdf.pages[pagenum]
        # Находим количество таблиц на странице
        tables = page_tables.find_tables()


        # Находим все элементы
        page_elements = [(element.y1, element) for element in page._objs]
        # Сортируем все элементы по порядку нахождения на странице
        page_elements.sort(key=lambda a: a[0], reverse=True)

        # Находим элементы, составляющие страницу
        for i,component in enumerate(page_elements):
            # Извлекаем положение верхнего края элемента в PDF
            pos= component[0]
            # Извлекаем элемент структуры страницы
            element = component[1]
            
            # Проверяем, является ли элемент текстовым
            if isinstance(element, LTTextContainer):
                # Проверяем, находится ли текст в таблице
                if table_extraction_flag == False:
                    # Используем функцию извлечения текста и формата для каждого текстового элемента
                    (line_text, format_per_line) = text_extraction(element)
                    # Добавляем текст каждой строки к тексту страницы
                    page_text.append(line_text)
                    # Добавляем формат каждой строки, содержащей текст
                    line_format.append(format_per_line)
                    page_content.append(line_text)
                else:
                    # Пропускаем текст, находящийся в таблице
                    pass

        # Создаём ключ для словаря
        dctkey = 'Page_'+str(pagenum)
        # Добавляем список списков как значение ключа страницы
        text_per_page[dctkey]= [page_text, line_format, text_from_images,text_from_tables, page_content]

    # Закрываем объект файла pdf
    pdfFileObj.close()

    # Удаляем созданные дополнительные файлы
    # os.remove('cropped_image.pdf')
    # os.remove('PDF_image.png')

    # Удаляем содержимое страницы
    result = ''.join(text_per_page['Page_0'][4])
    # print(result)

    page_keys = list(text_per_page.keys())
    pages = [text_per_page[pgkey][0] for pgkey in page_keys]

    lines = []
    for page in pages:
        for line in page:
            if line.strip() == '':
                continue
            lines.append(line.strip())
    lines = lines[2:]

    return lines