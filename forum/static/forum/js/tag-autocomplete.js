// JavaScript for tag autocomplete functionality

document.addEventListener('DOMContentLoaded', function() {
    // Find all tag input fields
    const tagInputs = document.querySelectorAll('.tag-input');

    // Process each tag input field
    tagInputs.forEach(function(input) {
        // Create a container for the autocomplete dropdown
        const autocompleteContainer = document.createElement('div');
        autocompleteContainer.className = 'autocomplete-container';
        autocompleteContainer.style.display = 'none';
        autocompleteContainer.style.position = 'absolute';
        autocompleteContainer.style.border = '1px solid #ddd';
        autocompleteContainer.style.maxHeight = '200px';
        autocompleteContainer.style.overflowY = 'auto';
        autocompleteContainer.style.backgroundColor = 'white';
        autocompleteContainer.style.zIndex = '1000';
        autocompleteContainer.style.width = input.offsetWidth + 'px';

        // Insert the container after the input
        input.parentNode.insertBefore(autocompleteContainer, input.nextSibling);

        // Add event listener for input changes
        input.addEventListener('input', debounce(function() {
            const currentValue = input.value;
            const lastTag = getCurrentTag(currentValue, input.selectionStart);

            if (lastTag.trim().length > 0) {
                // Fetch matching tags from the server
                fetchMatchingTags(lastTag.trim())
                    .then(tags => {
                        displayAutocompleteSuggestions(tags, autocompleteContainer, input, lastTag, currentValue);
                    });
            } else {
                // Hide the autocomplete container if there's no input
                autocompleteContainer.style.display = 'none';
            }
        }, 300));

        // Hide autocomplete when clicking outside
        document.addEventListener('click', function(e) {
            if (e.target !== input && e.target !== autocompleteContainer) {
                autocompleteContainer.style.display = 'none';
            }
        });
    });
});

// Helper function to get the current tag being typed
function getCurrentTag(value, cursorPosition) {
    // Find the last comma before the cursor position
    const lastCommaIndex = value.lastIndexOf(',', cursorPosition - 1);

    // Extract the text between the last comma and the cursor
    return value.substring(lastCommaIndex + 1, cursorPosition);
}

// Helper function to fetch matching tags from the server
function fetchMatchingTags(query) {
    return new Promise((resolve, reject) => {
        // Make an AJAX request to the tag suggestions endpoint
        fetch(`/tags/suggestions/?query=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                resolve(data.tags);
            })
            .catch(error => {
                console.error('Error fetching tag suggestions:', error);
                // Return an empty array in case of error
                resolve([]);
            });
    });
}

// Helper function to display autocomplete suggestions
function displayAutocompleteSuggestions(tags, container, input, currentTag, fullValue) {
    // Clear previous suggestions
    container.innerHTML = '';

    if (tags.length === 0) {
        container.style.display = 'none';
        return;
    }

    // Create and append suggestion elements
    tags.forEach(tag => {
        const suggestion = document.createElement('div');
        suggestion.className = 'autocomplete-suggestion';
        suggestion.textContent = tag;
        suggestion.style.padding = '8px';
        suggestion.style.cursor = 'pointer';

        // Highlight on hover
        suggestion.addEventListener('mouseover', function() {
            this.style.backgroundColor = '#f0f0f0';
        });

        suggestion.addEventListener('mouseout', function() {
            this.style.backgroundColor = 'transparent';
        });

        // Handle click on suggestion
        suggestion.addEventListener('click', function() {
            // Replace the current tag with the selected one
            const lastCommaIndex = fullValue.lastIndexOf(',', input.selectionStart - 1);
            const start = lastCommaIndex === -1 ? 0 : lastCommaIndex + 1;
            const beforeTag = fullValue.substring(0, start);
            const afterTag = fullValue.substring(input.selectionStart);

            // Add the selected tag
            let newValue;
            if (start === 0 && fullValue.trim() === currentTag.trim()) {
                // If this is the only tag, don't add a comma
                newValue = tag;
            } else {
                // Add the tag with appropriate spacing
                newValue = beforeTag + (start === 0 ? '' : ' ') + tag + ', ' + afterTag;
            }

            input.value = newValue;

            // Hide the suggestions
            container.style.display = 'none';

            // Focus back on the input
            input.focus();
        });

        container.appendChild(suggestion);
    });

    // Position and show the container
    container.style.top = (input.offsetTop + input.offsetHeight) + 'px';
    container.style.left = input.offsetLeft + 'px';
    container.style.display = 'block';
}

// Debounce function to limit how often the input event handler is called
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}
