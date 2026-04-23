<script setup>
import { ref } from 'vue';

defineProps({
  filters: {
    type: Array,
    default: () => ['All', 'Draft', 'Pending', 'Paid']
  },
  selected: {
    type: String,
    default: 'All'
  }
});

defineEmits(['filter-change']);

const isOpen = ref(false);
</script>

<template>
  <div class="filter-bar">
    <button class="filter-button" @click="isOpen = !isOpen">
      Filter by status
      <svg class="dropdown-arrow" :class="{ open: isOpen }" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
    
    <div v-if="isOpen" class="filter-dropdown">
      <div 
        v-for="filter in filters" 
        :key="filter"
        class="filter-option"
        @click="() => { $emit('filter-change', filter); isOpen = false; }"
        :class="{ active: selected === filter }"
      >
        {{ filter }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-bar {
  position: relative;
  display: inline-block;
}

.filter-button {
  padding: 0.75rem 1rem;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  color: var(--text-primary);
  transition: all 0.2s;
}

.filter-button:hover {
  border-color: var(--text-primary);
  background-color: var(--bg-secondary);
}

.filter-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  min-width: 150px;
  z-index: 10;
  margin-top: 0.5rem;
}

.filter-option {
  padding: 0.75rem 1rem;
  cursor: pointer;
  color: var(--text-primary);
  transition: background-color 0.2s;
}

.filter-option:hover {
  background-color: var(--bg-secondary);
}

.filter-option.active {
  background-color: #0d1b2a;
  color: white;
}

.filter-option:first-child {
  border-radius: 0.5rem 0.5rem 0 0;
}

.filter-option:last-child {
  border-radius: 0 0 0.5rem 0.5rem;
}

.dropdown-arrow {
  width: 0.6rem;
  height: 0.6rem;
  margin-left: 0.5rem;
  transition: transform 0.2s;
  display: inline-block;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}
</style>