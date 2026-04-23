<script setup>
defineProps({
  id: {
    type: String,
    default: ''
  },
  dueDate: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    default: ''
  },
  amount: {
    type: Number,
    default: 0
  },
  status: {
    type: String,
    default: 'draft'
  }
});
</script>

<template>
  <div class="invoice-box">
    <div class="box-content">
      <div class="invoice-id">{{ id }}</div>
      <div class="invoice-name">{{ name }}</div>
      <div class="invoice-due-date">{{ dueDate }}</div>
      <div class="invoice-amount">{{ amount }}</div>
      <div class="invoice-status" :class="status.toLowerCase()">{{ status }}</div>
    </div>
  </div>
</template>

<style scoped>
.invoice-box {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.box-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.invoice-id {
  font-weight: bold;
  color: #0d1b2a;
  min-width: 5rem;
}

.invoice-name {
  flex: 1;
  color: #333;
  font-size: 1rem;
}

.invoice-due-date {
  color: #666;
  font-size: 0.9rem;
  min-width: 6rem;
}

.invoice-amount {
  font-weight: bold;
  color: #0d1b2a;
  min-width: 5rem;
  text-align: right;
}

.invoice-status {
  padding: 0.4rem 0.8rem;
  border-radius: 0.25rem;
  font-size: 0.85rem;
  font-weight: 500;
  min-width: 4rem;
  text-align: center;
}

.invoice-status.paid {
  background-color: #d4edda;
  color: #155724;
}

.invoice-status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.invoice-status.overdue {
  background-color: #f8d7da;
  color: #721c24;
}

.invoice-status.draft {
  background-color: #e2e3e5;
  color: #383d41;
}
</style>
