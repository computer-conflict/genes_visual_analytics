<template>
  <div class="flex flex-col justify-center m-10">
    <div class="flex items-center border-b border-verdigris-500 py-2 mx-40">
      <input 
        id="searcher"
        v-model="query"
        type="text" 
        class="appearance-none bg-transparent border-none w-full text-gray-700 mr-3 py-1 px-2 leading-tight focus:outline-none"
        placeholder="Gen searcher" 
        aria-label="Full name"
      >
      <button 
        class="flex-shrink-0 bg-verdigris-500 hover:bg-verdigris-700 border-verdigris-500 hover:border-verdigris-700 text-sm border-4 text-black py-1 px-2 rounded" 
        type="button"
        @click="refresh()"
      >
        Search
      </button>
    </div>
    <div class="flex flex-col justify-center m-10">
      <div
        v-for="(card, index) in genCards"
        :key="index"
        class="flex flex-col mb-10"
      >
        <h2 class="text-xl">
          {{ card.name }}
        </h2>
        <a class="font-thin font-extralight">{{ card.description }}</a>
      </div>
    </div>
  </div>
</template>
<script setup>
// -- Data -- //
const query = ref('')
const config = useRuntimeConfig()
const genCards = ref([])

const searchUrl = () => {
  const params = `?query_text=${encodeURIComponent(query.value)}&n_results=5`
  return `${config.public.api.baseUrl}/search${params}`
}

const {data, error, refresh} = useFetch(searchUrl, {
  method: 'GET',
  server: false,
  immediate: false,
  transform: (data) => {
    return transformResponse('genCards', data)
  },
})
watch(error, (value) => {
  if (value)
    console.log(value)
})
watch(data, (value) => {
  genCards.value = value
})

</script>
<style lang="scss" scoped>

</style>

