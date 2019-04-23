<template>
  <div>
     <form>
       <input type="checkbox" name="question_type" ref="question_type" value="1" v-on:change="checkQuestionType($event)"> MCQs Questions? <br>

       Main Question Regex<br>
       <!-- <input type="text" name="main_ques_regex" ref="main_ques_regex" > <br> -->
       
       <select type="text" name="main_ques_regex" v-on:change="checkValMainQuesRegex($event)" ref="main_ques_regex" > 
        <option value="">None</option>
        <option value="\d+\.">&#60;num&#62;.</option>
        <option value="\d+">&#60;num&#62;</option>
        <option value="\d+\)">&#60;num&#62;)</option>
        <option value="\(\d+">(&#60;num&#62;</option>
        <option value="Problem\s\d+">Problem &#60;num&#62;</option>
        <option value="Question\s\d+">Question &#60;num&#62;</option>
        <option value="Q\s\d+">Q &#60;num&#62;</option>
        <option value=".*\s+Problem">&#60;text&#62; Problem</option>
        <option value=".*\s+Question">&#60;text&#62; Question</option>
        <option value="other">other</option>
       </select>
       <input type="text" name="main_ques_regex_other" ref="main_ques_regex_other" style='display:none;'/><br>
       
       Sub Question Regex<br>
       <select type="text" name="sub_ques_regex" v-on:change="checkValSubQuesRegex($event)" ref="sub_ques_regex" > 
        <option value="">None</option>
        <option value="\([a-zA-Z]\)">(&#60;alpha&#62;)</option>
        <option value="[a-zA-Z]\)">&#60;alpha&#62;)</option>
        <option value="[a-zA-Z]\.">&#60;alpha&#62;.</option>
        <option value="\d+\)">&#60;num&#62;)</option>
        <option value="\d+\.\d+">&#60;num&#62;.&#60;num&#62;</option>
        <option value="(?i)[MDCLXVI]+\)">&#60;roman&#62; )</option>
        <option value="(?i)[MDCLXVI]+\.">&#60;roman&#62; .</option>
        <option value="other">other</option>

       </select>
       <input type="text" name="sub_ques_regex_other" ref="sub_ques_regex_other" style='display:none;'/><br>
       
       <div class="mcq_div" ref="mcq_div" style='display:none;'>
         MCQ Regex<br>
         <select type="text" name="mcq_regex" v-on:change="checkValMCQRegex($event)" ref="mcq_regex" > 
          <option value="">None</option>
          <option value="\([a-zA-Z]\)">(&#60;alpha&#62;)</option>
          <option value="[a-zA-Z]\)">&#60;alpha&#62;)</option>
          <option value="[a-zA-Z]\.">&#60;alpha&#62;.</option>
          <option value="\d+\)">&#60;num&#62;)</option>
          <option value="\d+\.">&#60;num&#62;.</option>
          <option value="\d+">&#60;num&#62;</option>
          <option value="\d+\)">&#60;num&#62;)</option>
          <option value="other">other</option>
         </select>
         <input type="text" name="mcq_regex_other" ref="mcq_regex_other" style='display:none;'/><br>
       </div>

       Answer Regex<br>
       <select type="text" name="ans_regex" v-on:change="checkValAnsRegex($event)" ref="ans_regex" > 
        <option value="">None</option>
        <option value="Answer">Answer</option>
        <option value="Solution">Solution</option>
        <option value="Ans">Ans</option>
        <option value="A:">A:</option>
        <option value="other">other</option>
       </select>
       <input type="text" name="ans_regex_other" ref="ans_regex_other" style='display:none;'/><br>
       <input type="checkbox" name="use_style" ref="use_style" value="1"> Use Style Based QnA separation <br>
      
       Marks Regex<br>
       <select type="text" name="marks_regex" v-on:change="checkValMarksRegex($event)" ref="marks_regex" > 
        <option value="">None</option>
        <option value="\(\d+\spoints\)">(&#60;num&#62; points)</option>
        <option value="\(\d+\smarks\)">(&#60;num&#62; marks)</option>
        <option value="\(\d+\spts\)">(&#60;num&#62; pts)</option>
        <option value="\[\d+\spoints\]">[&#60;num&#62; points]</option>
        <option value="\[\d+\smarks\]">[&#60;num&#62; marks]</option>
        <option value="\[\d+\spts\]">[&#60;num&#62; pts]</option>
        <option value="other">other</option>
       </select>
       <input type="text" name="marks_regex_other" ref="marks_regex_other" style='display:none;'/><br>

       Time Given for Entire Paper : <br>
       <input type="text" name="time_given" ref="time_given"> <br>

       Total Marks for Entire Paper :<br>
       <input type="text" name="tot_marks" ref="tot_marks"> <br>

       <!-- <input type="text" name="marks_regex" ref="marks_regex" > <br> -->
       PDF Directory : <br>
       <input type="text" name="pdf_dir" ref="pdf_dir"> <br>
       <button type="button" v-on:click="initBbox">Initialise Bounding Boxes</button>
       <button type="button" v-on:click="submitChanges">Submit Changes</button>
     </form>
  </div>
</template>

<script>

import $ from 'jquery'

export default {
  name: 'InitialiseInput',
  props: ['name', 'batchUpdateSelections', 'changeMarksScale', 'pdfDimensions', 'getSelections', 'setPDFPath'],
  data () {
    return {
      quesReg: '',
      subQuesReg: '',
      ansReg: '',
      marksReg: '',
      pdfDir: '',
      pdfPath: '',
      useStyle: '',
      totMarks: '',
      timeGiven: '',
      inputData: {},
      questionType: '',
      mcqReg: ''
    }
  },
  methods: {
    initBbox: function () {
      this.quesReg = this.$refs.main_ques_regex.value
      this.subQuesReg = this.$refs.sub_ques_regex.value
      this.ansReg = this.$refs.ans_regex.value
      this.marksReg = this.$refs.marks_regex.value
      this.pdfDir = this.$refs.pdf_dir.value
      this.useStyle = this.$refs.use_style.checked
      this.totMarks = parseInt(this.$refs.tot_marks.value)
      this.timeGiven = parseInt(this.$refs.time_given.value)
      this.questionType = 'Descriptive'
      this.mcqReg = ''
      if (this.$refs.question_type.checked) {
        this.questionType = 'MCQ'
        this.mcqReg = this.$refs.mcq_regex.value
      }
      if (!isNaN(this.totMarks) && !isNaN(this.timeGiven)) {
        this.changeMarksScale(this.totMarks, this.timeGiven)
      }
      if (this.quesReg === 'other') {
        this.quesReg = this.$refs.main_ques_regex_other.value
      }
      if (this.subQuesReg === 'other') {
        this.subQuesReg = this.$refs.sub_ques_regex_other.value
      }
      if (this.ansReg === 'other') {
        this.ansReg = this.$refs.ans_regex_other.value
      }
      if (this.marksReg === 'other') {
        this.marksReg = this.$refs.marks_regex_other.value
      }
      if (this.mcqReg === 'other') {
        this.mcqReg = this.$refs.mcq_regex_other.value
      }
      // this.quesReg = '\\d+\\.'
      // this.subQuesReg = '\\([a-zA-Z]\\)'
      // this.ansReg = 'Answer'
      // this.marksReg = '\\(\\d+\\spoints\\)'
      if (this.pdfDir === '') {
        this.pdfPath = this.name
      } else {
        this.pdfPath = this.pdfDir + '/' + this.name
      }
      this.setPDFPath(this.pdfPath)
      this.inputData = {}
      this.inputData['ques_reg'] = this.quesReg
      this.inputData['sub_ques_reg'] = this.subQuesReg
      this.inputData['ans_reg'] = this.ansReg
      this.inputData['marks_reg'] = this.marksReg
      this.inputData['pdf_path'] = this.pdfPath
      this.inputData['use_style'] = this.useStyle
      this.inputData['pdf_dimensions'] = this.pdfDimensions
      this.inputData['question_type'] = this.questionType
      this.inputData['mcq_reg'] = this.mcqReg
      var context = this
      $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        url: 'http://127.0.0.1:5000/getannot',
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, HEAD, OPTIONS'
        },
        success: function (msg) {
          context.batchUpdateSelections(msg)
        },
        error: function (request, status, error) {
          console.log(error)
        },
        data: JSON.stringify(this.inputData)
      })
    },
    submitChanges: function () {
      this.inputData = {}
      this.inputData['pdf_path'] = this.pdfPath
      this.inputData['selections'] = this.getSelections()
      this.inputData['pdf_dimensions'] = this.pdfDimensions
      $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        url: 'http://127.0.0.1:5000/submitChanges',
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, HEAD, OPTIONS'
        },
        success: function (msg) {
          console.log(msg)
        },
        error: function (request, status, error) {
          console.log(error)
        },
        data: JSON.stringify(this.inputData)
      })
    },
    checkValMainQuesRegex: function (event) {
      if (this.$refs.main_ques_regex.value === 'other') {
        this.$refs.main_ques_regex_other.style.display = 'block'
      } else {
        this.$refs.main_ques_regex_other.style.display = 'none'
      }
    },
    checkValSubQuesRegex: function (event) {
      if (this.$refs.sub_ques_regex.value === 'other') {
        this.$refs.sub_ques_regex_other.style.display = 'block'
      } else {
        this.$refs.sub_ques_regex_other.style.display = 'none'
      }
    },
    checkValAnsRegex: function (event) {
      if (this.$refs.ans_regex.value === 'other') {
        this.$refs.ans_regex_other.style.display = 'block'
      } else {
        this.$refs.ans_regex_other.style.display = 'none'
      }
    },
    checkValMarksRegex: function (event) {
      if (this.$refs.marks_regex.value === 'other') {
        this.$refs.marks_regex_other.style.display = 'block'
      } else {
        this.$refs.marks_regex_other.style.display = 'none'
      }
    },
    checkValMCQRegex: function (event) {
      if (this.$refs.mcq_regex.value === 'other') {
        this.$refs.mcq_regex_other.style.display = 'block'
      } else {
        this.$refs.mcq_regex_other.style.display = 'none'
      }
    },
    checkQuestionType: function (event) {
      if (this.$refs.question_type.checked) {
        this.$refs.mcq_div.style.display = 'block'
      } else {
        this.$refs.mcq_div.style.display = 'none'
      }
    }
  }
}
</script>

<style scoped>

</style>
