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

question_regex_patterns = ['^\s*\d+\.\s', '^\s*\d+\.\)', '^\s*\d+\)']

sub_question_regex_patterns = ['^\s*[a-zA-Z]\.\s', '^\s*[a-zA-Z]\.\)', '^\s*[a-zA-Z]\)']

answer_regex_patterns = []

marks_regex_patterns = []

PAGELOWERLIMIT = 30

question_map = {}

question_count = 0

## User Defined based on the pdf involved
page_ht = 792

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


def get_LT_line_list_from_box(layout, x1, x2, y1, y2):

	LT_list = []
	if (y1 > y2):
		swap(y1, y2)
	if (x1 > x2):
		swap(x1, x2)
	if isinstance(layout, LTTextLineHorizontal):
		x = (layout.bbox[0] + layout.bbox[2])/2.0
		y = (layout.bbox[1] + layout.bbox[3])/2.0
		if (x <= x2 and x >= x1 and y >= y1 and y <= y2):
			return [layout]
		else:
			return []
	else:
		if not hasattr(layout, '__iter__'):
			return []
		for node in layout:
			LT_list = LT_list + get_LT_line_list_from_box(node, x1, x2, y1, y2)
		return LT_list

def get_LT_image_list_from_box(layout, x1, x2, y1, y2):
	LT_list = []
	if (y1 > y2):
		swap(y1, y2)
	if (x1 > x2):
		swap(x1, x2)
	if not hasattr(layout, '__iter__'):
		if isinstance(layout, LTImage) or isinstance(layout, LTFigure):
			# print('LTFigure')
			x = (layout.bbox[0] + layout.bbox[2])/2.0
			y = (layout.bbox[1] + layout.bbox[3])/2.0
			if (y >= y1 and y <= y2):
				return [layout]
			else:
				return []
		else:
			return []
	else:
		for node in layout:
			LT_list = LT_list + get_LT_image_list_from_box(node, x1, x2, y1, y2)
		return LT_list

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
	# print(layout)
	if isinstance(layout, LTTextLineHorizontal):
		if layout.bbox[1] != layout.bbox[3] and layout.bbox[0] != layout.bbox[2]:
			return [layout]
		else:
			return []
	elif not hasattr(layout, '__iter__'):
		return []
	else:
		lines = []
		for node in layout:
			lines = lines + get_lines(node)
		return lines

def get_question_lines(pages, reg_all):
	questions = []
	question_indices = []
	reg_main_ques = [re.compile(pattern) for pattern in question_regex_patterns]
	reg_sub_ques = [re.compile(pattern) for pattern in sub_question_regex_patterns]
	reg_ans = [re.compile(pattern) for pattern in answer_regex_patterns]

	global question_count
	question_count = 0

	for lines in pages:
		page_all = []
		page_indices = []
		index = 0
		for line in lines:
			for reg in reg_all:
				if reg.match(line.get_text()) != None:
					if reg in reg_main_ques:
						question_count += 1
						page_all.append([line, reg, 'main_ques', question_count])
						page_indices.append(index)
						break	
					elif reg in reg_sub_ques:
						page_all.append([line, reg, 'sub_ques', question_count])
						page_indices.append(index)
						break
					elif reg in reg_ans:
						page_all.append([line, reg, 'ans', question_count])
						page_indices.append(index)
						break	
			index += 1
		questions.append(page_all)
		question_indices.append(page_indices)
	return questions, question_indices

def get_sorted_lines(lines):
	sorted_lines = sorted(lines, key=lambda x : x.bbox[1], reverse=True)
	return sorted_lines

