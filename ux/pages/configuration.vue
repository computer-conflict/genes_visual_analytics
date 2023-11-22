<template>
  <div class="h-screen flex flex-col">
    <div class="flex flex-row flex-wrap grow">
      <SideNavigation
        class="mh-100"
      />

      <article
        class="px-8 pt-8"
        style="width: 88%;"
      >
        <component
          :is="sectionComponent"
        />
      </article>
    </div>
  </div>
</template>
<script setup>
const sectionComponent = ref('ConfigurationGlobal');
useListen('configuration:section', ({section}) => {
  sectionComponent.value = section;
});
</script>