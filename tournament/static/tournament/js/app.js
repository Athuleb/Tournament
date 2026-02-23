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
            console.log('Form submission started');

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

                if (data.status === 'success') {
                    messageDiv.textContent = data.message;
                    messageDiv.className = 'message success';
                    messageDiv.style.display = 'block';

                    if (data.download_pdf) {
                        setTimeout(() => {
                            window.location.href = `/download-pdf/${data.college_id}/`;
                        }, 2000);
                    }

                    form.reset();
                    photoPreview.innerHTML = '';
                } else {
                    messageDiv.textContent = data.message;
                    messageDiv.className = 'message error';
                    messageDiv.style.display = 'block';
                }
            } catch (error) {
                console.error('Error:', error);
                messageDiv.textContent = 'An error occurred. Please try again.';
                messageDiv.className = 'message error';
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
