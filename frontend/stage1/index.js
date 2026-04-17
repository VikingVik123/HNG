/* ============================================
   TODO CARD - INTERACTIVE BEHAVIOR
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    const todoCard = document.querySelector('[data-testid="test-todo-card"]');
    const checkbox = document.querySelector('[data-testid="test-todo-complete-toggle"]');
    const editBtn = document.querySelector('[data-testid="test-todo-edit-button"]');
    const deleteBtn = document.querySelector('[data-testid="test-todo-delete-button"]');
    const statusControl = document.querySelector('[data-testid="test-todo-status-control"]');
    const statusBadge = document.querySelector('[data-testid="test-todo-status"]');
    const timeRemaining = document.querySelector('[data-testid="test-todo-time-remaining"]');
    const overdueIndicator = document.querySelector('[data-testid="test-todo-overdue-indicator"]');
    const priorityBadge = document.querySelector('[data-testid="test-todo-priority"]');
    const titleElement = document.querySelector('[data-testid="test-todo-title"]');
    const descriptionElement = document.querySelector('[data-testid="test-todo-description"]');
    const expandToggle = document.querySelector('[data-testid="test-todo-expand-toggle"]');
    const descriptionSection = document.querySelector('.description-section');
    const collapsibleSection = document.querySelector('[data-testid="test-todo-collapsible-section"]');
    
    const editForm = document.querySelector('[data-testid="test-todo-edit-form"]');
    const editTitle = document.querySelector('[data-testid="test-todo-edit-title-input"]');
    const editDescription = document.querySelector('[data-testid="test-todo-edit-description-input"]');
    const editPriority = document.querySelector('[data-testid="test-todo-edit-priority-select"]');
    const editDueDate = document.querySelector('[data-testid="test-todo-edit-due-date-input"]');
    const saveBtn = document.querySelector('[data-testid="test-todo-save-button"]');
    const cancelBtn = document.querySelector('[data-testid="test-todo-cancel-button"]');

    // Fixed due date: March 1, 2026, 18:00 UTC
    let DUE_DATE = new Date('2026-03-01T18:00:00Z');
    let currentStatus = 'Pending';
    let currentPriority = 'High';
    let isEditMode = false;
    let updateInterval;

    /**
     * Calculate readable time remaining text with granular details
     * @param {Date} dueDate - The due date
     * @returns {object} - Object with text and isOverdue flag
     */
    function getTimeRemainingText(dueDate) {
        const now = new Date();
        const diffMs = dueDate - now;

        if (diffMs < 0) {
            // Overdue
            const absDiffMs = Math.abs(diffMs);
            const days = Math.floor(absDiffMs / (1000 * 60 * 60 * 24));
            const hours = Math.floor((absDiffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((absDiffMs % (1000 * 60 * 60)) / (1000 * 60));

            let text = 'Overdue';
            if (days > 0) {
                text = `Overdue by ${days} day${days > 1 ? 's' : ''}`;
            } else if (hours > 0) {
                text = `Overdue by ${hours} hour${hours > 1 ? 's' : ''}`;
            } else if (minutes > 0) {
                text = `Overdue by ${minutes} minute${minutes > 1 ? 's' : ''}`;
            }

            return { text, isOverdue: true };
        } else if (diffMs === 0) {
            return { text: 'Due now!', isOverdue: false };
        } else {
            // Due in future
            const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

            let text;
            if (days > 0) {
                if (days === 1 && hours === 0) {
                    text = 'Due tomorrow';
                } else if (days === 1) {
                    text = `Due tomorrow (${hours}h remaining)`;
                } else {
                    text = `Due in ${days} day${days > 1 ? 's' : ''}`;
                }
            } else if (hours > 0) {
                text = `Due in ${hours} hour${hours > 1 ? 's' : ''}`;
            } else {
                text = `Due in ${minutes} minute${minutes > 1 ? 's' : ''}`;
            }

            return { text, isOverdue: false };
        }
    }

    /**
     * Update the time remaining display
     */
    function updateTimeRemaining() {
        if (currentStatus === 'Done') {
            if (timeRemaining) {
                timeRemaining.textContent = 'Completed';
            }
            if (overdueIndicator) {
                overdueIndicator.style.display = 'none';
            }
            return;
        }

        const timeInfo = getTimeRemainingText(DUE_DATE);
        
        if (timeRemaining) {
            timeRemaining.textContent = timeInfo.text;
        }

        // Handle overdue state
        if (timeInfo.isOverdue) {
            todoCard.classList.add('overdue');
            if (overdueIndicator) {
                overdueIndicator.style.display = 'inline-block';
            }
        } else {
            todoCard.classList.remove('overdue');
            if (overdueIndicator) {
                overdueIndicator.style.display = 'none';
            }
        }
    }

    /**
     * Update visual state based on priority
     */
    function updatePriorityVisuals() {
        todoCard.classList.remove('priority-high', 'priority-medium', 'priority-low');
        todoCard.classList.add(`priority-${currentPriority.toLowerCase()}`);
    }

    /**
     * Update visual state based on status
     */
    function updateStatusVisuals() {
        todoCard.classList.remove('in-progress', 'completed');
        
        if (currentStatus === 'Done') {
            todoCard.classList.add('completed');
        } else if (currentStatus === 'In Progress') {
            todoCard.classList.add('in-progress');
        }

        statusBadge.textContent = currentStatus;
        statusBadge.setAttribute('aria-label', `Status: ${currentStatus}`);
        statusControl.value = currentStatus;

        // Update time remaining display
        updateTimeRemaining();
    }

    /**
     * Handle checkbox toggle
     */
    if (checkbox) {
        checkbox.addEventListener('change', (e) => {
            const isChecked = e.target.checked;

            if (isChecked) {
                currentStatus = 'Done';
            } else {
                currentStatus = 'Pending';
            }

            updateStatusVisuals();
        });
    }

    /**
     * Handle status control changes
     */
    if (statusControl) {
        statusControl.addEventListener('change', (e) => {
            currentStatus = e.target.value;
            
            // Sync checkbox with status
            if (currentStatus === 'Done') {
                checkbox.checked = true;
            } else {
                checkbox.checked = false;
            }

            updateStatusVisuals();
        });
    }

    /**
     * Check if description is long enough to collapse
     */
    function checkDescriptionLength() {
        const lineHeight = parseInt(window.getComputedStyle(descriptionElement).lineHeight);
        const scrollHeight = descriptionElement.scrollHeight;
        const maxHeight = lineHeight * 3; // 3 lines default

        if (scrollHeight > maxHeight) {
            descriptionSection.classList.add('collapsed');
            expandToggle.style.display = 'block';
        } else {
            descriptionSection.classList.remove('collapsed');
            expandToggle.style.display = 'none';
        }
    }

    /**
     * Handle expand/collapse toggle
     */
    if (expandToggle) {
        expandToggle.addEventListener('click', () => {
            const isExpanded = expandToggle.getAttribute('aria-expanded') === 'true';
            
            if (isExpanded) {
                descriptionSection.classList.add('collapsed');
                collapsibleSection.classList.remove('expanded');
                expandToggle.setAttribute('aria-expanded', 'false');
                expandToggle.querySelector('.expand-text').textContent = 'Show more';
            } else {
                descriptionSection.classList.remove('collapsed');
                collapsibleSection.classList.add('expanded');
                expandToggle.setAttribute('aria-expanded', 'true');
                expandToggle.querySelector('.expand-text').textContent = 'Show less';
            }
        });
    }

    /**
     * Enter edit mode
     */
    function enterEditMode() {
        isEditMode = true;
        todoCard.classList.add('edit-active');
        editForm.classList.add('edit-form-visible');
        
        // Set form values
        editTitle.value = titleElement.textContent;
        editDescription.value = descriptionElement.textContent;
        editPriority.value = currentPriority;
        
        // Set current due date
        const dateStr = DUE_DATE.toISOString().split('T')[0];
        editDueDate.value = dateStr;
        
        // Focus on first input
        editTitle.focus();
    }

    /**
     * Exit edit mode (cancel)
     */
    function exitEditMode() {
        isEditMode = false;
        todoCard.classList.remove('edit-active');
        editForm.classList.remove('edit-form-visible');
        
        // Return focus to edit button
        editBtn.focus();
    }

    /**
     * Save edit changes
     */
    function saveChanges(e) {
        e.preventDefault();

        // Update title
        titleElement.textContent = editTitle.value || 'Untitled Task';
        
        // Update description
        descriptionElement.textContent = editDescription.value || 'No description';
        
        // Update priority
        currentPriority = editPriority.value;
        priorityBadge.textContent = currentPriority;
        priorityBadge.setAttribute('aria-label', `${currentPriority} priority`);
        updatePriorityVisuals();
        
        // Update due date
        if (editDueDate.value) {
            DUE_DATE = new Date(editDueDate.value + 'T18:00:00Z');
            const dueElement = document.querySelector('[data-testid="test-todo-due-date"]');
            const dateObj = new Date(editDueDate.value);
            const options = { year: 'numeric', month: 'short', day: 'numeric' };
            dueElement.textContent = `Due ${dateObj.toLocaleDateString('en-US', options)}`;
            dueElement.setAttribute('datetime', DUE_DATE.toISOString());
        }
        
        // Recalculate if description needs collapsing
        checkDescriptionLength();
        
        // Update time display
        updateTimeRemaining();
        
        exitEditMode();
    }

    /**
     * Handle edit button
     */
    if (editBtn) {
        editBtn.addEventListener('click', () => {
            if (isEditMode) {
                exitEditMode();
            } else {
                enterEditMode();
            }
        });
    }

    /**
     * Handle save button
     */
    if (saveBtn) {
        saveBtn.addEventListener('click', saveChanges);
    }

    /**
     * Handle cancel button
     */
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            exitEditMode();
        });
    }

    /**
     * Handle delete button
     */
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            const confirmed = confirm('Are you sure you want to delete this task?');
            if (confirmed) {
                todoCard.style.transition = 'all 0.3s ease';
                todoCard.style.opacity = '0';
                todoCard.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    todoCard.remove();
                }, 300);
            }
        });
    }

    /**
     * Initialize card state
     */
    function initialize() {
        updatePriorityVisuals();
        updateStatusVisuals();
        checkDescriptionLength();
    }

    // Initial setup
    initialize();

    // Update time remaining every 30 seconds (as per requirements)
    updateInterval = setInterval(() => {
        updateTimeRemaining();
    }, 30000);

    // Call once initially
    updateTimeRemaining();
});

