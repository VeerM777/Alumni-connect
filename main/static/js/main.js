// Main JavaScript for Alumni Connect portal

document.addEventListener("DOMContentLoaded", function () {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Profile picture preview
  const profilePictureInput = document.querySelector(
    'input[type="file"][name="profile_picture"]'
  );
  if (profilePictureInput) {
    profilePictureInput.addEventListener("change", function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          // Check if preview container exists, if not create it
          let previewContainer = document.querySelector(".profile-pic-preview");
          if (!previewContainer) {
            previewContainer = document.createElement("div");
            previewContainer.className = "profile-pic-preview mt-2";
            profilePictureInput.parentNode.appendChild(previewContainer);
          }

          // Create preview image
          previewContainer.innerHTML = `
                        <p class="form-text">New profile picture preview:</p>
                        <img src="${e.target.result}" alt="Profile picture preview" class="img-thumbnail" style="max-height: 100px;">
                    `;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Date picker enhancement
  const datePickers = document.querySelectorAll('input[type="date"]');
  datePickers.forEach(function (picker) {
    // Add class for styling
    picker.classList.add("form-control");
  });

  // Career update form toggle
  const isCurrentCheckbox = document.getElementById("id_is_current");
  const endDateField = document.getElementById("id_end_date").parentNode;

  if (isCurrentCheckbox && endDateField) {
    // Initial state
    endDateField.style.display = isCurrentCheckbox.checked ? "none" : "block";

    // Toggle on change
    isCurrentCheckbox.addEventListener("change", function () {
      endDateField.style.display = this.checked ? "none" : "block";
    });
  }

  // Confirmation modals
  const confirmationLinks = document.querySelectorAll("[data-confirm]");
  confirmationLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      if (!confirm(this.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // Search form enhancements
  const searchForm = document.querySelector('form[role="search"]');
  if (searchForm) {
    const searchInput = searchForm.querySelector('input[type="search"]');
    searchInput.addEventListener("input", function () {
      // Add clear button when text is entered
      let clearButton = searchForm.querySelector(".search-clear");
      if (this.value && !clearButton) {
        clearButton = document.createElement("button");
        clearButton.className = "btn btn-sm search-clear position-absolute";
        clearButton.style.right = "40px";
        clearButton.style.top = "5px";
        clearButton.innerHTML = '<i class="fas fa-times"></i>';
        clearButton.addEventListener("click", function () {
          searchInput.value = "";
          searchInput.focus();
          this.remove();
        });
        searchInput.parentNode.style.position = "relative";
        searchInput.parentNode.appendChild(clearButton);
      } else if (!this.value && clearButton) {
        clearButton.remove();
      }
    });
  }

  // Filter toggle on mobile
  const filterToggle = document.querySelector(".filter-toggle");
  if (filterToggle) {
    filterToggle.addEventListener("click", function () {
      const filterContainer = document.querySelector(".filter-container");
      filterContainer.classList.toggle("show");
    });
  }
});
