<script setup>
defineEmits(['click']);
</script>

<template>
  <div class="new-invoice-btn" @click="$emit('click')">
    <div class="plus-circle">
      <span class="plus">+</span>
    </div>
    <span class="text">New Invoice</span>
  </div>
</template>

<style scoped>
.new-invoice-btn {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background-color: #7c3aed;
  padding: 0.6rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: fit-content;
}

.new-invoice-btn:hover {
  background-color: #6d28d9;
  transform: scale(1.05);
}

.plus-circle {
  width: 1.5rem;
  height: 1.5rem;
  background-color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.plus {
  font-size: 1rem;
  color: #7c3aed;
  font-weight: bold;
  line-height: 1;
}

.text {
  color: white;
  font-weight: 500;
  font-size: 0.9rem;
}
</style>
