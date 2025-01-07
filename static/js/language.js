document.getElementById('back-button').addEventListener('click', () => {
        window.location.href = '/';
    });
console.log(similarLanguages);
const cardsContainer = document.getElementById('cards-container');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
let currentPage = 0;
const cardsPerPage = 4;

function renderCards() {
    cardsContainer.innerHTML = '';
    const start = currentPage * cardsPerPage;
    const end = Math.min(start + cardsPerPage, similarLanguages.length);
    const visibleLanguages = similarLanguages.slice(start, end);
    visibleLanguages.forEach(lang => {
        const card = document.createElement('div');
        card.classList.add('card');
        card.innerHTML = `
            <h2><a href="${lang.language}" target="_blank">${lang.language}</a></h2>
        `;
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
    if ((currentPage + 1) * cardsPerPage < similarLanguages.length) {
        currentPage++;
        renderCards();
    }
});

renderCards();
