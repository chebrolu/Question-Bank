<template>
    <modal 
      name="modalAdaptive"
      transition="nice-modal-fade"
      :min-width="200"
      :min-height="300"
      :delay="100"
      :adaptive="true" 
      @before-open="beforeOpen">
    <div class="example-modal-content">
      
      <form>
        <select v-model="type">
          <option>Main Question</option>
          <option>Sub Question</option>
          <option>Answer</option>
        </select> <br>
        <!-- Question Number : <input v-model="qnum"> <br> -->
        Marks : <input v-model="marks"> <br>
        Scale : {{marksScale}}
      </form>
      <textarea type="text" name="text_data" ref="text_data" v-model="textData" style="width:300px; height:100px"></textarea> <br>
      <div v-for="(opt, id) in options"
        :key="id"
      >
        Option {{id + 1}} : <input type="text" v-model="opt.optionText">
      </div>
        
      </input>
      <button class="button-class" @click="saveData">Save Changed Data</button>
      <button class="button-class" @click="closeModal">Close Model</button>
    
    </div>
  </modal>
</template>
<script>
export default {
  name: 'modalAdaptive',
  methods: {
    closeModal: function () {
      this.$modal.hide('modalAdaptive')
    },
    beforeOpen (event) {
      this.id = event.params.id
      this.updateSelectionById = event.params.updateSelectionById
      this.getSelectionById = event.params.getSelectionById
      this.marksScale = event.params.marksScale
      this.localSelection = this.getSelectionById(this.id)
      this.type = this.localSelection.type
      this.marks = this.localSelection.marks
      this.qnum = this.localSelection.qnum
      this.textData = this.localSelection.textData
      this.options = this.localSelection.options
      this.questionType = this.localSelection.question_type
    },
    saveData (event) {
      this.$modal.hide('modalAdaptive')
      this.localSelectionUpdated = this.localSelection
      this.localSelectionUpdated.name = this.selectionName
      this.localSelectionUpdated.marks = this.marks
      this.localSelectionUpdated.type = this.type
      this.localSelectionUpdated.qnum = this.qnum
      this.localSelectionUpdated.textData = this.textData
      this.localSelectionUpdated.color = this.color_type_map[this.type]
      this.updateSelectionById(this.id, this.localSelectionUpdated)
    }
  },
  data: function () {
    return {
      id: '',
      updateSelectionById: '',
      getSelectionById: '',
      localSelection: '',
      selectionName: '',
      localSelectionUpdated: '',
      type: '',
      marks: '',
      qnum: '',
      textData: '',
      marksScale: '',
      color_type_map: {'Main Question': 'rgb(255, 0, 0)', 'Answer': 'rgb(0, 255, 0)', 'Sub Question': 'rgb(0, 0, 255)'},
      questionType: '',
      options: []
    }
  }
}

</script>

<style scoped>

.button-class {
  pointer-events: auto;
}

.example-modal-content{
  pointer-events: auto;
}

</style>
