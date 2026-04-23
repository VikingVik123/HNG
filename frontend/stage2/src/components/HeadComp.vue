<script setup>
import { ref } from 'vue';

const invoiceCount = ref(0);
</script>

<template>
  <div class="header">
    <h1>Invoices</h1>
    <p>{{ invoiceCount }} invoices</p>
  </div>
</template>

<style scoped>
.header {
  color: white;
  padding: 1rem;
}
</style>