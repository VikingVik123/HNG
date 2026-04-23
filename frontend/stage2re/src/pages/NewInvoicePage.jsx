import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import SideBar from '../components/SideBar';
import './NewInvoicePage.css';

const NewInvoicePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isEditing = !!searchParams.get('id');

  const [errors, setErrors] = useState({});
  const [formData, setFormData] = useState({
    id: '',
    billFrom: {
      streetAddress: '',
      city: '',
      postCode: '',
      country: '',
    },
    billTo: {
      clientName: '',
      clientEmail: '',
      streetAddress: '',
      city: '',
      postCode: '',
      country: '',
    },
    invoiceDate: new Date().toISOString().split('T')[0],
    paymentTerms: 'Net 30 Days',
    projectDescription: '',
    items: [
      { itemId: Date.now(), name: '', quantity: 1, price: 0, total: 0 },
    ],
    status: 'draft',
  });

  useEffect(() => {
    if (isEditing) {
      loadInvoiceForEditing();
    }
  }, [searchParams]);

  const loadInvoiceForEditing = () => {
    const invoiceId = searchParams.get('id');
    if (invoiceId) {
      try {
        const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
        const invoice = invoices.find((inv) => inv.id === invoiceId);
        if (invoice) {
          setFormData({ ...invoice });
        }
      } catch (error) {
        console.error('Error loading invoice:', error);
      }
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Validate Bill From
    if (!formData.billFrom.streetAddress.trim()) {
      newErrors.billFromStreet = 'Street address is required';
    }
    if (!formData.billFrom.city.trim()) {
      newErrors.billFromCity = 'City is required';
    }
    if (!formData.billFrom.postCode.trim()) {
      newErrors.billFromPostCode = 'Post code is required';
    }
    if (!formData.billFrom.country.trim()) {
      newErrors.billFromCountry = 'Country is required';
    }

    // Validate Bill To
    if (!formData.billTo.clientName.trim()) {
      newErrors.clientName = 'Client name is required';
    }
    if (!formData.billTo.clientEmail.trim()) {
      newErrors.clientEmail = 'Client email is required';
    } else if (
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.billTo.clientEmail)
    ) {
      newErrors.clientEmail = 'Please enter a valid email address';
    }
    if (!formData.billTo.streetAddress.trim()) {
      newErrors.billToStreet = 'Street address is required';
    }
    if (!formData.billTo.city.trim()) {
      newErrors.billToCity = 'City is required';
    }
    if (!formData.billTo.postCode.trim()) {
      newErrors.billToPostCode = 'Post code is required';
    }
    if (!formData.billTo.country.trim()) {
      newErrors.billToCountry = 'Country is required';
    }

    // Validate items
    if (formData.items.length === 0) {
      newErrors.items = 'At least one item is required';
    } else {
      formData.items.forEach((item, index) => {
        if (!item.name.trim()) {
          newErrors[`itemName${index}`] = 'Item name is required';
        }
        if (item.quantity <= 0) {
          newErrors[`itemQty${index}`] = 'Quantity must be greater than 0';
        }
        if (item.price < 0) {
          newErrors[`itemPrice${index}`] = 'Price must be non-negative';
        }
      });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validateForm()) return;

    try {
      const invoices = JSON.parse(localStorage.getItem('invoices')) || [];
      let updatedInvoice = {
        ...formData,
        items: formData.items.map((item) => ({
          name: item.name,
          quantity: item.quantity,
          price: item.price,
          total: item.quantity * item.price,
        })),
      };

      if (isEditing) {
        const index = invoices.findIndex(
          (inv) => inv.id === searchParams.get('id')
        );
        if (index >= 0) {
          invoices[index] = updatedInvoice;
        }
      } else {
        updatedInvoice.id = `INV-${Date.now()}`;
        invoices.push(updatedInvoice);
      }

      localStorage.setItem('invoices', JSON.stringify(invoices));
      navigate('/');
    } catch (error) {
      console.error('Error saving invoice:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleNestedInputChange = (parent, field, value) => {
    setFormData((prev) => ({
      ...prev,
      [parent]: {
        ...prev[parent],
        [field]: value,
      },
    }));
  };

  const handleItemChange = (index, field, value) => {
    const updatedItems = [...formData.items];
    updatedItems[index] = { ...updatedItems[index], [field]: value };
    setFormData((prev) => ({
      ...prev,
      items: updatedItems,
    }));
  };

  const addItem = () => {
    setFormData((prev) => ({
      ...prev,
      items: [
        ...prev.items,
        { itemId: Date.now(), name: '', quantity: 1, price: 0, total: 0 },
      ],
    }));
  };

  const removeItem = (index) => {
    if (formData.items.length > 1) {
      setFormData((prev) => ({
        ...prev,
        items: prev.items.filter((_, i) => i !== index),
      }));
    }
  };

  return (
    <div className="new-invoice-container">
      <SideBar />
      <main className="invoice-form-content">
        <div className="form-wrapper">
          <div className="form-header">
            <button className="back-btn" onClick={() => navigate('/')}>
              ← Back
            </button>
            <h1>{isEditing ? 'Edit Invoice' : 'New Invoice'}</h1>
          </div>

          <form className="invoice-form">
            {/* Bill From Section */}
            <div className="form-section">
              <h2>Bill From</h2>
              <div className="form-group">
                <label>Street Address *</label>
                <input
                  type="text"
                  value={formData.billFrom.streetAddress}
                  onChange={(e) =>
                    handleNestedInputChange(
                      'billFrom',
                      'streetAddress',
                      e.target.value
                    )
                  }
                  className={errors.billFromStreet ? 'error' : ''}
                />
                {errors.billFromStreet && (
                  <span className="error-message">{errors.billFromStreet}</span>
                )}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>City *</label>
                  <input
                    type="text"
                    value={formData.billFrom.city}
                    onChange={(e) =>
                      handleNestedInputChange('billFrom', 'city', e.target.value)
                    }
                    className={errors.billFromCity ? 'error' : ''}
                  />
                  {errors.billFromCity && (
                    <span className="error-message">
                      {errors.billFromCity}
                    </span>
                  )}
                </div>
                <div className="form-group">
                  <label>Post Code *</label>
                  <input
                    type="text"
                    value={formData.billFrom.postCode}
                    onChange={(e) =>
                      handleNestedInputChange(
                        'billFrom',
                        'postCode',
                        e.target.value
                      )
                    }
                    className={errors.billFromPostCode ? 'error' : ''}
                  />
                  {errors.billFromPostCode && (
                    <span className="error-message">
                      {errors.billFromPostCode}
                    </span>
                  )}
                </div>
                <div className="form-group">
                  <label>Country *</label>
                  <input
                    type="text"
                    value={formData.billFrom.country}
                    onChange={(e) =>
                      handleNestedInputChange(
                        'billFrom',
                        'country',
                        e.target.value
                      )
                    }
                    className={errors.billFromCountry ? 'error' : ''}
                  />
                  {errors.billFromCountry && (
                    <span className="error-message">
                      {errors.billFromCountry}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Bill To Section */}
            <div className="form-section">
              <h2>Bill To</h2>
              <div className="form-group">
                <label>Client's Name *</label>
                <input
                  type="text"
                  value={formData.billTo.clientName}
                  onChange={(e) =>
                    handleNestedInputChange(
                      'billTo',
                      'clientName',
                      e.target.value
                    )
                  }
                  className={errors.clientName ? 'error' : ''}
                />
                {errors.clientName && (
                  <span className="error-message">{errors.clientName}</span>
                )}
              </div>

              <div className="form-group">
                <label>Client's Email *</label>
                <input
                  type="email"
                  value={formData.billTo.clientEmail}
                  onChange={(e) =>
                    handleNestedInputChange(
                      'billTo',
                      'clientEmail',
                      e.target.value
                    )
                  }
                  className={errors.clientEmail ? 'error' : ''}
                />
                {errors.clientEmail && (
                  <span className="error-message">{errors.clientEmail}</span>
                )}
              </div>

              <div className="form-group">
                <label>Street Address *</label>
                <input
                  type="text"
                  value={formData.billTo.streetAddress}
                  onChange={(e) =>
                    handleNestedInputChange(
                      'billTo',
                      'streetAddress',
                      e.target.value
                    )
                  }
                  className={errors.billToStreet ? 'error' : ''}
                />
                {errors.billToStreet && (
                  <span className="error-message">{errors.billToStreet}</span>
                )}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>City *</label>
                  <input
                    type="text"
                    value={formData.billTo.city}
                    onChange={(e) =>
                      handleNestedInputChange('billTo', 'city', e.target.value)
                    }
                    className={errors.billToCity ? 'error' : ''}
                  />
                  {errors.billToCity && (
                    <span className="error-message">{errors.billToCity}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>Post Code *</label>
                  <input
                    type="text"
                    value={formData.billTo.postCode}
                    onChange={(e) =>
                      handleNestedInputChange(
                        'billTo',
                        'postCode',
                        e.target.value
                      )
                    }
                    className={errors.billToPostCode ? 'error' : ''}
                  />
                  {errors.billToPostCode && (
                    <span className="error-message">
                      {errors.billToPostCode}
                    </span>
                  )}
                </div>
                <div className="form-group">
                  <label>Country *</label>
                  <input
                    type="text"
                    value={formData.billTo.country}
                    onChange={(e) =>
                      handleNestedInputChange(
                        'billTo',
                        'country',
                        e.target.value
                      )
                    }
                    className={errors.billToCountry ? 'error' : ''}
                  />
                  {errors.billToCountry && (
                    <span className="error-message">
                      {errors.billToCountry}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Invoice Details Section */}
            <div className="form-section">
              <div className="form-row">
                <div className="form-group">
                  <label>Invoice Date</label>
                  <input
                    type="date"
                    value={formData.invoiceDate}
                    onChange={(e) =>
                      handleInputChange('invoiceDate', e.target.value)
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Payment Terms</label>
                  <select
                    value={formData.paymentTerms}
                    onChange={(e) =>
                      handleInputChange('paymentTerms', e.target.value)
                    }
                  >
                    <option>Net 30 Days</option>
                    <option>Net 60 Days</option>
                    <option>Net 90 Days</option>
                    <option>Due on Delivery</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Project Description</label>
                <textarea
                  value={formData.projectDescription}
                  onChange={(e) =>
                    handleInputChange('projectDescription', e.target.value)
                  }
                  rows="3"
                ></textarea>
              </div>
            </div>

            {/* Items Section */}
            <div className="form-section">
              <h2>Items</h2>
              {errors.items && (
                <span className="error-message">{errors.items}</span>
              )}
              <div className="items-table">
                <div className="items-header">
                  <div className="col-name">Item Name</div>
                  <div className="col-qty">Qty</div>
                  <div className="col-price">Price</div>
                  <div className="col-total">Total</div>
                  <div className="col-action"></div>
                </div>

                {formData.items.map((item, index) => (
                  <div key={item.itemId} className="items-row">
                    <input
                      type="text"
                      placeholder="Item name"
                      value={item.name}
                      onChange={(e) =>
                        handleItemChange(index, 'name', e.target.value)
                      }
                      className={`col-name ${
                        errors[`itemName${index}`] ? 'error' : ''
                      }`}
                    />
                    <input
                      type="number"
                      placeholder="0"
                      value={item.quantity}
                      onChange={(e) =>
                        handleItemChange(
                          index,
                          'quantity',
                          parseInt(e.target.value) || 0
                        )
                      }
                      className={`col-qty ${
                        errors[`itemQty${index}`] ? 'error' : ''
                      }`}
                      min="0"
                    />
                    <input
                      type="number"
                      placeholder="0.00"
                      value={item.price}
                      onChange={(e) =>
                        handleItemChange(
                          index,
                          'price',
                          parseFloat(e.target.value) || 0
                        )
                      }
                      className={`col-price ${
                        errors[`itemPrice${index}`] ? 'error' : ''
                      }`}
                      min="0"
                      step="0.01"
                    />
                    <div className="col-total">
                      {(item.quantity * item.price).toFixed(2)}
                    </div>
                    <button
                      type="button"
                      className="col-action"
                      onClick={() => removeItem(index)}
                      disabled={formData.items.length === 1}
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>

              <button
                type="button"
                className="add-item-btn"
                onClick={addItem}
              >
                + Add New Item
              </button>
            </div>

            {/* Form Actions */}
            <div className="form-actions">
              <button
                type="button"
                className="btn-cancel"
                onClick={() => navigate('/')}
              >
                Cancel
              </button>
              <button type="button" className="btn-save" onClick={handleSave}>
                {isEditing ? 'Update Invoice' : 'Save Invoice'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default NewInvoicePage;
