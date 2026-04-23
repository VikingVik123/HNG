<script setup>
</script>

<template>
  <div class="empty-state">
    <div class="empty-icon">
      <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <!-- Envelope -->
        <rect x="30" y="60" width="140" height="90" fill="none" stroke="#7c3aed" stroke-width="2" rx="5"/>
        <path d="M 30 60 L 100 110 L 170 60" fill="none" stroke="#7c3aed" stroke-width="2"/>
        
        <!-- Megaphone -->
        <circle cx="140" cy="50" r="15" fill="#7c3aed"/>
        <path d="M 155 50 L 175 40 L 175 60 Z" fill="#7c3aed"/>
      </svg>
    </div>
    <h2>There is nothing here</h2>
    <p>Create an invoice by clicking the <span class="highlight">New Invoice</span> button and get started</p>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.empty-icon {
  width: 12rem;
  height: 12rem;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

h2 {
  font-size: 1.75rem;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  font-weight: 700;
}

p {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0;
  max-width: 400px;
}

.highlight {
  color: #7c3aed;
  font-weight: 600;
}
</style>
