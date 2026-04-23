<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import SideBar from '../components/SideBar.vue'
import HeadComp from '../components/HeadComp.vue'
import InvBox from '../components/InvBox.vue';
import FilterBar from '../components/FilterBar.vue';
import NewInvoice from '../components/NewInvoice.vue';
import EmptyState from '../components/EmptyState.vue';

const router = useRouter();
const invoices = ref([]);
const selectedFilter = ref('All');

const filters = ['All', 'Draft', 'Pending', 'Paid'];

const filteredInvoices = computed(() => {
  if (selectedFilter.value === 'All') {
    return invoices.value;
  }
  return invoices.value.filter(inv => inv.status.toLowerCase() === selectedFilter.value.toLowerCase());
});

const loadInvoices = () => {
  try {
    const savedInvoices = localStorage.getItem('invoices');
    if (savedInvoices) {
      invoices.value = JSON.parse(savedInvoices);
    }
  } catch (error) {
    console.error('Error loading invoices:', error);
  }
};

const handleNewInvoice = () => {
  router.push('/new-invoice');
};

const handleFilterChange = (filter) => {
  selectedFilter.value = filter;
};

const handleInvoiceClick = (invoiceId) => {
  router.push(`/invoice/${invoiceId}`);
};

onMounted(() => {
  loadInvoices();
});
</script>

<template>
  <div class="app-container">
    <SideBar />
    <main class="main-content">
      <div class="content-wrapper">
        <div class="top-section">
          <HeadComp :count="filteredInvoices.length" />
          <div class="controls">
            <FilterBar :filters="filters" :selected="selectedFilter" @filter-change="handleFilterChange" />
            <NewInvoice @click="handleNewInvoice" />
          </div>
        </div>
        <div class="invoices-section">
          <EmptyState v-if="filteredInvoices.length === 0" />
          <InvBox 
            v-else
            v-for="invoice in filteredInvoices"
            :key="invoice.id"
            :id="invoice.id"
            :name="invoice.billTo.clientName"
            :dueDate="invoice.invoiceDate"
            :amount="invoice.items.reduce((sum, item) => sum + (item.quantity * item.price), 0)"
            :status="invoice.status"
            @click="handleInvoiceClick(invoice.id)"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--bg-secondary);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  margin-left: 6rem;
  height: 100vh;
  background-color: var(--bg-secondary);
  padding: 2rem;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
}

.top-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
}

.controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.invoices-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>