<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import SideBar from '../components/SideBar.vue';

const router = useRouter();
const route = useRoute();

const invoice = ref(null);
const showDeleteModal = ref(false);

const loadInvoice = () => {
  try {
    const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
    invoice.value = invoices.find(inv => inv.id === route.params.id);
  } catch (error) {
    console.error('Error loading invoice:', error);
  }
};

const markAsPaid = () => {
  if (invoice.value) {
    invoice.value.status = 'paid';
    saveInvoice();
  }
};

const editInvoice = () => {
  router.push(`/new-invoice?id=${invoice.value.id}`);
};

const deleteInvoice = () => {
  showDeleteModal.value = false;
  try {
    const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
    const filtered = invoices.filter(inv => inv.id !== route.params.id);
    localStorage.setItem('invoices', JSON.stringify(filtered));
    router.push('/');
  } catch (error) {
    console.error('Error deleting invoice:', error);
  }
};

const saveInvoice = () => {
  try {
    const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
    const index = invoices.findIndex(inv => inv.id === invoice.value.id);
    if (index >= 0) {
      invoices[index] = invoice.value;
      localStorage.setItem('invoices', JSON.stringify(invoices));
    }
  } catch (error) {
    console.error('Error saving invoice:', error);
  }
};

const getTotalAmount = () => {
  if (!invoice.value) return 0;
  return invoice.value.items.reduce((sum, item) => sum + (item.quantity * item.price), 0);
};

onMounted(() => {
  loadInvoice();
});
</script>

<template>
  <div class="detail-container" v-if="invoice">
    <SideBar />
    <main class="detail-content">
      <div class="detail-wrapper">
        <div class="detail-header">
          <router-link to="/" class="back-btn">← Back to Invoices</router-link>
          <div class="header-actions">
            <button class="btn-edit" @click="editInvoice">Edit</button>
            <button class="btn-delete" @click="showDeleteModal = true">Delete</button>
            <button v-if="invoice.status !== 'paid'" class="btn-pay" @click="markAsPaid">Mark as Paid</button>
          </div>
        </div>

        <!-- Invoice Details -->
        <div class="invoice-detail">
          <div class="invoice-header-info">
            <div>
              <h1>{{ invoice.id }}</h1>
              <p class="status-badge" :class="invoice.status">{{ invoice.status }}</p>
            </div>
          </div>

          <!-- Bill From / Bill To -->
          <div class="bill-info">
            <div class="bill-section">
              <h3>Bill From</h3>
              <p>{{ invoice.billFrom.streetAddress }}</p>
              <p>{{ invoice.billFrom.city }}, {{ invoice.billFrom.postCode }}</p>
              <p>{{ invoice.billFrom.country }}</p>
            </div>
            <div class="bill-section">
              <h3>Bill To</h3>
              <p><strong>{{ invoice.billTo.clientName }}</strong></p>
              <p>{{ invoice.billTo.streetAddress }}</p>
              <p>{{ invoice.billTo.city }}, {{ invoice.billTo.postCode }}</p>
              <p>{{ invoice.billTo.country }}</p>
              <p>{{ invoice.billTo.clientEmail }}</p>
            </div>
          </div>

          <!-- Invoice Dates -->
          <div class="dates-info">
            <div class="date-item">
              <p class="label">Invoice Date</p>
              <p class="value">{{ invoice.invoiceDate }}</p>
            </div>
            <div class="date-item">
              <p class="label">Payment Terms</p>
              <p class="value">{{ invoice.paymentTerms }}</p>
            </div>
          </div>

          <!-- Project Description -->
          <div class="description">
            <h3>Project Description</h3>
            <p>{{ invoice.projectDescription }}</p>
          </div>

          <!-- Items Table -->
          <table class="items-table">
            <thead>
              <tr>
                <th>Item Name</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in invoice.items" :key="index">
                <td>{{ item.name }}</td>
                <td>{{ item.quantity }}</td>
                <td>£ {{ item.price.toFixed(2) }}</td>
                <td>£ {{ (item.quantity * item.price).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Total -->
          <div class="invoice-total">
            <span>Total Amount Due</span>
            <span class="amount">£ {{ getTotalAmount().toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </main>

    <!-- Delete Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal" @click.stop>
        <h2>Confirm Delete</h2>
        <p>Are you sure you want to delete this invoice? This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showDeleteModal = false">Cancel</button>
          <button class="btn-confirm-delete" @click="deleteInvoice">Delete</button>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="detail-container">
    <SideBar />
    <main class="detail-content">
      <p>Invoice not found</p>
    </main>
  </div>
</template>

<style scoped>
.detail-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--bg-secondary);
}

.detail-content {
  flex: 1;
  margin-left: 6rem;
  overflow-y: auto;
  padding: 2rem;
  background-color: var(--bg-secondary);
}

.detail-wrapper {
  max-width: 900px;
  margin: 0 auto;
  background-color: var(--bg-primary);
  padding: 2rem;
  border-radius: 0.75rem;
  color: var(--text-primary);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.back-btn {
  color: #7c3aed;
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s;
}

.back-btn:hover {
  color: #6d28d9;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.header-actions button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.btn-edit {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-edit:hover {
  background-color: var(--border-color);
}

.btn-delete {
  background-color: rgba(255, 87, 87, 0.1);
  color: #ff5757;
  border: 1px solid rgba(255, 87, 87, 0.2);
}

.btn-delete:hover {
  background-color: rgba(255, 87, 87, 0.2);
}

.btn-pay {
  background-color: #7c3aed;
  color: white;
}

.btn-pay:hover {
  background-color: #6d28d9;
}

.invoice-header-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.invoice-header-info h1 {
  font-size: 2rem;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.status-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 0.25rem;
  font-weight: 600;
  font-size: 0.85rem;
  margin: 0;
}

.status-badge.draft {
  background-color: #e2e3e5;
  color: #383d41;
}

.status-badge.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.paid {
  background-color: #d4edda;
  color: #155724;
}

.bill-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.bill-section h3 {
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  margin: 0 0 0.75rem 0;
}

.bill-section p {
  margin: 0.25rem 0;
  color: var(--text-primary);
  line-height: 1.6;
}

.dates-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: var(--bg-secondary);
  border-radius: 0.5rem;
}

.date-item .label {
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.85rem;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
}

.date-item .value {
  color: var(--text-primary);
  font-weight: 600;
  margin: 0;
  font-size: 1rem;
}

.description {
  margin-bottom: 2rem;
}

.description h3 {
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  margin: 0 0 0.75rem 0;
}

.description p {
  color: var(--text-primary);
  margin: 0;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 2rem;
  background-color: var(--card-bg);
}

.items-table thead {
  background-color: var(--bg-secondary);
  border-bottom: 2px solid var(--border-color);
}

.items-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.items-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.invoice-total {
  display: flex;
  justify-content: flex-end;
  gap: 2rem;
  padding: 1.5rem;
  background-color: #0d1b2a;
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1.1rem;
}

.invoice-total .amount {
  min-width: 150px;
  text-align: right;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background-color: var(--bg-primary);
  padding: 2rem;
  border-radius: 0.75rem;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  color: var(--text-primary);
}

.modal h2 {
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
}

.modal p {
  color: var(--text-secondary);
  margin: 0 0 1.5rem 0;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.modal-actions button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-cancel:hover {
  background-color: var(--border-color);
}

.btn-confirm-delete {
  background-color: #ff5757;
  color: white;
}

.btn-confirm-delete:hover {
  background-color: #ff2e2e;
}
</style>
