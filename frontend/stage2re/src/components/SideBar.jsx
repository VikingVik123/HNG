import React from 'react';
import { useTheme } from '../context/ThemeContext';
import './SideBar.css';

const SideBar = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <div className="sidebar">
      <div className="logo">
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <circle cx="50" cy="50" r="45" fill="#7c3aed" />
          <text
            x="50"
            y="60"
            fontSize="50"
            fontWeight="bold"
            fill="white"
            textAnchor="middle"
          >
            I
          </text>
        </svg>
      </div>

      <div className="sidebar-content"></div>

      <div className="sidebar-bottom">
        <button
          className="dark-mode-btn"
          onClick={toggleTheme}
          title={isDarkMode ? 'Light Mode' : 'Dark Mode'}
        >
          {!isDarkMode ? (
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="5" fill="white" />
              <path
                d="M12 1v6m0 6v6"
                stroke="white"
                strokeWidth="2"
              />
              <path
                d="M4.22 4.22l4.24 4.24m5.08 5.08l4.24 4.24"
                stroke="white"
                strokeWidth="2"
              />
              <path d="M1 12h6m6 0h6" stroke="white" strokeWidth="2" />
              <path
                d="M4.22 19.78l4.24-4.24m5.08-5.08l4.24-4.24"
                stroke="white"
                strokeWidth="2"
              />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
                fill="white"
              />
            </svg>
          )}
        </button>

        <img
          src="https://4kwallpapers.com/images/walls/thumbs_3t/18378.jpg"
          alt="profile"
          className="profile-img"
        />
      </div>
    </div>
  );
};

export default SideBar;
