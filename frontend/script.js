document.addEventListener('DOMContentLoaded', () => {
    // --- CONFIGURATION ---
    // Replace these with your actual API Gateway endpoint URLs
    const API_GENERATE_URL = 'https://<API-ID>.execute-api.<REGION>.amazonaws.com/prod/generate-presigned-url';
    const API_SEARCH_URL = 'https://<API-ID>.execute-api.<REGION>.amazonaws.com/prod/search';

    // --- DOM ELEMENTS ---
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const searchResultsContainer = document.getElementById('search-results');

    // --- UPLOAD LOGIC ---
    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const file = fileInput.files[0];
        if (!file) {
            alert('Por favor, seleccione un archivo para cargar.');
            return;
        }

        updateStatus('Iniciando carga...');
        try {
            // 1. Get a pre-signed URL from our backend
            const presignedUrlResponse = await fetch(API_GENERATE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fileName: file.name })
            });

            if (!presignedUrlResponse.ok) {
                throw new Error('No se pudo obtener la URL de carga.');
            }

            const { uploadUrl } = await presignedUrlResponse.json();

            // 2. Upload the file directly to S3 using the pre-signed URL
            updateStatus(`Cargando archivo: ${file.name}...`);
            const uploadResponse = await fetch(uploadUrl, {
                method: 'PUT',
                body: file,
                headers: { 'Content-Type': file.type }
            });

            if (!uploadResponse.ok) {
                throw new Error('La carga del archivo a S3 falló.');
            }

            updateStatus(`¡Éxito! El archivo "${file.name}" fue cargado y está siendo procesado.`);
            uploadForm.reset();

        } catch (error) {
            console.error('Error en la carga:', error);
            updateStatus(`Error: ${error.message}`);
        }
    });

    // --- SEARCH LOGIC ---
    searchForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const query = searchInput.value.trim();
        if (!query) {
            alert('Por favor, ingrese un término de búsqueda.');
            return;
        }

        displayResults(null, 'Buscando...');
        try {
            const searchUrl = `${API_SEARCH_URL}?q=${encodeURIComponent(query)}`;
            const response = await fetch(searchUrl);

            if (!response.ok) {
                throw new Error('La búsqueda falló.');
            }

            const results = await response.json();
            displayResults(results);

        } catch (error) {
            console.error('Error en la búsqueda:', error);
            displayResults(null, `Error: ${error.message}`);
        }
    });

    // --- UI HELPER FUNCTIONS ---
    function updateStatus(message) {
        // A simple status update. Could be replaced with a more robust notification system.
        console.log(message);
        alert(message);
    }

    function displayResults(results, message = '') {
        searchResultsContainer.innerHTML = ''; // Clear previous results

        if (message) {
            const messageElement = document.createElement('p');
            messageElement.textContent = message;
            searchResultsContainer.appendChild(messageElement);
        }

        if (results && results.length > 0) {
            const list = document.createElement('ul');
            results.forEach(result => {
                const item = document.createElement('li');
                item.innerHTML = `
                    <h3>${result.s3_key} (Score: ${result.score.toFixed(2)})</h3>
                    <div class="highlight">
                        ${result.highlight ? result.highlight.join(' ... ') : 'No highlight available.'}
                    </div>
                    <p><strong>Entidades:</strong> ${result.entities.map(e => e.Text).join(', ') || 'N/A'}</p>
                `;
                list.appendChild(item);
            });
            searchResultsContainer.appendChild(list);
        } else if (!message) {
             const messageElement = document.createElement('p');
            messageElement.textContent = 'No se encontraron resultados.';
            searchResultsContainer.appendChild(messageElement);
        }
    }
});
