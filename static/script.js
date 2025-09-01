
    // Mobile nav toggle
    const toggle = document.querySelector(".nav-toggle");
    const navLinks = document.getElementById("nav-links");
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", !expanded);
      navLinks.classList.toggle("active");
    });

    document.querySelectorAll('input[name="products"]').forEach(cb => {
  cb.addEventListener('change', () => {
    const feedback = document.getElementById('cart-feedback');
    if (cb.checked) {
      feedback.textContent = `${cb.dataset.name} added to selection.`;
    } else {
      feedback.textContent = `${cb.dataset.name} removed from selection.`;
    }
  });
});

// validating the buy page forms

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("orderForm");

  form.addEventListener("submit", function (e) {
    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const email = document.getElementById("email").value.trim();

    let errors = [];

    // Name validation: at least 3 characters, letters only
    if (!/^[A-Za-z\s]{3,}$/.test(name)) {
      errors.push("Please enter a valid name (letters only, min 2 chars).");
    }

    // Phone validation: must be 10–12 digits
    if (!/^[0-9]{10,12}$/.test(phone)) {
      errors.push("Phone number must be 10 to 15 digits.");
    }

    // Email validation: must match email format
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.push("Please enter a valid email address.");
    }

    if (errors.length > 0) {
      e.preventDefault(); // stop form submission
      alert(errors.join("\n"));
    }
  });
});

// script to listen to eventf from guides page

document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.read-more-btn');

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const currentMoreInfo = button.previousElementSibling;

      // Collapse all others
      document.querySelectorAll('.more-info').forEach(section => {
        if (section !== currentMoreInfo) {
          section.classList.remove('show');
          const btn = section.parentElement.querySelector('.read-more-btn');
          if (btn) btn.textContent = 'Read More';
        }
      });

      // Toggle this one
      const isOpen = currentMoreInfo.classList.contains('show');
      currentMoreInfo.classList.toggle('show');
      button.textContent = isOpen ? 'Read More' : 'Read Less';
    });
  });
});

// validate register


document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".balcony-form");

  form.addEventListener("submit", function (e) {
    let valid = true;
    let messages = [];

    // Get field values
    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const email = document.getElementById("email").value.trim();
    const balconyType = document.getElementById("balcony-type").value;
    const sunlight = parseInt(document.getElementById("sunlight").value, 10);
    const size = parseFloat(document.getElementById("balconySize").value);
    const water = document.getElementById("water").value;
    const soil = document.getElementById("soil").value;
    const season = document.getElementById("season").value;

    // Name
    if (name === "") {
      valid = false;
      messages.push("Name is required.");
    }

    // Phone: 07xxxxxxxx
    const phonePattern = /^07\d{8}$/;
    if (!phonePattern.test(phone)) {
      valid = false;
      messages.push("Phone must be in the format 07XXXXXXXX.");
    }

    // Email format
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
      valid = false;
      messages.push("Enter a valid email address.");
    }

    // Balcony type
    if (balconyType === "") {
      valid = false;
      messages.push("Please select a balcony type.");
    }

    // Sunlight hours
    if (isNaN(sunlight) || sunlight < 0 || sunlight >12) {
      valid = false;
      messages.push("Sunlight hours must be between 0 and 12.");
    }

    // Balcony size
    if (isNaN(size) || size <= 0) {
      valid = false;
      messages.push("Balcony size must be a positive number.");
    }

    // Water availability
    if (water === "") {
      valid = false;
      messages.push("Please select water availability.");
    }

    // Soil type
    if (soil === "") {
      valid = false;
      messages.push("Please select a soil type.");
    }

    // Season
    if (season === "") {
      valid = false;
      messages.push("Please select the current season.");
    }

    // If not valid, prevent submission and show messages
    if (!valid) {
      e.preventDefault();
      alert(messages.join("\n"));
    }
  });
});


