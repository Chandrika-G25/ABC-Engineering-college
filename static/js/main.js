/* Student Management System - Main JavaScript Interactive Logic */

document.addEventListener('DOMContentLoaded', () => {
    // Sidebar toggle for mobile responsive view
    const toggleBtn = document.getElementById('toggleSidebarBtn');
    const sidebar = document.getElementById('appSidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Auto-dismiss alert notifications after 4 seconds
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });
});
