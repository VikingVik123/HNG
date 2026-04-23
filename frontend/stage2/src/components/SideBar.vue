<script setup>
import { useTheme } from '../composables/useTheme';

const { isDarkMode, toggleTheme } = useTheme();
</script>

<template>
  <div class="sidebar">
    <div class="logo">
      <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="45" fill="#7c3aed"/>
        <text x="50" y="60" font-size="50" font-weight="bold" fill="white" text-anchor="middle">I</text>
      </svg>
    </div>
    
    <div class="sidebar-content">
      <!-- Navigation or other content can go here -->
    </div>

    <div class="sidebar-bottom">
      <button class="dark-mode-btn" @click="toggleTheme" :title="isDarkMode ? 'Light Mode' : 'Dark Mode'">
        <svg v-if="!isDarkMode" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="5" fill="white"/>
          <path d="M12 1v6m0 6v6" stroke="white" stroke-width="2"/>
          <path d="M4.22 4.22l4.24 4.24m5.08 5.08l4.24 4.24" stroke="white" stroke-width="2"/>
          <path d="M1 12h6m6 0h6" stroke="white" stroke-width="2"/>
          <path d="M4.22 19.78l4.24-4.24m5.08-5.08l4.24-4.24" stroke="white" stroke-width="2"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="white"/>
        </svg>
      </button>
      
      <img src="https://4kwallpapers.com/images/walls/thumbs_3t/18378.jpg" alt="profile" class="profile-img">
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: 5rem;
  height: 100vh;
  padding: 1rem 0.75rem;
  background-color: #4a5c8a;
  position: fixed;
  left: 0;
  top: 0;
  box-sizing: border-box;
  border-radius: 0 1rem 1rem 0;
}

.logo {
  width: 100%;
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.logo svg {
  width: 100%;
  height: 100%;
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sidebar-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.dark-mode-btn {
  width: 2.5rem;
  height: 2.5rem;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.3s;
}

.dark-mode-btn:hover {
  opacity: 0.8;
}

.dark-mode-btn svg {
  width: 1.5rem;
  height: 1.5rem;
}

.profile-img {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.3s;
}

.profile-img:hover {
  transform: scale(1.05);
}
</style>