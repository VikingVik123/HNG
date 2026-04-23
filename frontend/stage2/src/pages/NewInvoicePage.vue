<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import SideBar from '../components/SideBar.vue';

const router = useRouter();
const route = useRoute();
const errors = ref({});
const isEditing = computed(() => !!route.query.id);

const formData = ref({
  id: '',
  billFrom: {
    streetAddress: '',
    city: '',
    postCode: '',
    country: ''
  },
  billTo: {
    clientName: '',
    clientEmail: '',
    streetAddress: '',
    city: '',
    postCode: '',
    country: ''
  },
  invoiceDate: new Date().toISOString().split('T')[0],
  paymentTerms: 'Net 30 Days',
  projectDescription: '',
  items: [
    { name: '', quantity: 1, price: 0, total: 0 }
  ],
  status: 'draft'
});

const loadInvoiceForEditing = () => {
  if (route.query.id) {
    try {
      const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
      const invoice = invoices.find(inv => inv.id === route.query.id);
      if (invoice) {
        formData.value = { ...invoice };
      }
    } catch (error) {
      console.error('Error loading invoice:', error);
    }
  }
};

const validateForm = () => {
  errors.value = {};

  // Validate Bill From
  if (!formData.value.billFrom.streetAddress.trim()) {
    errors.value.billFromStreet = 'Street address is required';
  }
  if (!formData.value.billFrom.city.trim()) {
    errors.value.billFromCity = 'City is required';
  }
  if (!formData.value.billFrom.postCode.trim()) {
    errors.value.billFromPostCode = 'Post code is required';
  }
  if (!formData.value.billFrom.country.trim()) {
    errors.value.billFromCountry = 'Country is required';
  }

  // Validate Bill To
  if (!formData.value.billTo.clientName.trim()) {
    errors.value.clientName = 'Client name is required';
  }
  if (!formData.value.billTo.clientEmail.trim()) {
    errors.value.clientEmail = 'Client email is required';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.value.billTo.clientEmail)) {
    errors.value.clientEmail = 'Please enter a valid email address';
  }
  if (!formData.value.billTo.streetAddress.trim()) {
    errors.value.billToStreet = 'Street address is required';
  }
  if (!formData.value.billTo.city.trim()) {
    errors.value.billToCity = 'City is required';
  }
  if (!formData.value.billTo.postCode.trim()) {
    errors.value.billToPostCode = 'Post code is required';
  }
  if (!formData.value.billTo.country.trim()) {
    errors.value.billToCountry = 'Country is required';
  }

  // Validate items
  if (formData.value.items.length === 0) {
    errors.value.items = 'At least one item is required';
  } else {
    formData.value.items.forEach((item, index) => {
      if (!item.name.trim()) {
        errors.value[`itemName${index}`] = 'Item name is required';
      }
      if (item.quantity <= 0) {
        errors.value[`itemQty${index}`] = 'Quantity must be greater than 0';
      }
      if (item.price < 0) {
        errors.value[`itemPrice${index}`] = 'Price must be a positive number';
      }
    });
  }

  return Object.keys(errors.value).length === 0;
};

const addItem = () => {
  formData.value.items.push({ name: '', quantity: 1, price: 0, total: 0 });
};

const removeItem = (index) => {
  if (formData.value.items.length > 1) {
    formData.value.items.splice(index, 1);
  }
};

const saveDraft = () => {
  if (!isEditing.value) {
    formData.value.id = formData.value.id || 'INV-' + Date.now();
  }
  formData.value.status = 'draft';
  saveInvoice();
};

const sendInvoice = () => {
  if (!validateForm()) {
    alert('Please fix the errors in the form');
    return;
  }
  
  if (!isEditing.value) {
    formData.value.id = formData.value.id || 'INV-' + Date.now();
  }
  formData.value.status = 'pending';
  saveInvoice();
};

const saveInvoice = () => {
  try {
    const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
    const existingIndex = invoices.findIndex(inv => inv.id === formData.value.id);
    
    if (existingIndex >= 0) {
      invoices[existingIndex] = formData.value;
    } else {
      invoices.push(formData.value);
    }
    
    localStorage.setItem('invoices', JSON.stringify(invoices));
    alert('Invoice saved successfully!');
    router.push('/');
  } catch (error) {
    console.error('Error saving invoice:', error);
    alert('Error saving invoice');
  }
};

