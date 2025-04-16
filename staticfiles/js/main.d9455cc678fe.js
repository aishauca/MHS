// Add this to static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
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
  
    // Tooltip initialization for action icons
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  
    // Mobile navigation enhancement
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
      navbarToggler.addEventListener('click', function() {
        document.body.classList.toggle('nav-open');
      });
      
      // Close mobile menu when clicking outside
      document.addEventListener('click', function(event) {
        if (
          navbarCollapse.classList.contains('show') && 
          !navbarCollapse.contains(event.target) && 
          !navbarToggler.contains(event.target)
        ) {
          navbarToggler.click();
        }
      });
    }
  
    // Enhance form inputs with floating labels effect
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(input => {
      input.addEventListener('focus', () => {
        input.parentElement.classList.add('focused');
      });
      
      input.addEventListener('blur', () => {
        if (input.value === '') {
          input.parentElement.classList.remove('focused');
        }
      });
      
      // Check initial state
      if (input.value !== '') {
        input.parentElement.classList.add('focused');
      }
    });
  
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
      button.addEventListener('click', function(e) {
        const x = e.clientX - e.target.getBoundingClientRect().left;
        const y = e.clientY - e.target.getBoundingClientRect().top;
        
        const ripple = document.createElement('span');
        ripple.classList.add('ripple-effect');
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        this.appendChild(ripple);
        
        setTimeout(() => {
          ripple.remove();
        }, 600);
      });
    });
  });
  
  // CSRF token function for AJAX requests
  function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }
  
  // Function to handle favorites toggling
  function setupFavoriteToggle() {
    document.querySelectorAll('.favorite-btn').forEach(btn => {
      btn.addEventListener('click', async function(e) {
        e.preventDefault();
        const resourceId = this.dataset.resourceId;
        const csrftoken = getCookie('csrftoken');
        
        try {
          const response = await fetch(`/resources/favorite/${resourceId}/`, {
            method: 'POST',
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': csrftoken
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            this.classList.toggle('active', data.is_favorite);
            
            // If we're on the favorites page and the item was unfavorited
            if (!data.is_favorite && window.location.pathname.includes('favorites')) {
              const card = this.closest('.card');
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
        } catch (error) {
          console.error('Error toggling favorite:', error);
        }
      });
    });
  }
  
  // Get CSRF cookie
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
  
  // Run after DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    setupFavoriteToggle();
  });