def get_lines_by_pages(layout):
	return [get_sorted_lines(get_lines(page)) for page in layout]

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
	if bytes_as_hex.startswith('ffd8'.encode()):
		file_type = '.jpeg'
	elif bytes_as_hex == '89504e47':
		 # or bytes_as_hex == '789ced9d'
		file_type = '.png'
	elif bytes_as_hex == '47494638':
		file_type = '.gif'
	elif bytes_as_hex.startswith('424d'.encode()):
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
				# try:
				# print(pypdf_obj)
				pypdf_obj = pypdf_obj["/"+lt_image.name]
				# print(pypdf_obj)

				size = (pypdf_obj['/Width'], pypdf_obj['/Height'])
				data = pypdf_obj.getData()
				if ('/ColorSpace' in pypdf_obj) and pypdf_obj['/ColorSpace'] == '/DeviceRGB':
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

				# except Exception as e:
				# 	print("Exception")
				# 	print(e)
				# 	return None
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
		# print(line.get_text())
		x0 = min(x0, line.bbox[0])
		y0 = min(y0, line.bbox[1])
		x1 = max(x1, line.bbox[2])
		# y1 = max(y1, line.bbox[3])
	if next_line:
		y0 = next_line.bbox[3]
		# y0 = max(y0,PAGELOWERLIMIT)
	else:
		y0 = max(y0,PAGELOWERLIMIT)
	# print("-----------------------------------------")
	return [x0, y0, x1, y1]

def get_meta_data(lines, meta_pattern_list):
	meta = []
	reg_list = [re.compile(pattern) for pattern in meta_pattern_list]
	for reg in reg_list:
		meta_found = False
		for line in lines :
			# print(line.get_text())
			if reg.search(line.get_text()) != None:
				# print('found')
				meta_ext = reg.search(line.get_text()).group(0)
				meta.append(re.compile('\d+').search(meta_ext).group(0))
				meta_found = True
				# print('found')
				# print(re.compile('\d+').search(meta_ext).group(0))
				break
		if (not meta_found):
			meta.append('None')
	if len(meta) == 0:
		meta.append('None')
	return meta

def split_question_lines(lines):
	font_type_count = {}
	for line in lines:
		if isinstance(line, LTTextLineHorizontal):	
			for obj in line._objs:
				if isinstance(obj, LTChar):
					if (obj.fontname in font_type_count):
						font_type_count[obj.fontname] += 1
					else:
						font_type_count[obj.fontname] = 0

	sorted_font_type_count = sorted(font_type_count.items(), key=lambda x : x[1], reverse=True)
	
	if (len(sorted_font_type_count) <= 1):
		return -1
	else:
		font_type1 = sorted_font_type_count[0][0]
		font_type2 = sorted_font_type_count[1][0]

	line_labels = [] 
	for line in lines:	
		if isinstance(line, LTTextLineHorizontal):
			line_font_type_counts = [0,0,0]
			for obj in line._objs:
				if isinstance(obj, LTChar):
					if (obj.fontname == font_type1):
						line_font_type_counts[0] += 1
					elif (obj.fontname == font_type2):
						line_font_type_counts[1] += 1
					else:
						line_font_type_counts[2] += 1						
			line_labels.append(line_font_type_counts.index(max(line_font_type_counts)))
		else:
			line_labels.append(2)

	seen_lab = -1
	line_idx = -1
	for idx, lab in enumerate(line_labels):
		if lab < 2: 
			if seen_lab == -1 :
				seen_lab = lab 
			elif seen_lab != lab : 
				line_idx = idx
				break

	return line_idx

def modify_question_lines_style(lines, que_lines, que_line_indices):
	final_ques_lines = []
	final_ques_line_indices = []

	for i in range(len(lines)):
		final_page_ques_lines = []
		final_page_ques_line_indices = []

		page_lines = lines[i]
		page_que_lines = que_lines[i]
		page_que_indices = que_line_indices[i]
		
		for j in range(len(page_que_lines)):
			
			final_page_ques_lines.append(page_que_lines[j])
			final_page_ques_line_indices.append(page_que_indices[j])

			if j != len(page_que_lines)-1:
				ans_index = split_question_lines(page_lines[page_que_indices[j]: page_que_indices[j+1]])
				if ans_index != -1:
					final_page_ques_lines.append([page_lines[page_que_indices[j] + ans_index], '', 'ans', page_que_lines[j][3]])
					final_page_ques_line_indices.append(page_que_indices[j] + ans_index)
			else:
				ans_index = split_question_lines(page_lines[page_que_indices[j]:])
				if ans_index != -1:
					final_page_ques_lines.append([page_lines[page_que_indices[j] + ans_index], '', 'ans', page_que_lines[j][3]])
					final_page_ques_line_indices.append(page_que_indices[j] + ans_index)

		final_ques_lines.append(final_page_ques_lines)
		final_ques_line_indices.append(final_page_ques_line_indices)
	return final_ques_lines, final_ques_line_indices

