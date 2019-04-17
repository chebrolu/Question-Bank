from flask import Flask, redirect, url_for, request, json
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

import sys
sys.path.insert(0, '../Question-Bank/')

import splitter

@app.route('/getannot',methods = ['POST'])
def getannot():
	if request.method == 'POST':

		input_data = request.get_json()
		response = app.response_class(
			response=json.dumps(splitter.get_selection_boxes_from_PDF(input_data['pdf_path'], input_data['ques_reg'], input_data['ans_reg'], input_data['sub_ques_reg'], input_data['marks_reg'], input_data['use_style'], input_data['pdf_dimensions'], input_data['question_type'], input_data['mcq_reg'])),
			mimetype='application/json'
		)

		return response


@app.route('/submitChanges',methods = ['POST'])
def submitChanges():
	if request.method == 'POST':

		input_data = request.get_json()
		retval = splitter.extract_text_from_pdf_selections(input_data['pdf_path'], input_data['selections'], input_data['pdf_dimensions'])
		response = app.response_class(
			response=json.dumps({'msg' : retval}),
			mimetype='application/json'
		)
		return response

@app.route('/getTextForSelection',methods = ['POST'])
def getTextForSelection():
	if request.method == 'POST':

		input_data = request.get_json()
		retval = splitter.extract_text_from_current_selection(input_data['pdf_path'], input_data['page_num'], input_data['pdf_dimensions'], input_data['coordinates'])
		response = app.response_class(
			response=json.dumps({'textData' : retval}),
			mimetype='application/json'
		)
		return response

if __name__ == '__main__':
	app.run(debug = True)