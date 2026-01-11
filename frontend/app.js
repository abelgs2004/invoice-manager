const BACKEND_URL = "";

// Elements
const uploadSection = document.getElementById("uploadSection");
const driveConnectBox = document.getElementById("driveConnectBox");
const navSignInBtn = document.getElementById("navSignInBtn");
const navLogoutBtn = document.getElementById("navLogoutBtn");
const dropzone = document.getElementById("dropzone");
const dropzoneContent = document.getElementById("dropzoneContent"); // ADDED
const fileInput = document.getElementById("fileInput");
const resultArea = document.getElementById("resultArea");
const resultJson = document.getElementById("resultJson");
const driveLinkContainer = document.getElementById("driveLinkContainer");
const driveLinkBtn = document.getElementById("driveLinkBtn");

// New Elements
const previewContainer = document.getElementById("previewContainer");
const previewIcon = document.getElementById("previewIcon");
const filenameInput = document.getElementById("filenameInput");
const clearBtn = document.getElementById("clearBtn");

let currentFile = null;
let currentFileFields = null; // Store dry-run results

async function checkDriveStatus() {
  try {
    const res = await fetch(`${BACKEND_URL}/drive/status`, { cache: "no-store" });
    const data = await res.json();

    // Always show upload section
    uploadSection.style.display = "block";

    // Update Navbar Buttons
    if (data.connected) {
      if (navSignInBtn) navSignInBtn.style.display = "none";
      if (navLogoutBtn) navLogoutBtn.style.display = "inline-flex";
    } else {
      if (navSignInBtn) navSignInBtn.style.display = "inline-flex";
      if (navLogoutBtn) navLogoutBtn.style.display = "none";
    }

    if (driveConnectBox) {
      driveConnectBox.style.display = "block"; // Always show box logic
      const contentDiv = driveConnectBox.querySelector('.drive-box-content');

      if (data.connected) {
        // Connected State: Hide the box entirely
        driveConnectBox.style.display = "none";
      } else {
        // Not Connected
        contentDiv.innerHTML = `
            <div class="drive-icon-small">
              <img src="https://upload.wikimedia.org/wikipedia/commons/1/12/Google_Drive_icon_%282020%29.svg" alt="Drive">
            </div>
            <div class="drive-text">
              <h4>Connect Google Drive</h4>
              <p>Automatically save and organize processed files.</p>
            </div>
            <a href="/connect-drive" class="btn btn-sm btn-google-outline">
              Connect
            </a>
         `;
      }
    }
  } catch (err) {
    console.error("Backend not reachable", err);
    // Even if backend is down, show the box so user sees the UI (falls back to default 'Connect' view)
    if (driveConnectBox) driveConnectBox.style.display = "block";
  }
}

/**
 * Handle Logout
 */
async function handleLogout() {
  try {
    await fetch(`${BACKEND_URL}/disconnect-drive`, { method: "POST" });
    // Refresh status to update UI
    checkDriveStatus();
  } catch (err) {
    console.error("Logout failed", err);
  }
}

/**
 * 1. File Selection Handler (Preview Phase)
 */
function handleFileSelection(file) {
  if (!file) return;

  // Validate type
  const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
  if (!validTypes.includes(file.type)) {
    alert("Invalid file type. Please upload PDF, PNG, or JPG.");
    return;
  }

  currentFile = file;

  // UI: Hide Dropzone Content, Show Preview
  dropzoneContent.style.display = 'none';
  previewContainer.style.display = 'flex';

  // Show Preview Image/Icon
  previewIcon.innerHTML = '';
  if (file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = document.createElement('img');
      img.src = e.target.result;
      previewIcon.appendChild(img);
    };
    reader.readAsDataURL(file);
  } else {
    previewIcon.innerHTML = '<i class="fa-solid fa-file-pdf"></i>';
  }

  // Trigger Analysis (Dry Run)
  analyzeFile(file);
}

/**
 * Helper: Show Toast Notification
 * type: 'progress' | 'success' | 'error'
 */
