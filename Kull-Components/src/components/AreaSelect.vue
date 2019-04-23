<template>
  <div class='selection-box' :style="styleObject">
    <modalAdaptive :id="id" :updateSelectionById="updateSelectionById" :getSelectionById="getSelectionById" :getComplement="getComplement">
    </modalAdaptive>
    <modals-container />
    <span>{{ name }}</span>
    <button class="button-class" type="button" v-on:click="deleteAreaSelect" v-if="showButton">Del</button>
    <button
      class="button-class"
      @click="$modal.show('modalAdaptive', 
      {
        id: id,
        updateSelectionById: updateSelectionById,
        getSelectionById: getSelectionById,
        getComplement: getComplement,
        marksScale: marksScale
      })"
      v-if="showButton">
      Edit
    </button>
    <!-- <button type="button">Del</button> -->
  </div>
</template>

<script>
import modalAdaptive from './Modal.vue'

export default {
  name: 'area-select',
  props: ['coordinates', 'color', 'name', 'active', 'id', 'deleteAreaSelection', 'showButton', 'updateSelectionById', 'getComplement', 'getSelectionById', 'marksScale'],
  components: {
    modalAdaptive
  },
  computed: {
    styleObject: function () {
      if (this.height === 0 || this.width === 0) {
        return {
          display: 'none'
        }
      }
      return {
        left: this.coordinates.left + this.coordinates.pageOffset.left + 'px',
        top: this.coordinates.top + this.coordinates.pageOffset.top + 'px',
        width: this.coordinates.width + 'px',
        height: this.coordinates.height + 'px',
        border: 'solid ' + this.color + ' 1px',
        background: this.color.replace(/\)$/, ', 0.05)').replace('rgb(', 'rgba(')
      }
    }
  },
  methods: {
    deleteAreaSelect: function (event) {
      this.deleteAreaSelection(this.id)
    }
  }
}
</script>

<style scoped>
.selection-box {
  position: absolute;
  pointer-events: none;
  text-align: center;
  z-index: 1000;
}

.button-class {
  pointer-events: auto;
}

span {
  color: black;
  display: inline;
  position: relative;
  font-weight: bold;
  font-size: 12px;
  text-shadow: white 0px 0px 2px, white 0px 0px 2px, white 0px 0px 5px, white 0px 0px 5px, white 0px 0px 30px, white 0px 0px 30px, white 0px 0px 30px, white 0px 0px 30px, white 0px 0px 30px, white 0px 0px 60px, white 0px 0px 60px, white 0px 0px 60px;
}
</style>
