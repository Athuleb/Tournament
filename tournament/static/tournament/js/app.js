document.addEventListener('DOMContentLoaded', () => {
    // Initialize AOS
    if (window.AOS) {
        AOS.init({
            duration: 1000,
            once: true,
            offset: 100
        });
    }

    // Mobile Menu Toggle
    const menuToggle = document.getElementById('mobile-menu');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            menuToggle.classList.toggle('is-active');
        });
    }

    // Close mobile menu when links are clicked
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            menuToggle.classList.remove('is-active');
        });
    });

    // Initialize Lucide Icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // Registration elements
    const form = document.getElementById('registrationForm');
    const messageDiv = document.getElementById('message');
    const photoInput = document.getElementById('studentPhoto');
    const photoPreview = document.getElementById('photoPreview');

    // Login handling
    const loginForm = document.getElementById('loginForm');
    const loginMessage = document.getElementById('loginMessage');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.classList.add('btn-loading');
            if (loginMessage) {
                loginMessage.classList.remove('show');
                loginMessage.innerHTML = '';
            }

            const formData = new FormData(loginForm);
            const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
            const csrfToken = csrfElement ? csrfElement.value : '';

            try {
                // Determine registration URL if not defined globally
                const fetchUrl = (typeof REGISTRATION_URL !== 'undefined') ? REGISTRATION_URL : window.location.pathname;

                const response = await fetch(fetchUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    }
                });

                if (!response.ok) throw new Error('Network response was not ok');

                const data = await response.json();
                if (submitBtn) submitBtn.classList.remove('btn-loading');

                if (data.status === 'login_success') {
                    if (loginMessage) {
                        loginMessage.innerHTML = `<i data-lucide="check-circle" style="width: 20px; height: 20px;"></i> <span>${data.message} Opening Registration Page...</span>`;
                        loginMessage.className = 'message success show';
                        if (window.lucide) lucide.createIcons();
                    }

                    // Direct redirect to registration page
                    setTimeout(() => {
                        window.location.href = '/registration/';
                    }, 1000);
                } else {
                    if (loginMessage) {
                        loginMessage.innerHTML = `<i data-lucide="alert-circle" style="width: 20px; height: 20px;"></i> <span>${data.message}</span>`;
                        loginMessage.className = 'message error show';
                        if (window.lucide) lucide.createIcons();
                    }
                }
            } catch (error) {
                if (submitBtn) submitBtn.classList.remove('btn-loading');
                console.error('Error:', error);
                if (loginMessage) {
                    loginMessage.textContent = 'An error occurred. Please try again.';
                    loginMessage.className = 'message error show';
                }
            }
        });
    }

    // Function to Reset Form UI
    const resetRegistrationUI = () => {
        if (messageDiv) {
            messageDiv.classList.remove('show');
            setTimeout(() => {
                messageDiv.style.display = 'none';
                messageDiv.innerHTML = '';
            }, 300);
        }
        const target = form || loginForm;
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    // Handle all "Register Now" links to ensure they "reopen" the form correctly
    document.querySelectorAll('a[href="#register"], a[href="#login"]').forEach(link => {
        link.addEventListener('click', (e) => {
            if (messageDiv && messageDiv.classList.contains('show')) {
                resetRegistrationUI();
            }
        });
    });

    // Photo Preview
    if (photoInput) {
        photoInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    photoPreview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Form Submission
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');

            // Start loading state
            submitBtn.classList.add('btn-loading');
            messageDiv.classList.remove('show');
            messageDiv.style.display = 'none';

            const formData = new FormData(form);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                const response = await fetch(REGISTRATION_URL, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    }
                });

                const data = await response.json();

                // Stop loading state
                submitBtn.classList.remove('btn-loading');

                if (data.status === 'success') {
                    // Trigger Goal Animation
                    const goalOverlay = document.getElementById('goalOverlay');
                    if (goalOverlay) {
                        goalOverlay.style.display = 'flex';
                        goalOverlay.classList.add('animating');
                        setTimeout(() => {
                            goalOverlay.classList.remove('animating');
                            goalOverlay.style.display = 'none';
                        }, 2000);
                    }

                    // Hide form and show success screen
                    form.style.display = 'none';
                    messageDiv.innerHTML = `
                        <div class="success-screen">
                            <i data-lucide="check-circle" style="width: 64px; height: 64px; color: var(--primary); margin-bottom: 20px;"></i>
                            <h3>Registration Successful!</h3>
                            <p>${data.message}</p>
                            <p style="font-size: 0.9rem; color: var(--primary); margin-top: 15px;">Form will reopen automatically...</p>
                        </div>
                    `;
                    messageDiv.className = 'message success show';
                    messageDiv.style.display = 'block';

                    // Initialize icon
                    if (window.lucide) {
                        lucide.createIcons();
                    }

                    // Automatically reopen the form after 3.5 seconds
                    setTimeout(() => {
                        form.reset();
                        if (photoPreview) photoPreview.innerHTML = '';

                        // Fade out message and show form
                        messageDiv.classList.remove('show');
                        setTimeout(() => {
                            messageDiv.style.display = 'none';
                            form.style.display = 'block';
                            form.style.opacity = '0';
                            setTimeout(() => {
                                form.style.transition = 'opacity 0.6s ease';
                                form.style.opacity = '1';
                            }, 50);
                        }, 400);
                    }, 3500);
                } else {
                    messageDiv.innerHTML = `
                        <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                            <i data-lucide="alert-circle" style="width: 20px; height: 20px;"></i>
                            <span>${data.message}</span>
                        </div>
                    `;
                    messageDiv.className = 'message error show';
                    messageDiv.style.display = 'block';
                    if (window.lucide) lucide.createIcons();
                    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } catch (error) {
                submitBtn.classList.remove('btn-loading');
                console.error('Error:', error);
                messageDiv.textContent = 'An error occurred. Please try again.';
                messageDiv.className = 'message error show';
                messageDiv.style.display = 'block';
            }
        });
    }

    // Scroll Animations Observer
    const observerOptions = { threshold: 0.1 };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.section').forEach(section => {
        observer.observe(section);
    });
});
