import React from 'react';
import './NewInvoice.css';

const NewInvoice = ({ onClick }) => {
  return (
    <div className="new-invoice-btn" onClick={onClick}>
      <div className="plus-circle">
        <span className="plus">+</span>
      </div>
      <span className="text">New Invoice</span>
    </div>
  );
};

export default NewInvoice;
