<template>
  <div class="h-screen flex flex-col justify-center ">
    <div v-if="errorLoading">
      {{ "Error al cargar la grafica" }}
    </div>
    
    <div class="flex grow justify-center">
      <FeedbackWaiting v-if="pending" />
    </div>
    
    <div
      v-show="!pending"
      id="main_plot"
      ref="plot"
      class="flex flex-col justify-center m-5 mx-10"
    />
  </div>
</template>
<script setup>
// -- Imports -- //
import * as Bokeh from '@bokeh/bokehjs'

// -- Data -- //
const config = useRuntimeConfig()
const plot = ref(null);
const errorLoading = ref(false)
const plotUrl = () => {
  return `${config.public.api.baseUrl}/plot`
}

const {data, error, pending} = useFetch(plotUrl, {
  method: 'GET',
  server: false,
  transform: (data) => {
    return data
  },
})
watch(error, () => {
  errorLoading.value = true
})
watch(data, (value) => {
  errorLoading.value = false
  Bokeh.embed.embed_item(JSON.parse(value), plot.value)
})

</script>
<style lang="scss" scoped>
#main_plot {

  > :first-child {
    width: -webkit-fill-available;
  }
}
      
</style>