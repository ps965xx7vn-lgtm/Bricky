// Print order button handler
document.addEventListener('DOMContentLoaded', function() {
    const printBtn = document.getElementById('print-order-btn');
    if (printBtn) {
        printBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    }
});
