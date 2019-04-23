<template>
  <div class='editor'>
    <div class='sidebar'>
      <h1>Question Bank</h1>
      <!-- <p><strong>A tool to interactively select text regions of PDFs and images.</strong> Use with <a href="https://github.com/jcushman/pdfquery">PDFQuery</a> (Python/PDF) or to make UZN/OCR zone files for <a href="https://github.com/tesseract-ocr/tesseract">tesseract</a> (image-to-text).</p>
      <p>More details (maybe) at <a href="https://github.com/jsoma/kull">https://github.com/jsoma/kull</a>.</p> -->
      <Uploader :notify="newFile"></Uploader>
      <p v-if="name"><strong>Click and drag on the image to the right</strong> to form selection areas.</p>
      <!-- 
      <ZoneViewer :selections="selections" class='zone-viewer' :batchUpdateSelections="batchUpdateSelections" :originalFilename="name" v-if="src"></ZoneViewer>
      <PDFZoneViewer :dimensions="pdfDimensions" :selections="selections" class='zone-viewer' :batchUpdateSelections="batchUpdateSelections" :originalFilename="name" v-if="arrayBuffer"></PDFZoneViewer> -->
      <InitialiseInput :batchUpdateSelections="batchUpdateSelections" :name="name" :changeMarksScale="changeMarksScale" :pdfDimensions="pdfDimensions" :getSelections="getSelections" :setPDFPath="setPDFPath"></InitialiseInput>
    </div>
    <div class='content'>
      <Annotator :src="src" :setPdfSize="setPdfSize" :arrayBuffer="arrayBuffer" :name="name" :selections="selections" :addSelection="addSelection" :deleteSelection="deleteSelection" :getSelectionById="getSelectionById" :updateSelectionById="updateSelectionById" :getComplement="getComplement" :marksScale="marksScale"></Annotator>
    </div>
  </div>
</template>

<script>
import $ from 'jquery'
import Uploader from '@/components/Uploader'
import Annotator from '@/components/Annotator'
import ZoneViewer from '@/components/ZoneViewer'
import PDFZoneViewer from '@/components/PDFZoneViewer'
// import randomColor from 'randomcolor'
import InitialiseInput from '@/components/InitialiseInput'

export default {
  name: 'editor',
  components: {
    Uploader,
    Annotator,
    ZoneViewer,
    PDFZoneViewer,
    InitialiseInput
  },
  data () {
    return {
      src: null,
      arrayBuffer: null,
      name: '',
      pdfPath: '',
      selections: [],
      pdfDimensions: {
        height: 0,
        width: 0
      },
      tempSelectionArr: [],
      inputData: {},
      marksScale: 1
    }
  },
  methods: {
    convertScale: function (selection) {
      selection.coordinates.height = selection.coordinates.height * 740 / 792.0
      selection.coordinates.width = selection.coordinates.width * 740 / 792.0
      selection.coordinates.top = selection.coordinates.top * 740 / 792.0
      selection.coordinates.left = selection.coordinates.left * 740 / 792.0
      return selection
    },
    setPDFPath: function (pdfpath) {
      this.pdfPath = pdfpath
    },
    batchUpdateSelectionsWithScaling: function (selections) {
      this.selections = selections
      this.selections = this.selections.map(selection => this.convertScale(selection))
    },
    batchUpdateSelections: function (selections) {
      this.selections = selections
    },
    setPdfSize: function (width, height) {
      this.pdfDimensions = {
        width: width,
        height: height
      }
    },
    compareFunc: function (a, b) {
      if (a['coordinates']['page'] < b['coordinates']['page']) {
        return -1
      } else {
        if (a['coordinates']['page'] === b['coordinates']['page']) {
          if (a['coordinates']['top'] < b['coordinates']['top']) {
            return -1
          } else {
            return 1
          }
        } else {
          return 1
        }
      }
    },
    addSelection: function (coords) {
      if (coords.height === 0 || coords.width === 0) {
        return
      }
      this.inputData = {}
      this.inputData['pdf_path'] = this.pdfPath
      this.inputData['page_num'] = coords.page
      this.inputData['pdf_dimensions'] = this.pdfDimensions
      this.inputData['coordinates'] = {top: coords.top, left: coords.left, height: coords.height, width: coords.width}
      var context = this
      $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        url: 'http://127.0.0.1:5000/getTextForSelection',
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, HEAD, OPTIONS'
        },
        success: function (msg) {
          context.selections.push({
            id: +new Date(),
            coordinates: {
              top: coords.top,
              left: coords.left,
              height: coords.height,
              width: coords.width,
              page: coords.page,
              pageOffset: coords.pageOffset
            },
            color: 'rgb(255, 0, 0)',
            name: 'Unnamed' + context.selections.length,
            marks: 0,
            textData: msg['textData'],
            type: 'Main Question',
            qnum: 0,
            qtype: 'Descriptive',
            options: []
          })
          context.selections.sort(context.compareFunc)
        },
        error: function (request, status, error) {
          console.log(error)
        },
        data: JSON.stringify(this.inputData)
      })
    },
    addSelectionById: function (data) {
      this.selections.push(data)
    },
    deleteSelection: function (id) {
      this.selections = this.selections.filter(selection => selection.id !== id)
    },
    newFile: function (data) {
      this.name = data.name
      this.src = data.src
      this.arrayBuffer = data.arrayBuffer
      this.selections = []
    },
    updateSelectionById: function (id, data) {
      this.deleteSelection(id)
      this.addSelectionById(data)
    },
    getComplement: function (id) {
      var i = 0
      var j = 0
      for (i = 0; i < this.selections.length; i++) {
        if (this.selections[i].id === id) {
          break
        }
      }
      var type = this.selections[i].type
      if (type === 'Main Question') {
        for (j = i + 1; j < this.selections.length; j++) {
          if (this.selections[j].type !== type) {
            if (this.selections[j].type === 'Sub Question') {
              return ''
            } else {
              return this.selections[j].textData
            }
          }
        }
      } else if (type === 'Sub Question') {
        for (j = i + 1; j < this.selections.length; j++) {
          if (this.selections[j].type !== type) {
            return this.selections[j].textData
          }
        }
      } else {
        for (j = i - 1; j >= 0; j--) {
          if (this.selections[j].type !== type) {
            return this.selections[j].textData
          }
        }
      }
      return ''
    },
    getSelectionById: function (id) {
      this.tempSelectionArr = this.selections.filter(selection => selection.id === id)
      return this.tempSelectionArr[0]
    },
    changeMarksScale: function (newTotalMarks, newTimeGiven) {
      this.marksScale = (newTimeGiven * 1.0) / newTotalMarks
    },
    getSelections: function () {
      return this.selections
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>

.editor {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  margin-top: 60px;
}

.sidebar {
  position: absolute;
  width: 400px;
  top: 0;
  left: 0;
  padding: 10px;
}

.content {
  position: absolute;
  width: auto;
  margin-left: 30px;
  top: 0px;
  left: 410px;
}

textarea {
  -webkit-box-sizing: border-box;
   -moz-box-sizing: border-box;
        box-sizing: border-box;
  font-size: 1em;
}

h2 {
  background: #FFF800;
  padding: 10px 25px;
}

h1 {
  background: #C50080;
  padding: 10px 25px;
  color: white;
}
</style>