def modify_question_lines_extra(lines, que_lines, que_line_indices):
	final_ques_lines = [que_lines[0]]
	final_ques_line_indices = [que_line_indices[0]]

	prev_page_ques_line = []
	if len(final_ques_lines[0]) > 0:
			prev_page_ques_line = final_ques_lines[0][-1]

	for i in range(1, len(lines)):

		page_lines = lines[i]
		page_que_lines = que_lines[i]
		page_que_indices = que_line_indices[i]

		final_page_ques_lines = []
		final_page_ques_line_indices = []

		if len(page_lines) > 0:
			if len(page_que_indices) == 0 or (len(page_que_indices) > 0 and page_que_indices[0] != 0):
				if len(prev_page_ques_line):
					temp_question_line = prev_page_ques_line.copy()
					temp_question_line[0] = page_lines[0]
					final_page_ques_lines.append(temp_question_line)
					final_page_ques_line_indices.append(0)

		final_page_ques_lines += page_que_lines
		final_page_ques_line_indices += page_que_indices

		# print(final_page_ques_line_indices)
		# print(final_page_ques_lines)

		final_ques_lines.append(final_page_ques_lines)
		final_ques_line_indices.append(final_page_ques_line_indices)
		
		if len(final_ques_lines[i]) > 0:
			prev_page_ques_line = final_ques_lines[i][-1]
		else:
			prev_page_ques_line = []
	# print(final_ques_line_indices)
	return final_ques_lines, final_ques_line_indices

def get_ques_Bboxes(lines, que_lines, que_line_indices, meta_pattern_list):
	ques_boxes = []
	for i in range(len(lines)):
		page_ques_boxes = []
		page_lines = lines[i]
		page_que_lines = que_lines[i]
		page_que_indices = que_line_indices[i]
		
		for j in range(len(page_que_lines)):
			if j != len(page_que_lines)-1:
				# print(i)
				# print(j)
				# print(page_lines[page_que_indices[j]].get_text())
				meta_list = get_meta_data(page_lines[page_que_indices[j]: page_que_indices[j+1]], meta_pattern_list)
				# print(meta_list)	
				page_ques_boxes.append([get_bounding_box(page_lines[page_que_indices[j]: page_que_indices[j+1]], page_que_lines[j+1][0])] + page_que_lines[j][2:4] + meta_list)
			else:
				meta_list = get_meta_data(page_lines[page_que_indices[j]:], meta_pattern_list)
				page_ques_boxes.append([get_bounding_box(page_lines[page_que_indices[j]:])] +  page_que_lines[j][2:4] + meta_list)

		# if len(page_ques_boxes) == 0:
		# 	page_ques_boxes.append([5,5,590,750])

		ques_boxes.append(page_ques_boxes)
	return ques_boxes

def get_annot_from_bbox(bbox, meta, color):
	return create_annot_box(bbox[0], bbox[1], bbox[2], bbox[3], meta, color)

