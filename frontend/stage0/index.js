/* ============================================
   TODO CARD - INTERACTIVE BEHAVIOR
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    const todoCard = document.querySelector('[data-testid="test-todo-card"]');
    const checkbox = document.querySelector('[data-testid="test-todo-complete-toggle"]');
    const editBtn = document.querySelector('[data-testid="test-todo-edit-button"]');
    const deleteBtn = document.querySelector('[data-testid="test-todo-delete-button"]');
    const timeRemaining = document.querySelector('[data-testid="test-todo-time-remaining"]');
    const statusBadge = document.querySelector('[data-testid="test-todo-status"]');

    // Fixed due date: March 1, 2026, 18:00 UTC
    const DUE_DATE = new Date('2026-03-01T18:00:00Z');

    /**
     * Calculate readable time remaining text
     * @param {Date} dueDate - The due date
     * @returns {string} - Friendly time remaining text
     */
    function getTimeRemainingText(dueDate) {
        const now = new Date();
        const diffMs = dueDate - now;

        if (diffMs < 0) {
            // Overdue
            const absDiffMs = Math.abs(diffMs);
            const hours = Math.floor(absDiffMs / (1000 * 60 * 60));
            const days = Math.floor(absDiffMs / (1000 * 60 * 60 * 24));

            if (days > 0) {
                return `Overdue by ${days} day${days > 1 ? 's' : ''}`;
            } else if (hours > 0) {
                return `Overdue by ${hours} hour${hours > 1 ? 's' : ''}`;
            } else {
                return 'Overdue';
            }
        } else if (diffMs === 0) {
            return 'Due now!';
        } else {
            // Due in future
            const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

            if (days > 0) {
                if (days === 1 && hours === 0) {
                    return 'Due tomorrow';
                } else if (days === 1) {
                    return `Due tomorrow (${hours}h remaining)`;
                } else {
                    return `Due in ${days} days`;
                }
            } else if (hours > 0) {
                return `Due in ${hours} hour${hours > 1 ? 's' : ''}`;
            } else {
                const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                return `Due in ${minutes} minute${minutes > 1 ? 's' : ''}`;
            }
        }
    }

    /**
     * Update the time remaining display
     */
    function updateTimeRemaining() {
        if (timeRemaining) {
            timeRemaining.textContent = getTimeRemainingText(DUE_DATE);
        }
    }

    /**
     * Handle checkbox toggle
     */
    if (checkbox) {
        checkbox.addEventListener('change', (e) => {
            const isChecked = e.target.checked;

            if (isChecked) {
                todoCard.classList.add('completed');
                if (statusBadge) {
                    statusBadge.textContent = 'Done';
                    statusBadge.setAttribute('aria-label', 'Status: Done');
                }
            } else {
                todoCard.classList.remove('completed');
                if (statusBadge) {
                    statusBadge.textContent = 'Pending';
                    statusBadge.setAttribute('aria-label', 'Status: Pending');
                }
            }
        });
    }

    /**
     * Handle edit button
     */
    if (editBtn) {
        editBtn.addEventListener('click', () => {
            console.log('✏️ Edit clicked');
            alert('Edit functionality would open a modal or edit form.');
        });
    }

    /**
     * Handle delete button
     */
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            console.log('🗑️ Delete clicked');
            const confirmed = confirm('Are you sure you want to delete this task?');
            if (confirmed) {
                console.log('Task deleted');
                alert('Task has been deleted.');
                // In a real app: todoCard.remove() or API call
            }
        });
    }

    // Initial update
    updateTimeRemaining();

    // Update time remaining every 60 seconds
    setInterval(updateTimeRemaining, 60000);
});
