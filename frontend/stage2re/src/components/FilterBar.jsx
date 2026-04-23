import React, { useState } from 'react';
import './FilterBar.css';

const FilterBar = ({ filters = ['All', 'Draft', 'Pending', 'Paid'], selected = 'All', onFilterChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleFilterClick = (filter) => {
    onFilterChange(filter);
    setIsOpen(false);
  };

  return (
    <div className="filter-bar">
      <button className="filter-button" onClick={() => setIsOpen(!isOpen)}>
        Filter by status
        <svg
          className={`dropdown-arrow ${isOpen ? 'open' : ''}`}
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M6 9l6 6 6-6"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="filter-dropdown">
          {filters.map((filter) => (
            <div
              key={filter}
              className={`filter-option ${selected === filter ? 'active' : ''}`}
              onClick={() => handleFilterClick(filter)}
            >
              {filter}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FilterBar;
