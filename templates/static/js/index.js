let currentPage = 1;
const limit = 12;
let isSearchMode = false;

async function fetchFilterOptions() {
    try {
        const yearResponse = await fetch('http://127.0.0.1:5000/languages/years');
        const designerResponse = await fetch('http://127.0.0.1:5000/languages/designers');

        const yearsData = await yearResponse.json();
        const designersData = await designerResponse.json();

        const yearSelect = document.getElementById('year-filter');
        const designerSelect = document.getElementById('designer-filter');

        yearsData.years.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        });

        designersData.designers.forEach(designer => {
            const option = document.createElement('option');
            option.value = designer;
            option.textContent = designer;
            designerSelect.appendChild(option);
        });

    } catch (error) {
        console.error('Error fetching filter options:', error);
    }
}

function abbreviateText(text, maxLength = 20) {
    if (text.length > maxLength) {
        return text.slice(0, maxLength) + '...';
    }
    return text;
}

async function fetchLanguages(page = 1) {
    isSearchMode = false;
    currentPage = page;

    document.getElementById('search-input').value = '';
    const year = document.getElementById('year-filter').value;
    const designer = document.getElementById('designer-filter').value;
    let apiUrl = `http://127.0.0.1:5000/languages/details?page=${page}&limit=${limit}`;

    if (year) {
        apiUrl += `&year=${year}`;
    }

    if (designer) {
        apiUrl += `&designer=${designer}`;
    }

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        const container = document.getElementById('cards-container');
        container.innerHTML = '';

        if (data.data && data.data.length > 0) {
            data.data.forEach(language => {
                const abbreviatedName = abbreviateText(language.languageName || 'N/A', 20);
                const card = `
                    <div class="card" onclick="redirectToLanguagePage('${language.languageName}')">
                        <div class="card-inner">
                            <div class="card-front">
                                <h3 title="${language.languageName || 'N/A'}">
                                    ${abbreviatedName}
                                </h3>
                                <p>Released: ${language.releasedYear || 'N/A'}</p>
                                <p>Designer: ${language.designer || 'N/A'}</p>
                            </div>
                            <div class="card-back">
                                <h3>Details</h3>
                                <p>Computational Classes: ${language.computationalClasses?.join(', ') || 'N/A'}</p>
                                <p>Paradigms: ${language.paradigms?.join(', ') || 'N/A'}</p>
                                <p>Usabilities: ${language.usabilities?.join(', ') || 'N/A'}</p>
                                <p>Technical Characteristics: ${language.technicalCharacteristics?.join(', ') || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                `;
                container.innerHTML += card;
            });

            document.getElementById('pageNumber').textContent = `Page: ${currentPage}`;
            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = data.data.length < limit;
        } else {
            container.innerHTML = '<p>No results found.</p>';
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('cards-container').innerHTML = '<p>Error fetching data. Please try again later.</p>';
    }
}


async function fetchSearchResults(page = 1) {
    isSearchMode = true;
    currentPage = page;

    const searchTerm = document.getElementById('search-input').value.trim();
    const apiUrl = `http://127.0.0.1:5000/languages/search?page=${page}&limit=${limit}&name=${encodeURIComponent(searchTerm)}`;
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        const container = document.getElementById('cards-container');
        container.innerHTML = '';

        if (data.data && data.data.length > 0) {
            data.data.forEach(language => {
                const abbreviatedName = abbreviateText(language.languageName || 'N/A', 20);
                const card = `
                    <div class="card" onclick="redirectToLanguagePage('${language.languageName}')">
                        <div class="card-inner">
                            <div class="card-front">
                                <h3 title="${language.languageName}">${abbreviatedName}</h3>
                                <p>Released: ${language.releasedYear || 'N/A'}</p>
                                <p>Designer: ${language.designer || 'N/A'}</p>
                            </div>
                            <div class="card-back">
                                <h3>Details</h3>
                                <p>Computational Classes: ${language.computationalClasses?.join(', ') || 'N/A'}</p>
                                <p>Paradigms: ${language.paradigms?.join(', ') || 'N/A'}</p>
                                <p>Usabilities: ${language.usabilities?.join(', ') || 'N/A'}</p>
                                <p>Technical Characteristics: ${language.technicalCharacteristics?.join(', ') || 'N/A'}</p>
                            </div>
                        </div>
                    </div>`;
                container.innerHTML += card;
            });

            document.getElementById('pageNumber').textContent = `Page: ${currentPage}`;
            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = data.data.length < limit;
        } else {
            container.innerHTML = '<p>No results found.</p>';
        }
    } catch (error) {
        console.error('Error fetching search results:', error);
        document.getElementById('cards-container').innerHTML = '<p>Error fetching data. Please try again later.</p>';
    }
}


function changePage(direction) {
    const nextPage = currentPage + direction;
    if (nextPage < 1) return;

    currentPage = nextPage;

    if (isSearchMode) {
        fetchSearchResults(currentPage);
    } else {
        fetchLanguages(currentPage);
    }
}


function redirectToLanguagePage(languageName) {
    window.location.href = `/languages/${encodeURIComponent(languageName)}`;
}

fetchFilterOptions();
fetchLanguages(currentPage);