def get_annots_for_ques(ques_boxes, meta = {"author": "", "contents": "question"}, color = [1, 0, 0]):
	ques_annots = []
	page_num = 0
	for page_boxes in ques_boxes:
		page_num += 1
		page_annots = []
		for box in page_boxes:
			meta["contents"] = "Belongs to Question " + str(box[2]) +"\n" + str(box[1]) + "\n" + "Marks : " + str(box[3])
			if box[1] == 'ans':
				color = [0, 1, 0]
			elif box[1] == 'main_ques':
				color = [1, 0, 0]
			elif box[1] == 'sub_ques':
				color = [0, 0, 1]
			annot_object = get_annot_from_bbox(box[0], meta, color)
			page_annots.append(annot_object)
			if box[1] == 'ans':
				question_map[box[2]]["ans_list"].append( (page_num, annot_object))
			elif box[1] == 'main_ques':
				question_map[box[2]] = {"main_ques" : (page_num, annot_object), "sub_ques_list" : [], "ans_list" : []}
			elif box[1] == 'sub_ques':
				question_map[box[2]]["sub_ques_list"].append((page_num, annot_object))
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

def get_text_from_LTList(LT_list):
	text_str = ""
	for LT_obj in LT_list:
		if isinstance(LT_obj, LTTextLineHorizontal):
			text_str += LT_obj.get_text()
	return text_str

def get_selection_boxes(layout, ques_boxes):
	selection_boxes = []
	page_num = 0
	id_num = 1 
	for page_boxes in ques_boxes:
		page_num += 1
		page_selections = []
		for box in page_boxes:
			id_num += 1
			selection_obj = {}
			color = []
			selection_type = ''
			question_type = ''
			options = []
			if box[1] == 'ans':
				color = 'rgb(0, 255, 0)'
				selection_type = 'Answer'
			elif box[1] == 'main_ques':
				color = 'rgb(255, 0, 0)'
				selection_type = 'Main Question'
				question_type = 'Descriptive'
			elif box[1] == 'sub_ques':
				color = 'rgb(0, 0, 255)'
				selection_type = 'Sub Question'
				question_type = 'Descriptive'

			ques_num = box[2]
			name = box[1] + " " + str(box[2])
			marks = box[3]
			coordinates_obj = {}
			coordinates_obj['page'] = page_num
			coordinates_obj['pageOffset'] = {'left' : 0, 'top' : (792-page_ht) / 10 + int((page_ht * 740 / 792.0) * (page_num- 1))}
			coordinates_obj['height'] = int((box[0][3] - box[0][1])* 740 / 792.0)
			coordinates_obj['width'] = int((box[0][2] - box[0][0])* 740 / 792.0)
			coordinates_obj['left'] = int((box[0][0])* 740 / 792.0)
			coordinates_obj['top'] = int((page_ht - box[0][3])* 740 / 792.0)

			selection_obj['id'] = id_num
			selection_obj['color'] = color
			selection_obj['name'] = name
			selection_obj['coordinates'] = coordinates_obj
			selection_obj['marks'] = marks
			selection_obj['type'] = selection_type
			selection_obj['qnum'] = ques_num
			selection_obj['textData'] = extract_text_from_bbox_coords(layout, page_num, box[0])
			selection_obj['question_type'] = question_type
			selection_obj['options'] = options

			page_selections.append(selection_obj)

		selection_boxes.append(page_selections)
	
	selection_boxes_tot = [x for y in selection_boxes for x in y]

	return selection_boxes_tot

