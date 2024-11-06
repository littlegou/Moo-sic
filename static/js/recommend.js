function openPopup() {
    document.getElementById('popupForm').style.display = 'flex';
}

function closePopup() {
    document.getElementById('popupForm').style.display = 'none';
}

window.onclick = function (event) {
    const popup = document.getElementById('popupForm');
    if (event.target == popup) {
        closePopup();
    }
}
