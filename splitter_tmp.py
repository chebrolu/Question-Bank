import types, sys, os, re, io
from binascii import b2a_hex
from PIL import Image

from pylatexenc.latexencode import utf8tolatex

from pdf2image import convert_from_path

from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import (
	DictionaryObject,
	NumberObject,
	FloatObject,
	NameObject,
	TextStringObject,
	ArrayObject
)

from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import *

question_regex_patterns = ['^\s*\d+\.\s', '^\s*\d+\.\)', '^\s*\d+\)', \
							'^\s*[a-zA-Z]\.\s', '^\s*[a-zA-Z]\.\)', '^\s*[a-zA-Z]\)']

def get_PDF_layout(pdf_path):
	try:
		document = open(pdf_path, 'rb')
	except Exception as e:
		return "Error reading file" + format(e)
	rsrcmgr = PDFResourceManager()
	laparams = LAParams()
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	layout = []
	for page in PDFPage.get_pages(document):
		interpreter.process_page(page)
		layout.append(device.get_result())
	return layout

def get_pages_pdfminer(pdf_path):
	try:
		document = open(pdf_path, 'rb')
	except Exception as e:
		return "Error reading file" + format(e)
	rsrcmgr = PDFResourceManager()
	laparams = LAParams()
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	return PDFPage.get_pages(document)

def get_pages_pdf2image(pdf_path):
	pages = convert_from_path(pdf_path)
	return pages

def page_to_image(page, img_path = 'out.jpg', format = 'JPEG'):
	page.save(img_path, format)

def get_image_from_page(page, x1, x2, y1, y2, w, h, img_path = 'test.jpg'):
	page_to_image(page, img_path)
	im = Image.open(img_path)
	W, H = im.size
	crop_rectangle = (x1*W/w, (h-y2)*H/h, x2*W/w, (h-y1)*H/h)
	cropped_image = im.crop(crop_rectangle)
	cropped_image.show()

def get_text_from_box(layout, x1, x2, y1, y2):
	text = ""
	if (y1 > y2):
		temp = y2
		y2 = y1
		y1 = temp
	if isinstance(layout, LTTextLineHorizontal):
		if ((layout.bbox[1] + layout.bbox[3])/2.0 <= y2 and (layout.bbox[1] + layout.bbox[3])/2.0 >= y1):
			return str(layout.get_text().encode('utf8'))
		else:
			return ""
	elif not hasattr(layout, '__iter__'):
		return ""
	else:
		for node in layout:
			text = text + str(get_text_from_box(node, x1, x2, y1, y2))
		return text

def get_LT_list_from_box(layout, x1, x2, y1, y2):

	LT_list = []
	if (y1 > y2):
		swap(y1, y2)
	if (x1 > x2):
		swap(x1, x2)
	if not hasattr(layout, '__iter__'):
		if isinstance(layout, LTChar) or isinstance(layout, LTImage) or isinstance(layout, LTFigure):
			x = (layout.bbox[0] + layout.bbox[2])/2.0
			y = (layout.bbox[1] + layout.bbox[3])/2.0
			if (x <= x2 and x >= x1 and y >= y1 and y <= y2):
				return [layout]
			else:
				return []
		# elif isinstance(layout, LTAnno):
		# 	return [layout]
		else:
			return []
	else:
		for node in layout:
			LT_list = LT_list + get_LT_list_from_box(node, x1, x2, y1, y2)
		return LT_list

def print_layout(file, layout, numTabs):
	for x in range(numTabs):
		file.write('\t')
	file.write(str(layout) + '\n')
	if hasattr(layout, '__iter__'):
		for node in layout:
			print_layout(file, node, numTabs + 1)

def print_layout_bytestream(file, layout, numTabs):
	if isinstance(layout, LTTextLineHorizontal):
		for x in range(0, numTabs):
			file.write('\t')
		file.write(unicode(layout.get_text().encode('utf8'), 'utf8') + '\n')
	elif not hasattr(layout, '__iter__'):
		return
	else:
		# file.write('\n')
		for node in layout:
			print_layout_bytestream(file, node, numTabs + 1)

