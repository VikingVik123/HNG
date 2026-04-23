import { ref } from 'vue';

const isDarkMode = ref(localStorage.getItem('theme') === 'dark');

export const useTheme = () => {
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value;
    applyTheme();
  };

  const applyTheme = () => {
    const theme = isDarkMode.value ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    
    const root = document.documentElement;
    
    if (isDarkMode.value) {
      // Dark mode colors
      root.style.setProperty('--bg-primary', '#1a1a2e');
      root.style.setProperty('--bg-secondary', '#0d1b2a');
      root.style.setProperty('--text-primary', '#e8e8e8');
      root.style.setProperty('--text-secondary', '#b0b0b0');
      root.style.setProperty('--border-color', '#333333');
      root.style.setProperty('--card-bg', '#252540');
      root.style.setProperty('--input-bg', '#2a2a3e');
      document.body.classList.add('dark-mode');
    } else {
      // Light mode colors
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

  // Apply theme on load
  applyTheme();

  return {
    isDarkMode,
    toggleTheme,
    applyTheme
  };
};