function showToast(message, type = 'progress') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  toast.innerHTML = `
    <div class="toast-header">
      <span class="toast-text">${message}</span>
      ${type !== 'progress' ? '<i class="fa-solid fa-xmark" style="cursor:pointer;" onclick="this.closest(\'.toast\').remove()"></i>' : ''}
    </div>
    ${type === 'progress' ? `
    <div class="toast-progress-bg">
      <div class="toast-progress-bar"></div>
    </div>` : ''}
  `;

  container.appendChild(toast);

  // Animate Progress (Fake it for better UX)
  if (type === 'progress') {
    const bar = toast.querySelector('.toast-progress-bar');
    setTimeout(() => { bar.style.width = '30%'; }, 100);
    setTimeout(() => { bar.style.width = '70%'; }, 500);
    setTimeout(() => { bar.style.width = '90%'; }, 1200);
  }

  // Auto-remove success/error toasts
  if (type !== 'progress') {
    setTimeout(() => {
      toast.style.animation = 'fadeOut 0.3s forwards';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  return toast;
}

/**
 * Helper: Analyze File (Dry Run) to get Smart Name & Stats
 */
async function analyzeFile(file) {
  // Clear any previous toasts
  document.getElementById('toastContainer').innerHTML = '';

  // Show Toast
  const toast = showToast(`Analyzing ${file.name}...`, 'progress');



  // DO NOT disable input or show "Analyzing" text there (User Request)
  // filenameInput.value = "Analyzing..."; <--- REMOVED

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${BACKEND_URL}/upload?dry_run=true`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    // Complete progress bar
    if (toast.querySelector('.toast-progress-bar')) {
      toast.querySelector('.toast-progress-bar').style.width = '100%';
    }

    if (data.status === "dry_run" || data.status === "success") {
      // Remove loading toast after short delay
      setTimeout(() => {
        toast.remove();
        showToast("Analysis Complete", "success");
      }, 500);

      // Populate Name
      if (data.predicted_filename) {
        filenameInput.value = data.predicted_filename;
      } else {
        filenameInput.value = file.name;
      }

      // Populate & Show Bottom Result Area (Preview Mode)
      if (data.fields) {
        // Cache fields for the real upload to skip LLM
        currentFileFields = data.fields;

        document.getElementById("resVendor").textContent = data.fields.vendor || "Unknown";
        document.getElementById("resDate").textContent = data.fields.date || "Unknown";
        document.getElementById("resAmount").textContent = data.fields.amount || "--";

        // Show the Result Area
        resultArea.style.display = "block";
        document.getElementById("resultGrid").style.display = "grid";

        // Hide "Success" badge and Drive link for now (this is just preview)
        driveLinkContainer.style.display = "none";
        if (clearBtn) clearBtn.style.display = "none";
      }
    } else if (data.status === "rate_limit") {
      toast.remove();
      showToast("⚠️ Quota Exceeded. Please wait 1 min.", "error");
      filenameInput.value = "Rate_Limit_Wait_1_Min";
    } else {
      toast.remove();
      showToast("Analysis Failed", "error");
      filenameInput.value = file.name;
    }

  } catch (err) {
    console.error("Analysis failed", err);
    toast.remove();
    showToast("Server Connection Error", "error");
    filenameInput.value = file.name;
  }
}

/**
 * 2. Delete/Reset Selection
 */
function handleDeleteSelection() {
  currentFile = null;
  currentFileFields = null;
  fileInput.value = "";

  // UI: Show Dropzone, Hide Preview
  previewContainer.style.display = 'none';
  dropzoneContent.style.display = 'block';
  previewIcon.innerHTML = '';

  // Clear toasts
  document.getElementById('toastContainer').innerHTML = '';

  // Reset Result Area if it was shown (since we are deleting the current selection)
  resultArea.style.display = "none";
}

/**
 * 3. Process/Upload Logic (The "Save" button action)
 */
async function processSelectedFile() {
  if (!currentFile) return;

  const newName = filenameInput.value.trim();
  if (!newName) {
    alert("File name cannot be empty.");
    return;
  }

  handleFileUpload(currentFile, newName);
}

/**
 * 4. File Upload Handler (Backend Comm - REAL SAVE)
 */
async function handleFileUpload(file, customName) {
  if (!file) return;

  // Show Toast
  const toast = showToast("Uploading and Saving to Drive...", "progress");

  // Reset UI: Hide result area initially (Clean UI)
  resultArea.style.display = "none";

  resultJson.textContent = "";
  driveLinkContainer.style.display = "none";
  if (clearBtn) clearBtn.style.display = "none";

  const formData = new FormData();
  const finalName = customName || file.name;
  if (finalName.toLowerCase().endsWith(".pdf") || finalName.toLowerCase().endsWith(".png") || finalName.toLowerCase().endsWith(".jpg") || finalName.toLowerCase().endsWith(".jpeg")) {
    formData.append("file", file, finalName);
  } else {
    const ext = file.name.split('.').pop();
    formData.append("file", file, `${finalName}.${ext}`);
  }

  // Pass cached fields if available to save API quota
  if (currentFileFields) {
    formData.append("provided_vendor", currentFileFields.vendor);
    formData.append("provided_date", currentFileFields.date);
    formData.append("provided_amount", currentFileFields.amount);
  }

  try {
    // Use custom name flag if we have a custom name
    const queryParams = customName ? "?use_custom_name=true" : "";
    const res = await fetch(`${BACKEND_URL}/upload${queryParams}`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    // Complete progress
    if (toast.querySelector('.toast-progress-bar')) {
      toast.querySelector('.toast-progress-bar').style.width = '100%';
    }

    const resGrid = document.getElementById("resultGrid");
    const rawJson = document.getElementById("resultJson");

    resGrid.style.display = "grid";
    rawJson.style.display = "none";

    if (data.status === "success") {
      setTimeout(() => {
        toast.remove();
        showToast("File Saved Successfully!", "success");
      }, 500);

      // Show Result Area ONLY on Success
      resultArea.style.display = "block";

      document.getElementById("resVendor").textContent = data.fields.vendor || "Unknown";
      document.getElementById("resDate").textContent = data.fields.date || "Unknown";
      document.getElementById("resAmount").textContent = data.fields.amount || "--";



      if (data.drive_link) {
        driveLinkContainer.style.display = "block";
        driveLinkBtn.href = data.drive_link;
      } else {
        driveLinkContainer.style.display = "none";
      }

      currentFile = null;
      fileInput.value = "";
      previewContainer.style.display = 'none';
      dropzoneContent.style.display = 'block';

      resultArea.scrollIntoView({ behavior: 'smooth', block: 'center' });

    } else {
      // Error: Keep Result Area Hidden, show Toast
      setTimeout(() => {
        toast.remove();
        showToast(`Error: ${data.detail}`, "error");
      }, 500);

      // No need to populate hidden result area
    }

  } catch (err) {
    console.error(err);
    toast.remove();
    showToast("Upload Failed", "error");
    // Result Area remains hidden
  } finally {
    // Show Clear Button if result area is visible (Success case)
    if (resultArea.style.display !== "none" && clearBtn) {
      clearBtn.style.display = "inline-flex";
    }
    checkDriveStatus();
  }
}

/**
 * 5. Handle Clear (Reset Everything)
 */
function handleClear() {
  resultArea.style.display = "none";
  handleDeleteSelection();
}

// --- Event Listeners ---

fileInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    handleFileSelection(e.target.files[0]);
  }
});

dropzoneContent.addEventListener("click", () => {
  fileInput.click();
});

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", (e) => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");

  if (e.dataTransfer.files.length > 0) {
    handleFileSelection(e.dataTransfer.files[0]);
  }
});

previewContainer.addEventListener("click", (e) => {
  e.stopPropagation();
});


// Helper: Smooth scroll to upload section
function scrollToUpload() {
  const el = document.getElementById("app-section");
  if (el) el.scrollIntoView({ behavior: "smooth" });
}

function scrollToHowItWorks() {
  const el = document.getElementById("how-it-works");
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  } else {
    console.error("Element #how-it-works not found");
  }
}

// Export for onclick usage in HTML
window.scrollToUpload = scrollToUpload;
window.scrollToHowItWorks = scrollToHowItWorks;
window.handleLogout = handleLogout;
window.handleDeleteSelection = handleDeleteSelection;
window.processSelectedFile = processSelectedFile;
window.handleClear = handleClear;

// Init
checkDriveStatus();


