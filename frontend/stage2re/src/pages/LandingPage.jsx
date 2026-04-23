import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import SideBar from '../components/SideBar';
import HeadComp from '../components/HeadComp';
import InvBox from '../components/InvBox';
import FilterBar from '../components/FilterBar';
import NewInvoice from '../components/NewInvoice';
import EmptyState from '../components/EmptyState';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const [invoices, setInvoices] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState('All');

  const filters = ['All', 'Draft', 'Pending', 'Paid'];

  const loadInvoices = () => {
    try {
      const savedInvoices = localStorage.getItem('invoices');
      if (savedInvoices) {
        setInvoices(JSON.parse(savedInvoices));
      }
    } catch (error) {
      console.error('Error loading invoices:', error);
    }
  };

  useEffect(() => {
    loadInvoices();
  }, []);

  const filteredInvoices = useMemo(() => {
    if (selectedFilter === 'All') {
      return invoices;
    }
    return invoices.filter(
      (inv) => inv.status.toLowerCase() === selectedFilter.toLowerCase()
    );
  }, [invoices, selectedFilter]);

  const handleNewInvoice = () => {
    navigate('/new-invoice');
  };

  const handleFilterChange = (filter) => {
    setSelectedFilter(filter);
  };

  const handleInvoiceClick = (invoiceId) => {
    navigate(`/invoice/${invoiceId}`);
  };

  return (
    <div className="app-container">
      <SideBar />
      <main className="main-content">
        <div className="content-wrapper">
          <div className="top-section">
            <HeadComp count={filteredInvoices.length} />
            <div className="controls">
              <FilterBar
                filters={filters}
                selected={selectedFilter}
                onFilterChange={handleFilterChange}
              />
              <NewInvoice onClick={handleNewInvoice} />
            </div>
          </div>
          <div className="invoices-section">
            {filteredInvoices.length === 0 ? (
              <EmptyState />
            ) : (
              filteredInvoices.map((invoice) => (
                <InvBox
                  key={invoice.id}
                  id={invoice.id}
                  name={invoice.billTo.clientName}
                  dueDate={invoice.invoiceDate}
                  amount={invoice.items.reduce(
                    (sum, item) => sum + item.quantity * item.price,
                    0
                  )}
                  status={invoice.status}
                  onClick={() => handleInvoiceClick(invoice.id)}
                />
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default LandingPage;
