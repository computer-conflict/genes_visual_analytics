<template>
  <client-only>
    <div class="h-screen block">
      <div v-if="errorLoading">
        {{ "Error al cargar la grafica" }}
      </div>
    
      <div class="flex grow justify-center">
        <feedback-waiting v-if="plot_pending" />
      </div>

      <div 
        v-show="showFilters"
      >
        <multiselect
          v-model="selectedOptions"
          :options="samples"
          :multiple="true"
          :close-on-select="false"
          :clear-on-select="false"
          :preserve-search="true"
          placeholder="Select samples to inspect"
          label="name"
          track-by="name"
          :preselect-first="true"
        />
      </div>


    
      <div
        v-show="!plot_pending"
        id="main_plot"
        ref="plot"
        class="flex flex-col justify-center m-5 mx-10"
      />
    </div>
  </client-only>
</template>

<script setup>
// -- Imports -- //
import * as Bokeh from '@bokeh/bokehjs'
import Multiselect from 'vue-multiselect'

// -- Data -- //
const config = useRuntimeConfig()
const plot = ref(null);
const errorLoading = ref(false)


const showFilters = ref(false)
const availablesSets = ref(['HiSeqV2_PANCAN'])
const set_name = ref('HiSeqV2_PANCAN')
const samples = ref([])
const selectedOptions = ref([])

const plotUrl = computed(() => {
  const samples = selectedOptions.value.length > 0 ? selectedOptions.value.map( (val) => val['value']) : -1
  return `${config.public.api.baseUrl}/plot?samples=${samples}`
})
const {data: plot_data, error: plot_error, pending: plot_pending} = useFetch(plotUrl, {
  method: 'GET',
  server: false,
  transform: (data) => {
    return data
  },
})
watch(plot_error, () => {
  errorLoading.value = true
})
watch(plot_data, (value) => {
  if(plot.value.firstChild) plot.value.removeChild(plot.value.firstChild)
  errorLoading.value = false
  Bokeh.embed.embed_item(JSON.parse(value), plot.value)
})

const {data: sample_filter_data, error: sample_filter_error} = useFetch(
  `${config.public.api.baseUrl}/get_samples?set_name=${set_name.value}`, {
  method: 'GET',
  server: false,
  transform: (data) => {
    return data
  },
})
watch(sample_filter_error, () => {
  showFilters.value = false
})
watch(sample_filter_data, (value) => {
  samples.value = value.map((v) => ({'name': v['name'], 'value': v['value']}))
  showFilters.value = true
})
</script>
<style lang="scss" scoped>
#main_plot {
  > :first-child {
    width: -webkit-fill-available;
  }
}
      
</style>