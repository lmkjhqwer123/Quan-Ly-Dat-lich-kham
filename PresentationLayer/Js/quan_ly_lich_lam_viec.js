function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function toggleShiftOptions(modalId, show) {
    const shiftOptions = document.getElementById('shiftOptions-' + modalId);
    if (show) {
        shiftOptions.classList.remove('hidden');
    } else {
        shiftOptions.classList.add('hidden');
    }
}


// Đóng modal khi nhấp ra ngoài (gán cho tất cả modal)
window.addEventListener('click', (event) => {
    document.querySelectorAll('.modal').forEach(modal => {
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    });
});
