import React, { createContext, useState, useContext, useEffect } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('theme') === 'dark';
  });

  useEffect(() => {
    applyTheme();
  }, [isDarkMode]);

  const applyTheme = () => {
    const theme = isDarkMode ? 'dark' : 'light';
    localStorage.setItem('theme', theme);

    const root = document.documentElement;

    if (isDarkMode) {
      root.style.setProperty('--bg-primary', '#1a1a2e');
      root.style.setProperty('--bg-secondary', '#0d1b2a');
      root.style.setProperty('--text-primary', '#e8e8e8');
      root.style.setProperty('--text-secondary', '#b0b0b0');
      root.style.setProperty('--border-color', '#333333');
      root.style.setProperty('--card-bg', '#252540');
      root.style.setProperty('--input-bg', '#2a2a3e');
      document.body.classList.add('dark-mode');
    } else {
      root.style.setProperty('--bg-primary', '#ffffff');
      root.style.setProperty('--bg-secondary', '#f5f5f5');
      root.style.setProperty('--text-primary', '#0d1b2a');
      root.style.setProperty('--text-secondary', '#666666');
      root.style.setProperty('--border-color', '#e0e0e0');
      root.style.setProperty('--card-bg', '#ffffff');
      root.style.setProperty('--input-bg', '#ffffff');
      document.body.classList.remove('dark-mode');
    }
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
