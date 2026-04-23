<script setup>
import { ref } from 'vue';

const isOpen = ref(false);
const selectedFilter = ref('All');

const filters = ['All', 'Draft', 'Pending', 'Paid'];

const selectFilter = (filter) => {
  selectedFilter.value = filter;
  isOpen.value = false;
};
</script>

<template>
  <div class="filter-bar">
    <button class="filter-button" @click="isOpen = !isOpen">
      Filter by status: {{ selectedFilter }}
    </button>
    
    <div v-if="isOpen" class="filter-dropdown">
      <div 
        v-for="filter in filters" 
        :key="filter"
        class="filter-option"
        @click="selectFilter(filter)"
        :class="{ active: selectedFilter === filter }"
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
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.filter-button:hover {
  border-color: #0d1b2a;
  background-color: #f9f9f9;
}

.filter-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  min-width: 150px;
  z-index: 10;
  margin-top: 0.5rem;
}

.filter-option {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.filter-option:hover {
  background-color: #f0f0f0;
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
</style>