def print_layout_tree(file, layout, numTabs):
	# for x in range(0, numTabs):
	# 	file.write('\t')
	# file.write(str(type(layout)))
	# file.write(str(layout))
	# file.write('\n')
	if isinstance(layout, LTTextLineHorizontal):
		for x in range(0, numTabs):
			file.write('\t')
		file.write(str(layout.bbox) + layout.get_text().encode('utf8') + '\n')
	elif not hasattr(layout, '__iter__'):
		return
	else:
		# file.write('\n')
		for node in layout:
			print_layout_tree(file, node, numTabs + 1)

def group_by_indent(layout, lines):
	if isinstance(layout, LTTextLineHorizontal):
		try:
			lines[layout.bbox[0]] = lines[layout.bbox[0]] + [layout]
		except KeyError as e:
			lines[layout.bbox[0]] = [layout]
	elif not hasattr(layout, '__iter__'):
		return
	else:
		for node in layout:
			group_by_indent(node, lines)

def get_lines(layout):
	if isinstance(layout, LTTextLineHorizontal):
		return [layout]
	elif not hasattr(layout, '__iter__'):
		return []
	else:
		lines = []
		for node in layout:
			lines = lines + get_lines(node)
		return lines

def get_question_lines(pages, reg):
	questions = []
	for lines in pages:
		page_ques = []
		for line in lines:
			for reg in regs:
				if reg.match(line.get_text()) != None:
					page_ques.append([line, reg])
					break
		questions.append(page_ques)
	return questions

def get_lines_by_pages(layout):
	return [get_lines(page) for page in layout]

def get_image_locations(layout):
	image_list = []
	if isinstance(layout, LTImage):# or isinstance(layout, LTFigure)
		return [layout]
	elif hasattr(layout, '__iter__'):
		for node in layout:
			image_list += get_image_locations(node)
		return image_list
	return []

def write_file (folder, filename, filedata, flags='w'):
	"""Write the file data to the folder and filename combination
	(flags: 'w' for write text, 'wb' for write binary, use 'a' instead of 'w' for append)"""
	result = False
	if os.path.isdir(folder):
		try:
			file_obj = open(os.path.join(folder, filename), flags)
			file_obj.write(filedata)
			file_obj.close()
			result = True
		except IOError:
			pass
	return result

