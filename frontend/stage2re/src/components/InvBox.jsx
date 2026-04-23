import React from 'react';
import './InvBox.css';

const InvBox = ({ id, dueDate, name, amount, status, onClick }) => {
  if (!id) return null;

  return (
    <div className="invoice-box" onClick={onClick}>
      <div className="invoice-id">{id}</div>
      <div className="invoice-due-date">Due {dueDate}</div>
      <div className="invoice-name">{name}</div>
      <div className="invoice-amount">£ {amount}</div>
      <div className={`invoice-status ${status.toLowerCase()}`}>
        <span className="status-dot"></span>
        {status}
      </div>
      <div className="arrow-icon">›</div>
    </div>
  );
};

export default InvBox;
