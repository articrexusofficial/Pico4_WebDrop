const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const fileList = document.getElementById('file-list');
const uploadBtn = document.getElementById('upload-btn');

// Store files to be uploaded (optional, for actual upload logic)
let filesToUpload = [];

// --- Event Listeners ---

// Trigger hidden file input click when browse button is clicked
browseBtn.addEventListener('click', () => {
    fileInput.click();
});

// Trigger hidden file input click when drop zone is clicked
dropZone.addEventListener('click', (e) => {
    // Prevent triggering if the click is on the button inside
    if (e.target !== browseBtn) {
         fileInput.click();
    }
});

// Handle file selection via browse
fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
    // Reset input value to allow selecting the same file again
    fileInput.value = null;
});

// Drag and Drop Events
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault(); // Prevent default browser behavior
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length) {
        // Temporarily set the input files to allow handleFiles to work correctly
        // with the `accept` attribute filtering if needed.
        // Note: This might not be strictly necessary if filtering happens in JS,
        // but can be useful for consistency.
        try {
            fileInput.files = droppedFiles;
        } catch (error) {
            console.warn("Could not directly assign DataTransfer files to input.files", error);
        }
        handleFiles(droppedFiles);
    }
});

// Upload Button Click (Placeholder)
uploadBtn.addEventListener('click', () => {
    if (filesToUpload.length === 0) {
        alert('Please select files to upload first.');
        return;
    }

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';

    const uploadPromises = filesToUpload.map(file => {
        const formData = new FormData();
        formData.append('file', file, file.name);

        return fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok && response.status !== 302) {
                return response.text().then(text => {
                    throw new Error(`Upload failed for ${file.name}: ${text || response.statusText}`);
                });
            }
            return file.name;
        });
    });

    Promise.allSettled(uploadPromises)
        .then(results => {
            const successfulUploads = results.filter(r => r.status === 'fulfilled').length;
            const failedUploads = results.filter(r => r.status === 'rejected').length;

            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload';

            fileList.innerHTML = '';
            filesToUpload = [];

            window.location.reload();
        });
});


// --- Helper Functions ---

/**
 * Handles the selected or dropped files.
 * @param {FileList} files - The files selected or dropped.
 */
function handleFiles(files) {
    // Clear previous selections shown in the list if you want single batch upload
    // fileList.innerHTML = '';
    // filesToUpload = [];

    for (const file of files) {
        // Basic validation (optional: check type more strictly if needed)
        if (!file.type.startsWith('image/')) {
             console.warn(`File skipped: ${file.name} is not an image.`);
            continue; // Skip non-image files
        }

         // Prevent duplicates (optional)
        if (filesToUpload.some(existingFile => existingFile.name === file.name && existingFile.size === file.size)) {
            console.warn(`File skipped: ${file.name} already added.`);
            continue;
        }

        // Add file to our list for potential upload
        filesToUpload.push(file);

        // Create list item and add to the display
        const listItem = createFileListItem(file);
        fileList.appendChild(listItem);
    }
     // Log the current set of files ready for upload
    console.log("Files ready for upload:", filesToUpload);
}

/**
 * Creates an HTML list item element for a given file.
 * @param {File} file - The file object.
 * @returns {HTMLLIElement} The created list item element.
 */
function createFileListItem(file) {
    const li = document.createElement('li');
    li.classList.add('file-item');

    const fileNameSpan = document.createElement('span');
    fileNameSpan.classList.add('file-name');
    fileNameSpan.textContent = file.name;
    fileNameSpan.title = file.name; // Show full name on hover if truncated

    const fileSizeSpan = document.createElement('span');
    fileSizeSpan.classList.add('file-size');
    fileSizeSpan.textContent = formatFileSize(file.size);

    li.appendChild(fileNameSpan);
    li.appendChild(fileSizeSpan);

    // Optional: Add a remove button for each file
    // const removeBtn = document.createElement('button');
    // removeBtn.textContent = '✖';
    // removeBtn.style.background = 'none';
    // removeBtn.style.border = 'none';
    // removeBtn.style.color = '#aaa';
    // removeBtn.style.cursor = 'pointer';
    // removeBtn.onclick = () => {
    //     li.remove();
    //     filesToUpload = filesToUpload.filter(f => f !== file); // Remove from upload array
    //     console.log("Files ready for upload:", filesToUpload);
    // };
    // li.appendChild(removeBtn);


    return li;
}

/**
 * Formats file size from bytes to KB, MB, GB.
 * @param {number} bytes - The file size in bytes.
 * @returns {string} The formatted file size string.
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    // Use toFixed(1) for one decimal place as in the image (e.g., 1.2 MB)
}