def get_selection_boxes_from_PDF(pdf_path, ques_reg, ans_reg, sub_ques_reg, marks_reg, use_style, pdf_dimensions, question_type, mcq_reg):

	# print("Hey at the top")
	layout = get_PDF_layout(pdf_path)

	global question_regex_patterns
	global answer_regex_patterns
	global sub_question_regex_patterns
	global marks_regex_patterns
	global page_ht

	page_ht = pdf_dimensions['height']
	question_regex_patterns = []
	answer_regex_patterns = []
	sub_question_regex_patterns = []
	marks_regex_patterns = []

	if ques_reg:
		delim_pattern = '^\s*' + ques_reg
		question_regex_patterns.append(delim_pattern)

	if ans_reg:
		delim_pattern = '^\s*' + ans_reg
		answer_regex_patterns.append(delim_pattern)

	if sub_ques_reg:
		delim_pattern = '^\s*' + sub_ques_reg
		sub_question_regex_patterns.append(delim_pattern)

	if marks_reg:
		delim_pattern = marks_reg
		marks_regex_patterns.append(delim_pattern)

	regs_all = [re.compile(pattern) for pattern in question_regex_patterns + sub_question_regex_patterns + answer_regex_patterns]
	
	lines = get_lines_by_pages(layout)
	que_lines, que_line_indices = get_question_lines(lines, regs_all)

	if use_style:
		que_lines, que_line_indices = modify_question_lines_style(lines, que_lines, que_line_indices)
	
	# print(que_line_indices)
	que_lines, que_line_indices = modify_question_lines_extra(lines, que_lines, que_line_indices)
	# print(que_line_indices)
	ques_boxes = get_ques_Bboxes(lines, que_lines, que_line_indices, marks_regex_patterns)

	# print(ques_boxes[0][0])
	
	selection_boxes = get_selection_boxes(layout, ques_boxes)

	if question_type == 'MCQ':
		# delim_pattern =  '^\s*' + mcq_reg
		# reg_mcq = re.compile(delim_pattern)
		selection_boxes = extract_options(selection_boxes, mcq_reg)
	
	# print (selection_boxes[1:5])		
	return selection_boxes	

def extract_options(selection_boxes, mcq_reg):
	for selection_box in selection_boxes:
		if selection_box['type'] != 'Ans':
			selection_box['question_type'] = 'MCQ'
			content = re.split(mcq_reg, selection_box['textData'])
			selection_box['textData'] = content[0]
			optionsData = []
			for option in content[1:]:
				optionsData.append({'optionText' : option})
			selection_box['options'] = optionsData
	return selection_boxes

def auto_ques_annot(layout, regs_all, meta_pattern_list, infile, outfile, use_style):
	lines = get_lines_by_pages(layout)
	que_lines, que_line_indices = get_question_lines(lines, regs_all)
	# if use_style:
	# 	que_lines, que_line_indices = modify_question_lines_style(lines, que_lines, que_line_indices)
	# print(que_line_indices)
	# print('--------------------')
	que_lines, que_line_indices = modify_question_lines_extra(lines, que_lines, que_line_indices)
	# print(que_line_indices)
	ques_boxes = get_ques_Bboxes(lines, que_lines, que_line_indices, meta_pattern_list)
	ques_annots = get_annots_for_ques(ques_boxes)
	# selection_boxes = get_selection_boxes(ques_boxes)
	add_annots(infile, ques_annots, outfile)

def key_y(a):
	return a.getObject()["/Rect"][1]

def get_bounding_box_coords(selection_coordinates, page_ht):

			# 	coordinates_obj['height'] = (box[0][3] - box[0][1])* 740 / 792.0
			# coordinates_obj['width'] = (box[0][2] - box[0][0])* 740 / 792.0
			# coordinates_obj['left'] = (box[0][0])* 740 / 792.0
			# coordinates_obj['top'] = (page_ht - box[0][3])* 740 / 792.0
	newSelection_coordinates = selection_coordinates
	newSelection_coordinates['height'] /= (740 / 792.0)	
	newSelection_coordinates['width'] /= (740 / 792.0)	
	newSelection_coordinates['left'] /= (740 / 792.0)	
	newSelection_coordinates['top'] /= (740 / 792.0)	

	bbox = [0]*4
	bbox[0] = newSelection_coordinates['left']
	bbox[3] = page_ht - newSelection_coordinates['top']
	bbox[1] = bbox[3] - newSelection_coordinates['height']
	bbox[2] = bbox[0] + newSelection_coordinates['width']  

	return bbox

def get_sorted_selections(selections):
	sorted_selections = sorted(selections, key=lambda x : (x['coordinates']['page'], x['coordinates']['top']))
	return sorted_selections