def determine_image_type (stream_first_4_bytes):
	"""Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
	file_type = None
	bytes_as_hex = b2a_hex(stream_first_4_bytes)
	# print(bytes_as_hex)
	if bytes_as_hex.startswith('ffd8'):
		file_type = '.jpeg'
	elif bytes_as_hex == '89504e47':
		 # or bytes_as_hex == '789ced9d'
		file_type = '.png'
	elif bytes_as_hex == '47494638':
		file_type = '.gif'
	elif bytes_as_hex.startswith('424d'):
		file_type = '.bmp'
	return file_type

def save_image (lt_image, page_number, images_folder, pypdf_obj = None):
	"""Try to save the image data from this LTImage object, and return the file name, if successful"""
	result = None
	if lt_image.stream:
		file_stream = lt_image.stream.get_rawdata()
		if file_stream:
			file_ext = determine_image_type(file_stream[0:4])
			if file_ext:
				file_name = ''.join([str(page_number), '_', lt_image.name, file_ext])
				if write_file(images_folder, file_name, file_stream, flags='wb'):
					result = file_name
			elif pypdf_obj:
				try:
					pypdf_obj = pypdf_obj["/"+lt_image.name]
					size = (pypdf_obj['/Width'], pypdf_obj['/Height'])
					data = pypdf_obj.getData()
					if pypdf_obj['/ColorSpace'] == '/DeviceRGB':
						mode = "RGB"
					else:
						mode = "P"
					img = Image.frombytes(mode, size, data)
					file_name = ''.join([str(page_number), '_', lt_image.name, '.png'])
					form = Image.registered_extensions()['.png']
					fp = io.BytesIO()
					img.save(fp, form)
					if write_file(images_folder, file_name, fp.getvalue(), flags='wb'):
						result = file_name
				except Exception as e:
					print(e)
					return None
	return result

def get_pypdf_images(pdf_path):
	pdfInput = PdfFileReader(open(pdf_path, 'rb'))
	return get_image_res(pdfInput)

def get_image_res(pdfInput):
	for i in range(pdfInput.getNumPages()):
		page = pdfInput.getPage(i)
		if '/XObject' in page['/Resources']:
			return page['/Resources']['/XObject'].getObject()

# x1, y1 starts in bottom left corner
def create_annot_box(x1, y1, x2, y2, meta, color = [1, 0, 0]):
	new_annot = DictionaryObject()

	new_annot.update({
		# NameObject("/P"): parent,
		NameObject("/F"): NumberObject(4),
		NameObject("/Type"): NameObject("/Annot"),
		NameObject("/Subtype"): NameObject("/Square"),

		NameObject("/T"): TextStringObject(meta["author"]),
		NameObject("/Contents"): TextStringObject(meta["contents"]),

		NameObject("/C"): ArrayObject([FloatObject(c) for c in color]),
		NameObject("/Rect"): ArrayObject([
			FloatObject(x1),
			FloatObject(y1),
			FloatObject(x2),
			FloatObject(y2)
		]),
	})
	return new_annot

def add_annot_to_page(annot, page, output):
	annot_ref = output._addObject(annot);

	if "/Annots" in page:
		page[NameObject("/Annots")].append(annot_ref)
	else:
		page[NameObject("/Annots")] = ArrayObject([annot_ref])

def add_annots(input_file, annot_maps, output_file = 'output.pdf'):
	pdfInput = PdfFileReader(open(input_file, "rb"))
	pdfOutput = PdfFileWriter()
	for i in range(pdfInput.getNumPages()):
		page = pdfInput.getPage(i)
		annot_map = annot_maps[i]
		for annot in annot_map:
			add_annot_to_page(annot, page, pdfOutput)
		pdfOutput.addPage(page)
	outputStream = open(output_file, "wb")
	pdfOutput.write(outputStream)

def get_bounding_box(lines, next_line = None):
	x0, y0, x1, y1 = lines[0].bbox
	for line in lines:
		x0 = min(x0, line.bbox[0])
		y0 = min(y0, line.bbox[1])
		x1 = max(x1, line.bbox[2])
		y1 = max(y1, line.bbox[3])
	if next_line:
		y0 = next_line.bbox[3]
	return [x0, y0, x1, y1]

def get_ques_Bboxes(lines, que_lines):
	ques_boxes = []
	for i in range(len(lines)):
		page_ques_boxes = []
		page_lines = lines[i]
		page_que_lines = que_lines[i]
		for j in range(len(page_que_lines)):
			if j != len(page_que_lines)-1:
				page_ques_boxes.append(get_bounding_box(page_lines[page_lines.index(page_que_lines[j][0]): page_lines.index(page_que_lines[j+1][0])], page_que_lines[j+1][0]))
			else:
				page_ques_boxes.append(get_bounding_box(page_lines[page_lines.index(page_que_lines[j][0]):]))
		ques_boxes.append(page_ques_boxes)
	return ques_boxes

def get_annot_from_bbox(bbox, meta, color):
	return create_annot_box(bbox[0], bbox[1], bbox[2], bbox[3], meta, color)

def get_annots_for_ques(ques_boxes, meta = {"author": "", "contents": "question"}, color = [1, 0, 0]):
	ques_annots = []
	for page_boxes in ques_boxes:
		page_annots = []
		for box in page_boxes:
			page_annots.append(get_annot_from_bbox(box, meta, color))
		ques_annots.append(page_annots)
	return ques_annots

def get_latex_from_LT(LT_list, page_number, image_res = None):
	latex_str = ""

	prevfontname = ""
	prevfontstyle = ""

	for i in range(len(LT_list)):
		if isinstance(LT_list[i], LTChar):
			attr = re.split(",|-", LT_list[i].fontname)
			if(prevfontname != attr[0]):
				# latex_str += "\\fontfamily{" + attr[0] + "}\\selectfont "
				prevfontname = attr[0]
			if(len(attr) > 1 and prevfontstyle != attr[1]):
				if prevfontstyle:
					latex_str += "}"
				prevfontstyle = attr[1]
				if prevfontstyle.startswith("Bold"):
					latex_str += "\\textbf{"
				elif prevfontstyle.startswith("Italic"):
					latex_str += "\\textit{"
			elif len(attr) == 1:
				if prevfontstyle:
					latex_str += "}"
					prevfontstyle = ""
			latex_str += utf8tolatex(LT_list[i].get_text())
		elif isinstance(LT_list[i], LTFigure) or isinstance(LT_list[i], LTImage):
			if prevfontstyle:
				latex_str += "}"
				prevfontstyle = ""
			img_name = save_image(LT_list[i], page_number, "images", image_res)
			if img_name:
				latex_str += "\\begin{figure}\\includegraphics[width=\\linewidth]{" + str(img_name) + "}\\end{figure}"
		# elif isinstance(LT_list[i], LTAnno):
		# 	latex_str += "\\newline\n"
	if prevfontstyle:
		latex_str += "}"
		prevfontstyle = ""
	return latex_str

def auto_ques_annot(layout, regs, infile, outfile):
	lines = get_lines_by_pages(layout)
	que_lines = get_question_lines(lines, regs)
	ques_boxes = get_ques_Bboxes(lines, que_lines)
	ques_annots = get_annots_for_ques(ques_boxes)
	add_annots(infile, ques_annots, outfile)

def compare_y(a, b):
	y1 = a.getObject()["/Rect"][1]
	y2 = b.getObject()["/Rect"][1]
	if y1 < y2:
		return 1
	elif y1 == y2:
		return 0
	else: 
		return -1

def key_y(a):
	return a.getObject()["/Rect"][1]

def get_latex_from_ann_file(pdf_path):
	pdfInput = PdfFileReader(open(pdf_path, "rb"))
	image_res = get_image_res(pdfInput)
	latex_list = []
	layout = get_PDF_layout(pdf_path)
	for i in range(pdfInput.getNumPages()):
		page = pdfInput.getPage(i)
		if "/Annots" in page:
			annot_list = page[NameObject("/Annots")]
			annot_list.sort(key=key_y)
			for annot in annot_list:
				ann = annot.getObject()
				if ann["/Subtype"] == NameObject("/Square"):
					LT_list = get_LT_list_from_box(layout[i], ann["/Rect"][0], ann["/Rect"][2], ann["/Rect"][1], ann["/Rect"][3])
					latex_list.append(get_latex_from_LT(LT_list, i, image_res).replace("{\\textrightarrow}", "${\\rightarrow}$"))
	return latex_list

if __name__ == '__main__':
	if len(sys.argv) > 1:
		pdf_path = sys.argv[1]
	layout = get_PDF_layout(pdf_path)
	
	if len(sys.argv) > 2:
		if sys.argv[2] == "0":
			regs = [re.compile(pattern) for pattern in question_regex_patterns]
			auto_ques_annot(layout, regs, pdf_path, 'annotated.pdf')
		elif sys.argv[2] == "1":
			latex_list = get_latex_from_ann_file(pdf_path)
			file = open("latex.txt", "w")
			file.write("\n\\bigskip\n\\newline\n".join([str(latex.encode('utf-8')) for latex in latex_list]))
	else:
		regs = [re.compile(pattern) for pattern in question_regex_patterns]
		auto_ques_annot(layout, regs, pdf_path, 'annotated.pdf')
		pdf_path = 'annotated.pdf'
		latex_list = get_latex_from_ann_file(pdf_path)
		file = open("latex.txt", "w")
		file.write("\n\\bigskip\n\\newline\n".join([latex.encode('utf-8') for latex in latex_list]))