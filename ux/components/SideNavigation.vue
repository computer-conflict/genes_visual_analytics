<template>
  <nav class="aside-nav">
    <h1 class="list-title border-b-1 ms-2 pb-3">
      {{ $t('settings.menu.title') }}
    </h1>
    <ul>
      <li
        v-for="(module, index) in modules"
        :key="index"
        class="mt-2"
        :class="{ active: selectedSection == module.component }"
        @click="updateConfigurationSection(module.component)"
      >
        <a class="ms-0 pb-1">
          <span>{{ module.name }} </span>
        </a>
      </li>
    </ul>
  </nav>
</template>
<script setup>
// -- Data --//
const { t: $t } = useI18n()

const modules = ref([
  { name: $t('settings.menu.global'), component: 'ConfigurationGlobal' },
  { name: $t('settings.menu.database'), component: 'ConfigurationDatabase'},
])

const selectedSection = ref('ConfigurationGlobal')

const updateConfigurationSection = (selectedComponent) => {
  selectedSection.value = selectedComponent
  useEvent('configuration:section', {section: selectedComponent})
}

</script>

<style lang="scss" scoped>
.aside-nav {
  background-color: #fff;
  border-right: 1px solid #e5e5e5;
  min-height: calc(100vh - 60px);
  height: auto;
  width: 12%;
  padding: 25px;

  .list-title {
    color: #5d5f66;
    font-size: 1em;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  li {
    cursor: pointer;
    padding: 4px 2px;
    border-radius: 5px;
    &:hover,
    &.active {
      background-color: #edeeee;
    }
  }
}
</style>
