<template>
  <div id="app">
    <simple-vue-form :action="'/api/post'" @ajaxSuccess="formSuccess" @ajaxError="formError">
      <input name="title"/>
      <textarea name="body"></textarea>
      <input type="submit"/>
    </simple-vue-form>
  </div>
</template>

<script>
import simpleVueForm from './components/simple_vue_form.vue'

export default {
  name: 'app',
  components: {
    'simple-vue-form': simpleVueForm
  },
  methods: {
    formSuccess (response) {
      console.log(response)
    },
    formError (response) {
      console.log(response)
    }
  }
}
</script>