const getError = (field) => {
  return errors.value[field] || '';
};

const hasError = (field) => {
  return !!errors.value[field];
};

onMounted(() => {
  loadInvoiceForEditing();
});
</script>

<template>
  <div class="invoice-form-container">
    <SideBar />
    <main class="form-content">
      <div class="form-wrapper">
        <h1>{{ isEditing ? 'Edit Invoice' : 'New Invoice' }}</h1>
        
        <form @submit.prevent>
          <!-- Bill From Section -->
          <div class="form-section">
            <label class="section-label">Bill From</label>
            <div class="form-group" :class="{ error: hasError('billFromStreet') }">
              <label>Street Address</label>
              <input v-model="formData.billFrom.streetAddress" type="text" placeholder="Street Address">
              <span v-if="hasError('billFromStreet')" class="error-message">{{ getError('billFromStreet') }}</span>
            </div>
            <div class="form-row">
              <div class="form-group" :class="{ error: hasError('billFromCity') }">
                <label>City</label>
                <input v-model="formData.billFrom.city" type="text" placeholder="City">
                <span v-if="hasError('billFromCity')" class="error-message">{{ getError('billFromCity') }}</span>
              </div>
              <div class="form-group" :class="{ error: hasError('billFromPostCode') }">
                <label>Post Code</label>
                <input v-model="formData.billFrom.postCode" type="text" placeholder="Post Code">
                <span v-if="hasError('billFromPostCode')" class="error-message">{{ getError('billFromPostCode') }}</span>
              </div>
              <div class="form-group" :class="{ error: hasError('billFromCountry') }">
                <label>Country</label>
                <input v-model="formData.billFrom.country" type="text" placeholder="Country">
                <span v-if="hasError('billFromCountry')" class="error-message">{{ getError('billFromCountry') }}</span>
              </div>
            </div>
          </div>

          <!-- Bill To Section -->
          <div class="form-section">
            <label class="section-label">Bill To</label>
            <div class="form-group" :class="{ error: hasError('clientName') }">
              <label>Client's Name</label>
              <input v-model="formData.billTo.clientName" type="text" placeholder="Client's Name">
              <span v-if="hasError('clientName')" class="error-message">{{ getError('clientName') }}</span>
            </div>
            <div class="form-group" :class="{ error: hasError('clientEmail') }">
              <label>Client's Email</label>
              <input v-model="formData.billTo.clientEmail" type="email" placeholder="Client's Email">
              <span v-if="hasError('clientEmail')" class="error-message">{{ getError('clientEmail') }}</span>
            </div>
            <div class="form-group" :class="{ error: hasError('billToStreet') }">
              <label>Street Address</label>
              <input v-model="formData.billTo.streetAddress" type="text" placeholder="Street Address">
              <span v-if="hasError('billToStreet')" class="error-message">{{ getError('billToStreet') }}</span>
            </div>
            <div class="form-row">
              <div class="form-group" :class="{ error: hasError('billToCity') }">
                <label>City</label>
                <input v-model="formData.billTo.city" type="text" placeholder="City">
                <span v-if="hasError('billToCity')" class="error-message">{{ getError('billToCity') }}</span>
              </div>
              <div class="form-group" :class="{ error: hasError('billToPostCode') }">
                <label>Post Code</label>
                <input v-model="formData.billTo.postCode" type="text" placeholder="Post Code">
                <span v-if="hasError('billToPostCode')" class="error-message">{{ getError('billToPostCode') }}</span>
              </div>
              <div class="form-group" :class="{ error: hasError('billToCountry') }">
                <label>Country</label>
                <input v-model="formData.billTo.country" type="text" placeholder="Country">
                <span v-if="hasError('billToCountry')" class="error-message">{{ getError('billToCountry') }}</span>
              </div>
            </div>
          </div>

          <!-- Invoice Date & Payment Terms -->
          <div class="form-row">
            <div class="form-group">
              <label>Invoice Date</label>
              <input v-model="formData.invoiceDate" type="date">
            </div>
            <div class="form-group">
              <label>Payment Terms</label>
              <select v-model="formData.paymentTerms">
                <option>Net 30 Days</option>
                <option>Net 60 Days</option>
                <option>Due on Receipt</option>
              </select>
            </div>
          </div>

          <!-- Project Description -->
          <div class="form-group">
            <label>Project Description</label>
            <input v-model="formData.projectDescription" type="text" placeholder="Project Description">
          </div>

          <!-- Item List -->
          <div class="form-section">
            <label class="section-label">Item List</label>
            <table class="items-table">
              <thead>
                <tr>
                  <th>Item Name</th>
                  <th>Qty</th>
                  <th>Price</th>
                  <th>Total</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in formData.items" :key="index">
                  <td>
                    <input v-model="item.name" type="text" placeholder="Item name"
                      :class="{ 'input-error': hasError(`itemName${index}`) }">
                    <span v-if="hasError(`itemName${index}`)" class="error-message">{{ getError(`itemName${index}`) }}</span>
                  </td>
                  <td>
                    <input v-model.number="item.quantity" type="number" min="1"
                      :class="{ 'input-error': hasError(`itemQty${index}`) }">
                    <span v-if="hasError(`itemQty${index}`)" class="error-message">{{ getError(`itemQty${index}`) }}</span>
                  </td>
                  <td>
                    <input v-model.number="item.price" type="number" min="0"
                      :class="{ 'input-error': hasError(`itemPrice${index}`) }">
                    <span v-if="hasError(`itemPrice${index}`)" class="error-message">{{ getError(`itemPrice${index}`) }}</span>
                  </td>
                  <td class="total">{{ (item.quantity * item.price).toFixed(2) }}</td>
                  <td><button type="button" class="delete-btn" @click="removeItem(index)">×</button></td>
                </tr>
              </tbody>
            </table>
            <button type="button" class="add-item-btn" @click="addItem">+ Add More Item</button>
          </div>
        </form>

        <!-- Action Buttons -->
        <div class="form-actions">
          <button type="button" class="btn-discard" @click="router.push('/')">Discard</button>
          <button type="button" class="btn-save-draft" @click="saveDraft">Save as Draft</button>
          <button type="button" class="btn-send" @click="sendInvoice">Save & Send</button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.invoice-form-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--bg-secondary);
}

