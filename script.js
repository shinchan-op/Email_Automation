// Load current attachment info on page load
window.addEventListener('load', loadCurrentAttachment);

async function loadCurrentAttachment() {
    try {
        const response = await fetch('/attachment_info');
        const result = await response.json();
        
        if (result.filename && result.exists) {
            showCurrentAttachment(result.filename);
        }
    } catch (err) {
        console.log('No current attachment');
    }
}

function showCurrentAttachment(filename) {
    const currentAttachmentDiv = document.getElementById('currentAttachment');
    const currentAttachmentName = document.getElementById('currentAttachmentName');
    
    currentAttachmentName.textContent = filename;
    currentAttachmentDiv.classList.remove('hidden');
}

// Handle attachment upload
document.getElementById('attachmentForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const attachmentFile = document.getElementById('attachment').files[0];
    const attachmentStatus = document.getElementById('attachmentStatus');
    
    if (!attachmentFile) {
        showMessage(attachmentStatus, 'Please select a file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('attachment', attachmentFile);

    try {
        // Show uploading state
        showMessage(attachmentStatus, 'Uploading attachment...', 'info');
        
        const response = await fetch('/upload_attachment', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (result.status === 'error') {
            showMessage(attachmentStatus, result.message, 'error');
        } else {
            showMessage(attachmentStatus, result.message, 'success');
            showCurrentAttachment(result.filename);
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
    const statusDiv = document.getElementById('status');
    const errorDiv = document.getElementById('error');
    
    // Hide previous messages
    statusDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');

    const formData = new FormData();
    formData.append('excel_file', excelFile);
    formData.append('template', template);

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

        // Show success summary with attachment name
        let successMessage = `<strong>${result.summary}</strong><br><br>`;
        successMessage += `<div class="mb-2"><strong>📎 Attachment:</strong> <span class="text-blue-600">${result.attachment_name}</span></div>`;
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