def extract_text_from_pdf_selections(pdf_path, selections, pdf_dimensions):
	# try:
	pdfInput = PdfFileReader(open(pdf_path, "rb"))
	image_res = get_image_res(pdfInput)
	page_ht = pdf_dimensions['height']
	sorted_selections = get_sorted_selections(selections)
	text_list = []
	layout = get_PDF_layout(pdf_path)
	for curr_selection in sorted_selections:
		curr_bbox = get_bounding_box_coords(curr_selection['coordinates'], page_ht)
		LT_list_images = get_LT_image_list_from_box(layout[curr_selection['coordinates']['page'] - 1], curr_bbox[0], curr_bbox[2], curr_bbox[1], curr_bbox[3])
	# 	text_list.append(get_text_from_LTList(LT_list))
		curr_text = curr_selection['textData']
		if len(LT_list_images):
			curr_text += "Images: \n"
			print(curr_selection['coordinates']['page'])
			print(LT_list_images)
			print(len(LT_list_images))
		for LT_img in LT_list_images:
			image_res = None
			img_name = save_image(LT_img, curr_selection['coordinates']['page'], "images", image_res)
			if img_name:
				curr_text += img_name + "\n"
		text_list.append(curr_text) 

	# print(sorted_selections[0])
	text_list = [selection['textData'] for selection in sorted_selections]

	file = open("text.txt", "w")
	file.write("\n".join(text_list))
	# print(text_list)
	return text_list
	# except:
	# 	return False

def extract_text_from_bbox_coords(layout, page_num, bbox):
	LT_list = get_LT_line_list_from_box(layout[page_num - 1], bbox[0], bbox[2], bbox[1], bbox[3])
	LT_list = get_sorted_lines(LT_list)
	text_data = get_text_from_LTList(LT_list)
	return text_data	

def extract_text_from_current_selection(pdf_path, page_num, pdf_dimensions, coordinates):
		# print("Hye")
	pdfInput = PdfFileReader(open(pdf_path, "rb"))
	# image_res = get_image_res(pdfInput)
	page_ht = pdf_dimensions['height']
	# sorted_selections = get_sorted_selections(selections)
	text_data = ''
	layout = get_PDF_layout(pdf_path)
	curr_bbox = get_bounding_box_coords(coordinates, page_ht)
	LT_list = get_LT_line_list_from_box(layout[page_num - 1], curr_bbox[0], curr_bbox[2], curr_bbox[1], curr_bbox[3])
	LT_list = get_sorted_lines(LT_list)
	text_data = get_text_from_LTList(LT_list)
	# print(text_data)
	return text_data
	

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
			if len(sys.argv) > 6:
				question_regex_patterns = []
				delim_pattern = '^\s*' + sys.argv[3]
				question_regex_patterns.append(delim_pattern)

				answer_regex_patterns = []
				delim_pattern = '^\s*' + sys.argv[4]
				answer_regex_patterns.append(delim_pattern)

				sub_question_regex_patterns = []
				delim_pattern = '^\s*' + sys.argv[5]
				sub_question_regex_patterns.append(delim_pattern)

				marks_regex_patterns = []
				delim_pattern = sys.argv[6]
				marks_regex_patterns.append(delim_pattern)

			regs_all = [re.compile(pattern) for pattern in question_regex_patterns + sub_question_regex_patterns + answer_regex_patterns]
			# regs_ans = [re.compile(pattern) for pattern in answer_regex_patterns]
			use_style = 1
			# use_style = 0
			auto_ques_annot(layout, regs_all, marks_regex_patterns, pdf_path, 'annotated.pdf', use_style)	
		elif sys.argv[2] == "1":
			latex_list = get_latex_from_ann_file(pdf_path)
			file = open("latex.txt", "w")
			file.write("\n\\bigskip\n\\newline\n".join([latex.encode('utf-8').decode() for latex in latex_list]))
	else:
		regs = [re.compile(pattern) for pattern in question_regex_patterns]
		auto_ques_annot(layout, regs, pdf_path, 'annotated.pdf')
		pdf_path = 'annotated.pdf'
		latex_list = get_latex_from_ann_file(pdf_path)
		file = open("latex.txt", "w")
		file.write("\n\\bigskip\n\\newline\n".join([latex.encode('utf-8').decode() for latex in latex_list]))