<script setup>
import SideBar from '../components/SideBar.vue'
import HeadComp from '../components/HeadComp.vue'
import InvBox from '../components/InvBox.vue';
import FilterBar from '../components/FilterBar.vue';
</script>

<template>
  <div class="app-container">
    <SideBar />
    <main class="main-content">
      <div class="top-section">
        <HeadComp />
        <FilterBar />
      </div>
      <div class="invoices-section">
        <InvBox 
          id="INV-001"
          name="John Doe"
          dueDate="2024-07-15"
          amount="250.00"
          status="Pending"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.main-content {
  flex: 1;
  overflow: auto;
  margin-left: 8rem;
  display: flex;
  flex-direction: column;
}

.top-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: white;
  border-bottom: 1px solid #eee;
}

.invoices-section {
  flex: 1;
  overflow: auto;
  padding: 1rem;
}
</style>