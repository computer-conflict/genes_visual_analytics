<template>
 <div class="flex flex-col justify-center m-10">
    <div class="flex items-center border-b border-verdigris-500 py-2 mx-40">
      <input 
       id="searcher" type="text"
       v-model="query" 
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
 </div>
</template>
<script setup>
// -- Data -- //
const query = ref('')

const {data, error, refresh} = useFetch()


</script>
<style lang="scss" scoped>

</style>