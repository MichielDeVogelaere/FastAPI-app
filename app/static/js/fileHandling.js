async function downloadFile(url, filename) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Download failed');

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
    } catch (error) {
        showError('Failed to download file: ' + error.message);
    }
}

function showError(message) {
    const error = document.getElementById('error');
    error.textContent = message;
    error.style.display = 'block';
    setTimeout(() => {
        error.style.display = 'none';
    }, 5000);
}

async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const progress = document.getElementById('progress');
    const error = document.getElementById('error');
    const downloads = document.getElementById('downloads');
    const downloadGrid = document.getElementById('downloadGrid');

    if (!fileInput.files.length) {
        showError('Please select a file first');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    progress.style.display = 'block';
    error.style.display = 'none';
    downloads.style.display = 'none';
    downloadGrid.innerHTML = '';

    try {
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            downloadGrid.innerHTML = '';
            const karaokeFiles = data.output_files.filter(file => file.endsWith('karaoke-version.mp3'));

            karaokeFiles.forEach(file => {
                const downloadUrl = `/download/${data.base_path}/${file}`;
                downloadGrid.innerHTML += `
                    <a href="#"
                       class="download-btn"
                       onclick="downloadFile('${downloadUrl}', '${file}'); return false;">
                        Download ${file.split('.')[0]}
                    </a>
                `;
            });
            if (karaokeFiles.length === 0) {
                showError('No karaoke-version.mp3 file found.');
            } else {
                downloads.style.display = 'block';
            }
        } else {
            showError(data.error || 'Upload failed');
        }
    } catch (e) {
        showError('An error occurred during upload');
    } finally {
        progress.style.display = 'none';
    }
}
