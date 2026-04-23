import React from 'react';
import './HeadComp.css';

const HeadComp = ({ count = 0 }) => {
  return (
    <div className="header">
      <h1>Invoices</h1>
      <p>There are {count} total invoices</p>
    </div>
  );
};

export default HeadComp;
