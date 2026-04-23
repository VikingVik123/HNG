import React from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { AppRouter } from './router';
import './style.css';

function App() {
  return (
    <ThemeProvider>
      <AppRouter />
    </ThemeProvider>
  );
}

export default App;
