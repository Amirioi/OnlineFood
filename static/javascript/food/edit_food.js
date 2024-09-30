document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('delete_button').addEventListener('click', function () {
        fetch('/delete-food/', {
            method: 'POST',
            body: document.location,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.href = '/profile/'; // Redirect to the checkout page
                } else {
                    console.error('Error:', data.message);
                    alert('Error: ' + data.message); // Display error message
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while submitting the order.');
            });
    });
});