.form-content {
  flex: 1;
  margin-left: 6rem;
  overflow-y: auto;
  padding: 2rem;
  background-color: var(--bg-secondary);
}

.form-wrapper {
  max-width: 800px;
  margin: 0 auto;
  background-color: var(--bg-primary);
  padding: 2rem;
  border-radius: 0.75rem;
  color: var(--text-primary);
}

h1 {
  font-size: 1.75rem;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  font-weight: 700;
}

.form-section {
  margin-bottom: 2rem;
}

.section-label {
  display: block;
  color: #7c3aed;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group.error input,
.form-group.error select {
  border-color: #ff5757 !important;
  background-color: rgba(255, 87, 87, 0.05);
}

.form-group label {
  display: block;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  background-color: var(--input-bg);
  color: var(--text-primary);
  border-radius: 0.5rem;
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
}

.error-message {
  display: block;
  color: #ff5757;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  background-color: var(--card-bg);
}

.items-table thead {
  background-color: var(--bg-secondary);
  border-bottom: 2px solid var(--border-color);
}

.items-table th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary);
}

.items-table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.items-table input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  background-color: var(--input-bg);
  color: var(--text-primary);
  border-radius: 0.25rem;
  font-size: 0.85rem;
}

.items-table input.input-error {
  border-color: #ff5757;
  background-color: rgba(255, 87, 87, 0.05);
}

.items-table .total {
  font-weight: 600;
  color: var(--text-primary);
}

.delete-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #ff5757;
  cursor: pointer;
  padding: 0;
  height: 1.5rem;
  width: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.delete-btn:hover {
  color: #ff2e2e;
}

.add-item-btn {
  color: #7c3aed;
  background: none;
  border: none;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.add-item-btn:hover {
  color: #6d28d9;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: flex-end;
}

.form-actions button {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  transition: all 0.3s;
}

.btn-discard {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-discard:hover {
  background-color: var(--border-color);
}

.btn-save-draft {
  background-color: #2d2d44;
  color: white;
}

.btn-save-draft:hover {
  background-color: #1a1a28;
}

.btn-send {
  background-color: #7c3aed;
  color: white;
}

.btn-send:hover {
  background-color: #6d28d9;
}
</style>

