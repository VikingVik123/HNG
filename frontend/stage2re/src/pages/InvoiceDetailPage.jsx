import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import SideBar from '../components/SideBar';
import './InvoiceDetailPage.css';

const InvoiceDetailPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const loadInvoice = () => {
    try {
      const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
      const foundInvoice = invoices.find((inv) => inv.id === id);
      setInvoice(foundInvoice);
    } catch (error) {
      console.error('Error loading invoice:', error);
    }
  };

  useEffect(() => {
    loadInvoice();
  }, [id]);

  const markAsPaid = () => {
    if (invoice) {
      const updatedInvoice = { ...invoice, status: 'paid' };
      saveInvoice(updatedInvoice);
      setInvoice(updatedInvoice);
    }
  };

  const editInvoice = () => {
    navigate(`/new-invoice?id=${invoice.id}`);
  };

  const deleteInvoice = () => {
    try {
      const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
      const filtered = invoices.filter((inv) => inv.id !== id);
      localStorage.setItem('invoices', JSON.stringify(filtered));
      navigate('/');
    } catch (error) {
      console.error('Error deleting invoice:', error);
    }
  };

  const saveInvoice = (updatedInvoice) => {
    try {
      const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
      const index = invoices.findIndex((inv) => inv.id === updatedInvoice.id);
      if (index >= 0) {
        invoices[index] = updatedInvoice;
        localStorage.setItem('invoices', JSON.stringify(invoices));
      }
    } catch (error) {
      console.error('Error saving invoice:', error);
    }
  };

  const getTotalAmount = () => {
    if (!invoice) return 0;
    return invoice.items.reduce(
      (sum, item) => sum + item.quantity * item.price,
      0
    );
  };

  if (!invoice) return <div>Loading...</div>;

  return (
    <div className="detail-container">
      <SideBar />
      <main className="detail-content">
        <div className="detail-wrapper">
          <div className="detail-header">
            <button className="back-btn" onClick={() => navigate('/')}>
              ← Back to Invoices
            </button>
            <div className="header-actions">
              <button className="btn-edit" onClick={editInvoice}>
                Edit
              </button>
              <button
                className="btn-delete"
                onClick={() => setShowDeleteModal(true)}
              >
                Delete
              </button>
              {invoice.status !== 'paid' && (
                <button className="btn-pay" onClick={markAsPaid}>
                  Mark as Paid
                </button>
              )}
            </div>
          </div>

          {/* Invoice Details */}
          <div className="invoice-detail">
            <div className="invoice-header-info">
              <div>
                <h1>{invoice.id}</h1>
                <p className={`status-badge ${invoice.status}`}>
                  {invoice.status}
                </p>
              </div>
            </div>

            {/* Bill From / Bill To */}
            <div className="bill-info">
              <div className="bill-section">
                <h3>Bill From</h3>
                <p>{invoice.billFrom.streetAddress}</p>
                <p>
                  {invoice.billFrom.city}, {invoice.billFrom.postCode}
                </p>
                <p>{invoice.billFrom.country}</p>
              </div>
              <div className="bill-section">
                <h3>Bill To</h3>
                <p>
                  <strong>{invoice.billTo.clientName}</strong>
                </p>
                <p>{invoice.billTo.streetAddress}</p>
                <p>
                  {invoice.billTo.city}, {invoice.billTo.postCode}
                </p>
                <p>{invoice.billTo.country}</p>
                <p>{invoice.billTo.clientEmail}</p>
              </div>
            </div>

            {/* Invoice Info */}
            <div className="invoice-info">
              <div className="info-item">
                <span className="label">Invoice Date</span>
                <span className="value">{invoice.invoiceDate}</span>
              </div>
              <div className="info-item">
                <span className="label">Payment Terms</span>
                <span className="value">{invoice.paymentTerms}</span>
              </div>
            </div>

            {/* Items Table */}
            <div className="items-section">
              <table className="items-table">
                <thead>
                  <tr>
                    <th>Item Description</th>
                    <th className="text-right">Quantity</th>
                    <th className="text-right">Price</th>
                    <th className="text-right">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.items.map((item, index) => (
                    <tr key={index}>
                      <td>{item.name}</td>
                      <td className="text-right">{item.quantity}</td>
                      <td className="text-right">£{item.price.toFixed(2)}</td>
                      <td className="text-right">
                        £{(item.quantity * item.price).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Total Amount */}
            <div className="total-section">
              <div className="total-amount">
                <span className="label">Total Amount Due</span>
                <span className="amount">£{getTotalAmount().toFixed(2)}</span>
              </div>
            </div>

            {/* Description */}
            {invoice.projectDescription && (
              <div className="description-section">
                <h3>Notes</h3>
                <p>{invoice.projectDescription}</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Delete Modal */}
      {showDeleteModal && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Confirm Deletion</h2>
            <p>Are you sure you want to delete this invoice?</p>
            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setShowDeleteModal(false)}
              >
                Cancel
              </button>
              <button className="btn-delete" onClick={deleteInvoice}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InvoiceDetailPage;
