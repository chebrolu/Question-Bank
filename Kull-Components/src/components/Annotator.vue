<template>
  <div>
    <h3 v-if="name">
      Currently working on: <span class="filename">{{ name }}</span>
      <span class="filetype">{{ arrayBuffer ? "PDF" : "image" }}</span>
    </h3>
    <p>If you want to zoom in/out, you'll need to use your browser zoom for the moment.</p>
    <div class='selection-area' @mousedown="start" @mouseup="end" @mousemove="drag" v-if="src || arrayBuffer" ref="selectionArea">
      <img :src="src" v-if="src">
      <PDF :setPdfSize="setPdfSize" :arrayBuffer="arrayBuffer" v-if="arrayBuffer"></PDF>
      <SelectionPreview :coordinates="coordinates" v-if="arrayBuffer"></SelectionPreview>
      <AreaSelect :coordinates="coordinates" ref="activeSelector" color="rgb(0,255,0)" active="true" :showButton="false"></AreaSelect>
      <AreaSelect v-for="selection in selections"
        :key="selection.id"
        :color="selection.color"
        :coordinates="selection.coordinates"
        :name="selection.name"
        :deleteAreaSelection="deleteAreaSelection"
        :id="selection.id"
        :showButton="true"
        :getSelectionById="getSelectionById"
        :updateSelectionById="updateSelectionById"
        :getComplement="getComplement"
        :marksScale="marksScale"
      ></AreaSelect>
    </div>
  </div>
</template>

<script>
import AreaSelect from '@/components/AreaSelect'
import PDF from '@/components/PDF'
import SelectionPreview from '@/components/SelectionPreview'

export default {
  name: 'Annotator',
  components: {
    AreaSelect,
    PDF,
    SelectionPreview
  },
  props: ['src', 'name', 'selections', 'addSelection', 'deleteSelection', 'arrayBuffer', 'setPdfSize', 'updateSelectionById', 'getComplement', 'getSelectionById', 'marksScale'],
  data () {
    return {
      down: false,
      coords: {
        xa: null,
        ya: null,
        xb: null,
        yb: null
      },
      pageNumber: 1,
      pageOffset: {
        top: 0,
        left: 0
      }
    }
  },
  computed: {
    coordinates () {
      return {
        left: Math.min(this.coords.xa, this.coords.xb),
        top: Math.min(this.coords.ya, this.coords.yb),
        width: Math.abs(this.coords.xa - this.coords.xb),
        height: Math.abs(this.coords.ya - this.coords.yb),
        page: this.pageNumber,
        pageOffset: {
          top: this.pageOffset.top,
          left: this.pageOffset.left
        }
      }
    }
  },
  methods: {
    reset: function () {
      this.coords.xa = null
      this.coords.ya = null
      this.coords.xb = null
      this.coords.yb = null
    },
    start: function (event) {
      // event.stopPropagation()
      // event.preventDefault()
      this.down = true

      this.pageNumber = parseInt(event.target.getAttribute('data-page-number') || 1)
      this.pageOffset.top = event.target.offsetTop
      this.pageOffset.left = event.target.offsetLeft
      this.coords.xa = event.offsetX
      this.coords.ya = event.offsetY
      this.coords.xb = event.offsetX
      this.coords.yb = event.offsetY
      // console.log(event.target)
      // console.log(event)
      // console.log(this.pageOffset.top)
    },
    end: function (event) {
      event.stopPropagation()
      event.preventDefault()
      this.down = false
      // console.log(this.coordinates)
      this.addSelection(this.coordinates)
      this.reset()
      // console.log('End being called ----------')
    },
    drag: function (event) {
      event.stopPropagation()
      event.preventDefault()
      if (this.down) {
        this.coords.xb = event.offsetX
        this.coords.yb = event.offsetY
        // console.log('coords')
        // console.log(event.offsetX)
        // console.log(event.offsetY)
        // console.log(this.coords.xb)
        // console.log(this.coords.yb)
        // console.log(this.coords.xa)
        // console.log(this.coords.ya)
      }
    },
    deleteAreaSelection: function (key) {
      this.deleteSelection(key)
    }
  }
}
</script>

<style scoped>
.selection-area {
  position: relative;
  display: inline-block;
  outline: solid 1px black;
}

h3 span.filename {
  padding: 0px 15px;
  background: #FFF800;
}

h3 span.filetype {
  text-transform: lowercase;
  font-size: 0.75em;
  background: black;
  color: white;
  border-radius: 10px;
  padding: 2px 12px;
}
</style>
