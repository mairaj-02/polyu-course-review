// Main JavaScript for PolyU GUR Course Reviews

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Search functionality
    const searchForm = document.querySelector('#search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.querySelector('#search-input');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.classList.add('is-invalid');
            }
        });
    }
    
    // Star rating display
    const starRatings = document.querySelectorAll('.star-rating');
    starRatings.forEach(function(rating) {
        const ratingValue = parseFloat(rating.getAttribute('data-rating'));
        const fullStars = Math.floor(ratingValue);
        const hasHalfStar = ratingValue % 1 >= 0.5;
        
        let starsHTML = '';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            starsHTML += '<i class="bi bi-star-fill text-warning"></i>';
        }
        
        // Half star
        if (hasHalfStar) {
            starsHTML += '<i class="bi bi-star-half text-warning"></i>';
        }
        
        // Empty stars
        const emptyStars = 5 - Math.ceil(ratingValue);
        for (let i = 0; i < emptyStars; i++) {
            starsHTML += '<i class="bi bi-star text-warning"></i>';
        }
        
        rating.innerHTML = starsHTML;
    });
    
    // Interactive star rating for review forms
    const ratingInputs = document.querySelectorAll('.rating-input');
    ratingInputs.forEach(function(input) {
        const ratingContainer = document.createElement('div');
        ratingContainer.className = 'star-rating-input mb-3';
        
        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('i');
            star.className = 'bi bi-star text-warning fs-4 me-1';
            star.setAttribute('data-rating', i);
            star.style.cursor = 'pointer';
            
            star.addEventListener('click', function() {
                input.value = i;
                updateStarDisplay(ratingContainer, i);
            });
            
            star.addEventListener('mouseover', function() {
                updateStarDisplay(ratingContainer, i);
            });
            
            ratingContainer.appendChild(star);
        }
        
        ratingContainer.addEventListener('mouseleave', function() {
            updateStarDisplay(ratingContainer, input.value || 0);
        });
        
        input.parentNode.insertBefore(ratingContainer, input);
        input.style.display = 'none';
        
        // Initialize display
        updateStarDisplay(ratingContainer, input.value || 0);
    });
    
    function updateStarDisplay(container, rating) {
        const stars = container.querySelectorAll('i');
        stars.forEach(function(star, index) {
            if (index < rating) {
                star.classList.remove('bi-star');
                star.classList.add('bi-star-fill');
            } else {
                star.classList.remove('bi-star-fill');
                star.classList.add('bi-star');
            }
        });
    }
    
    // Course filter functionality
    const categorySelect = document.querySelector('#category');
    const subcategorySelect = document.querySelector('#subcategory');
    
    if (categorySelect && subcategorySelect) {
        categorySelect.addEventListener('change', function() {
            const category = this.value;
            
            // Clear subcategory options
            subcategorySelect.innerHTML = '<option value="">All Subcategories</option>';
            
            // Add relevant subcategory options based on selected category
            if (category === 'CAR') {
                addSubcategoryOptions(['A', 'M', 'N', 'D'], [
                    'A: Human Nature, relation and development',
                    'M: Chinese culture and history',
                    'N: Culture, Organization, society, and globalization',
                    'D: Science, technology and environment'
                ]);
            } else if (category === 'Language') {
                addSubcategoryOptions(['English', 'Chinese'], [
                    'English',
                    'Chinese'
                ]);
            } else if (category === 'Leadership') {
                addSubcategoryOptions(['Tomorrow\'s Leaders', 'Tango'], [
                    'Tomorrow\'s Leaders',
                    'Tango'
                ]);
            }
        });
    }
    
    function addSubcategoryOptions(values, texts) {
        values.forEach(function(value, index) {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = texts[index];
            subcategorySelect.appendChild(option);
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
});