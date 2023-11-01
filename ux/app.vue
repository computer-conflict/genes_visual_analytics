<template>
  <div class="h-full flex flex-col justify-between">
    <header class="shadow">
      <Navigation />
    </header>
    <NuxtLayout>
      <NuxtPage class="page" />
    </NuxtLayout>
    <footer class="flex justify-center mt-4 shadow">
      <div class="w-full max-w-screen-xl mx-5 py-8">
        <ul class="flex flex-wrap justify-end text-sm font-medium mb-0 text-gray-600">
          <li>
              <a href="#" class="hover:underline">Contacto</a>
          </li>
        </ul>
        <hr class="my-5 border-gray-200 sm:mx-auto dark:border-gray-700" />
        <span class="block text-sm text-center mt-2"> 2023 Chromagens.</span>
      </div>
    </footer>
  </div>
</template>


<style lang="scss">
.page{
  min-height: calc(85vh);
}

.logo-img {
  max-inline-size: 100%;
  block-size: auto;
  max-height: 50px !important;
  max-width: 50px !important;
}
</style>