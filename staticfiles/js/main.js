// UCA Mental Health Services - Main JavaScript
// Created: April 16, 2025

// Main initialization function
function initializePage() {
  // Smooth scrolling for navigation links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Fade-in animation for cards
  const animateElements = document.querySelectorAll('.card, .dashboard-card');
  
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fadeIn');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    
    animateElements.forEach(el => {
      el.style.opacity = "0";
      observer.observe(el);
    });
  } else {
    // Fallback for browsers that don't support IntersectionObserver
    animateElements.forEach(el => {
      el.classList.add('animate-fadeIn');
    });
  }

  // Setup favorite buttons functionality
  setupFavoriteButtons();
}

// Favorites functionality
function setupFavoriteButtons() {
  const favoriteButtons = document.querySelectorAll('.favorite-btn');
  
  if (favoriteButtons.length > 0) {
    favoriteButtons.forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const resourceId = this.getAttribute('data-resource-id');
        if (!resourceId) return;
        
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        
        // Send Ajax request
        fetch(`/resources/favorite/${resourceId}/`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
          }
        })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          if (data.is_favorite) {
            this.classList.add('active');
          } else {
            this.classList.remove('active');
            
            // If we're on the favorites page and the item was unfavorited
            if (window.location.pathname.includes('favorites')) {
              const card = this.closest('.card');
              if (card) {
                card.style.opacity = '0';
                setTimeout(() => {
                  card.remove();
                  
                  // Check if there are no more favorites
                  if (document.querySelectorAll('.resource-card').length === 0) {
                    location.reload();
                  }
                }, 300);
              }
            }
          }
        })
        .catch(error => {
          console.error('Error toggling favorite:', error);
        });
      });
    });
  }
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Only call setupFavoriteButtons once
document.addEventListener('DOMContentLoaded', initializePage);