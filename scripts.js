document.getElementById('uploadButton').addEventListener('click', function () {
  // Create an input element for file upload
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '*'; // Accept all file types; you can modify this as needed

  // Trigger the file upload dialog
  input.click();

  // Handle file selection
  input.onchange = function () {
      const file = input.files[0]; // Get the selected file
      if (file) {
          // Clear status before upload
          const statusMessage = document.createElement('div'); // Create status message element
          document.body.appendChild(statusMessage); // Append it to the body or a specific container
          setTimeout(() => {
              statusMessage.textContent = `${file.name} uploaded successfully!`;
              addFileTile(file); // Call function to create the tile
          }, 1000);
      }
  };
});

function addFileTile(file) {
  const fileGrid = document.querySelector('.file-grid'); // Select the file grid
  const tile = document.createElement('div'); // Create a new tile div
  tile.classList.add('file-tile'); // Add a class for styling

  // Add remove icon
  const removeIcon = document.createElement('div');
  removeIcon.classList.add('remove-icon');
  removeIcon.textContent = '−'; // Dash icon
  tile.appendChild(removeIcon);

  // Add file preview if it's an image, or a placeholder for non-image files
  if (file.type.startsWith('image/')) {
      const img = document.createElement('img');
      img.src = URL.createObjectURL(file);  // Create preview URL for image
      img.alt = file.name;
      tile.appendChild(img);
  } else if (file.type === 'application/pdf') {
      const placeholder = document.createElement('div');
      placeholder.textContent = 'PDF Preview';
      placeholder.style.height = '100px';
      placeholder.style.lineHeight = '100px';
      placeholder.style.backgroundColor = '#f4f4f4';
      placeholder.style.color = '#aaa';
      tile.appendChild(placeholder);
  } else {
      const placeholder = document.createElement('div');
      placeholder.textContent = 'No Preview';
      placeholder.style.height = '100px';
      placeholder.style.lineHeight = '100px';
      placeholder.style.backgroundColor = '#f4f4f4';
      placeholder.style.color = '#aaa';
      tile.appendChild(placeholder);
  }

  // Add file name and type
  const fileName = document.createElement('div');
  fileName.classList.add('file-name');
  fileName.textContent = file.name;
  tile.appendChild(fileName);

  const fileType = document.createElement('div');
  fileType.classList.add('file-type');
  fileType.textContent = file.type || 'Unknown file type';
  tile.appendChild(fileType);

  // Append the tile to the grid
  fileGrid.appendChild(tile);

  // Add double-click event to open PDF
  if (file.type === 'application/pdf') {
      tile.addEventListener('dblclick', function() {
          openPDF(URL.createObjectURL(file));  // Open PDF viewer with the file
      });
  }

  // Add click event to the remove icon
  removeIcon.addEventListener('click', function(event) {
      event.stopPropagation(); // Prevent triggering the tile click event
      const confirmation = confirm(`Are you sure you want to remove "${file.name}"?`);
      if (confirmation) {
          fileGrid.removeChild(tile);  // Remove tile from grid
          statusMessage.textContent = `${file.name} has been removed.`; // Update status message
      }
  });
}

// Function to open PDF in modal
function openPDF(pdfUrl) {
  const modal = document.getElementById('pdfModal');
  const pdfViewer = document.getElementById('pdfViewer');
  pdfViewer.src = pdfUrl;  // Set PDF source
  modal.style.display = "block";  // Show modal

  // Close modal when clicking on the close button
  document.querySelector('.close').onclick = function() {
    modal.style.display = "none";  // Hide modal
    pdfViewer.src = "";  // Clear PDF source
  }

  // Close modal when clicking anywhere outside of the modal
  window.onclick = function(event) {
    if (event.target === modal) {
      modal.style.display = "none";  // Hide modal
      pdfViewer.src = "";  // Clear PDF source
    }
  }
}

