document.addEventListener('DOMContentLoaded', () => {
    const backButton = document.querySelector('.back-button');

    backButton.addEventListener('click', () => {
        console.log('Navigating back to the home page.');
    });
});
