// Load current attachment info on page load
window.addEventListener('load', loadCurrentAttachment);

async function loadCurrentAttachment() {
    try {
        const response = await fetch('/attachment_info');
        const result = await response.json();
        
        if (result.filenames && result.filenames.length > 0 && result.exists) {
            showCurrentAttachment(result.filenames);
        }
    } catch (err) {
        console.log('No current attachments');
    }
}

function showCurrentAttachment(filenames) {
    const currentAttachmentDiv = document.getElementById('currentAttachment');
    const currentAttachmentList = document.getElementById('currentAttachmentList');
    
    // Clear existing list items
    currentAttachmentList.innerHTML = '';
    
    // Populate the list with filenames
    filenames.forEach(filename => {
        const li = document.createElement('li');
        li.textContent = filename;
        currentAttachmentList.appendChild(li);
    });
    
    currentAttachmentDiv.classList.remove('hidden');
}

// Handle preview emails
document.getElementById('previewButton').addEventListener('click', async function(event) {
    event.preventDefault();
    
    const excelFile = document.getElementById('excel_file').files[0];
    const template = document.getElementById('template').value;
    const signature = document.getElementById('signature').value;
    const previewModal = document.getElementById('previewModal');
    const previewContent = document.getElementById('previewContent');
    const errorDiv = document.getElementById('error');
    
    // Hide previous messages
    errorDiv.classList.add('hidden');
    
    if (!excelFile) {
        showMessage(errorDiv, 'Please upload an Excel file first', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('excel_file', excelFile);
    formData.append('template', template);
    formData.append('signature', signature);

    try {
        const response = await fetch('/preview_emails', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (result.status === 'error') {
            if (result.invalid_emails) {
                let errorMessage = 'Invalid email addresses found:<br>' ;
                result.invalid_emails.forEach(item => {
                    errorMessage += 'Row ${item.row}: ${item.email}<br>' ;
                });
                showMessage(errorDiv, errorMessage, 'error');
            } else {
                showMessage(errorDiv, result.message, 'error');
            }
            return;
        }

        // Clear previous preview content
        previewContent.innerHTML = '';

        // Display each previewed email
        result.previews.forEach(preview => {
            const previewDiv = document.createElement('div');
            previewDiv.className = 'border-b border-gray-200 pb-4';
            previewDiv.innerHTML = `
                <div class="mb-2">
                    <strong>To:</strong> <span class="text-blue-600">${preview.email}</span>
                </div>
                <div class="mb-2">
                    <strong>Subject:</strong> <span class="text-blue-600">${preview.subject}</span>
                </div>
                <div class="mb-2">
                    <strong>Body:</strong>
                    <div class="mt-1 text-gray-700 whitespace-pre-wrap">${preview.body}</div>
                </div>
            `;
            previewContent.appendChild(previewDiv);
        });

        // Show the modal
        previewModal.classList.remove('hidden');
        
    } catch (err) {
        showMessage(errorDiv, `Error: ${err.message}`, 'error');
    }
});

// Close preview modal
document.getElementById('closePreview').addEventListener('click', function() {
    const previewModal = document.getElementById('previewModal');
    previewModal.classList.add('hidden');
});

// Handle attachment upload
document.getElementById('attachmentForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const attachmentFiles = document.getElementById('attachment').files;
    const attachmentStatus = document.getElementById('attachmentStatus');
    
    if (!attachmentFiles || attachmentFiles.length === 0) {
        showMessage(attachmentStatus, 'Please select at least one file', 'error');
        return;
    }

    const formData = new FormData();
    for (let file of attachmentFiles) {
        formData.append('attachments', file);
    }

    try {
        // Show uploading state
        showMessage(attachmentStatus, 'Uploading attachment(s)...', 'info');
        
        const response = await fetch('/upload_attachment', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (result.status === 'error') {
            showMessage(attachmentStatus, result.message, 'error');
        } else {
            showMessage(attachmentStatus, result.message, 'success');
            showCurrentAttachment(result.filenames);
        }
    } catch (err) {
        showMessage(attachmentStatus, `Error: ${err.message}`, 'error');
    }
});

// Handle draft creation
document.getElementById('emailForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const excelFile = document.getElementById('excel_file').files[0];
    const template = document.getElementById('template').value;
    const signature = document.getElementById('signature').value;
    const statusDiv = document.getElementById('status');
    const errorDiv = document.getElementById('error');
    
    // Hide previous messages
    statusDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');

    const formData = new FormData();
    formData.append('excel_file', excelFile);
    formData.append('template', template);
    formData.append('signature', signature);

    try {
        // Show loading state
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '⏳ Creating Drafts...';
        submitBtn.disabled = true;

        const response = await fetch('/create_drafts', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        // Restore button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;

        if (result.status === 'error') {
            showMessage(errorDiv, result.message, 'error');
            return;
        }

        // Show success summary with attachment names
        let successMessage = `<strong>${result.summary}</strong><br><br>`;
        successMessage += `<div class="mb-2"><strong>📎 Attachment(s):</strong> <span class="text-blue-600">${result.attachment_names.join(', ')}</span></div>`;
        successMessage += '<div class="space-y-1 max-h-60 overflow-y-auto">';
        
        result.results.forEach(res => {
            if (res.status === 'success') {
                successMessage += `<div class="text-green-600">${res.message}</div>`;
            } else {
                successMessage += `<div class="text-red-600">${res.message}</div>`;
            }
        });
        
        // Add invalid email errors if any
        if (result.invalid_emails) {
            successMessage += `<div class="mb-2 text-red-600"><strong>Invalid Emails:</strong><br>`;
            result.invalid_emails.forEach(item => {
                successMessage += `Row ${item.row}: ${item.email}<br>`;
            });
            successMessage += `</div>`;
        }

        successMessage += '<div class="space-y-1 max-h-60 overflow-y-auto">';
        
        result.results.forEach(res => {
            if (res.status === 'success') {
                successMessage += `<div class="text-green-600">${res.message}</div>`;
            } else {
                successMessage += `<div class="text-red-600">${res.message}</div>`;
            }
        });
        
        successMessage += '</div>';
        showMessage(statusDiv, successMessage, 'success');
        
    } catch (err) {
        showMessage(errorDiv, `Error: ${err.message}`, 'error');
        // Restore button on error
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
});

function showMessage(element, message, type) {
    element.innerHTML = message;
    element.classList.remove('hidden');
    
    if (type === 'success') {
        element.className = 'mt-6 p-4 bg-green-50 rounded-lg text-green-700 text-sm';
    } else if (type === 'info') {
        element.className = 'mt-2 text-sm text-blue-600';
    } else {
        element.className = 'mt-6 p-4 bg-red-50 rounded-lg text-red-700 text-sm';
    }
}