document.addEventListener('DOMContentLoaded', function () {
    const languageElement = document.getElementById('language-name');
    const backButton = document.getElementById('back-button');
    const popupModal = document.getElementById('popup-modal');
    const popupCloseButton = document.getElementById('close-popup');
    const popupTableBody = document.getElementById('popup-comparison-table-body');

    if (!languageElement) {
        console.error("Error: Element with ID 'language-name' not found.");
        return;
    }

    const langName = languageElement.textContent.trim();

    if (backButton) {
        backButton.addEventListener('click', function () {
            window.location.href = '/';
        });
    } else {
        console.error("Error: Back button not found.");
    }

    function loadComparisonDataInPopup(similarLanguage) {
        const popupTableBody = document.getElementById('popup-comparison-table-body');
        const popupHeaderLang1 = document.getElementById('popup-header-lang1');
        const popupHeaderLang2 = document.getElementById('popup-header-lang2');

        if (!popupTableBody) {
            console.error("Error: 'popup-comparison-table-body' element not found.");
            return;
        }

        fetch('/compare_languages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "given_language": langName,
                "similar_language": similarLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("API Error:", data.error);
                return;
            }

            popupTableBody.innerHTML = '';
            popupHeaderLang1.textContent = langName;
            popupHeaderLang2.textContent = similarLanguage;

            data.comparison.forEach(item => {
                const property = item.property || "N/A";
                const valueGiven = Array.isArray(item.given_language_value) ? item.given_language_value.join(', ') : item.given_language_value || "N/A";
                const valueSimilar = Array.isArray(item.similar_language_value) ? item.similar_language_value.join(', ') : item.similar_language_value || "N/A";
                const similarity = item.similarity || "Unknown";
                const row = document.createElement('tr');

                let similarityClass = '';
                if (similarity === 'Similar') {
                    similarityClass = 'similar';
                } else if (similarity === 'Different') {
                    similarityClass = 'different';
                } else {
                    similarityClass = 'no-similarity';
                }

                row.classList.add(similarityClass);
                row.innerHTML = `
                    <td>${property}</td>
                    <td>${valueGiven}</td>
                    <td>${valueSimilar}</td>
                    <td>${similarity}</td>
                `;
                popupTableBody.appendChild(row);
            });

            popupModal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Error fetching comparison data:', error);
        });
    }

    if (popupCloseButton) {
        popupCloseButton.addEventListener('click', function () {
            popupModal.style.display = 'none';
        });
    }

    popupModal.addEventListener('click', function (event) {
        if (event.target === popupModal) {
            popupModal.style.display = 'none';
        }
    });

    const cardsContainer = document.getElementById('cards-container');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    let currentPage = 0;
    const cardsPerPage = 4;

    if (window.similarLanguages && Array.isArray(window.similarLanguages) && window.similarLanguages.length > 0) {
        function renderCards() {
            cardsContainer.innerHTML = '';
            const start = currentPage * cardsPerPage;
            const end = Math.min(start + cardsPerPage, window.similarLanguages.length);
            const visibleLanguages = window.similarLanguages.slice(start, end);

            visibleLanguages.forEach(lang => {
                const card = document.createElement('div');
                card.classList.add('card');
                card.innerHTML = `
                    <h2><a href="${lang.language}" target="_blank">${lang.language}</a></h2>
                `;
                card.dataset.language = lang.language;
                card.addEventListener('click', () => loadComparisonDataInPopup(lang.language));
                cardsContainer.appendChild(card);
            });
        }

        prevBtn.addEventListener('click', () => {
            if (currentPage > 0) {
                currentPage--;
                renderCards();
            }
        });

        nextBtn.addEventListener('click', () => {
            if ((currentPage + 1) * cardsPerPage < window.similarLanguages.length) {
                currentPage++;
                renderCards();
            }
        });

        renderCards();
    } else {
        console.error('similarLanguages is not defined or empty.');
    }
});
