<template>
  <div>
    <nav class="flex flex-row items-center justify-between m-5">
      <NuxtLink
        to="/"
        class="flex flex-row items-center gap-5"
      >
        <nuxt-img
          src="/images/logos/chromagens-logo.svg"
          alt="SVG image"
          sizes="100px sm:70px md:70px lg:70px"
          class="logo-img"
        />
        <span class="text-xl">CHROMAGENS</span>
      </NuxtLink>
      <div class="flex flex-row gap-10">
        <NuxtLink
          to="/graphs"
          class="flex flex-row items-center"
        >            
          <span class="text-l">Gráficas</span>
        </NuxtLink>
        <NuxtLink
          to="/searcher"
          class="flex flex-row items-center"
        >
          <span class="text-l">Buscador</span>
        </NuxtLink>
      </div>
      <div class="flex flex-row text-l">
        <NuxtLink
          to="/configuration"
          class="flex flex-row items-center"
        >
          Configuración
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>

<style lang="scss" scoped>
.logo-img {
  max-inline-size: 100%;
  block-size: auto;
  max-height: 50px !important;
  max-width: 50px !important;
}
</style>