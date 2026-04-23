import React from 'react';
import './EmptyState.css';

const EmptyState = () => {
  return (
    <div className="empty-state">
      <div className="empty-icon">📋</div>
      <h2>No invoices</h2>
      <p>Create your first invoice to get started</p>
    </div>
  );
};

export default EmptyState;
