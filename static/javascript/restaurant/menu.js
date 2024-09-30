document.addEventListener("DOMContentLoaded", function () {
    const foodForm = document.getElementById('foodForm');

    foodForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const quantityInputs = document.querySelectorAll('input[type="number"]');
        const selectedFoods = [];
        quantityInputs.forEach(function (input) {
            const foodID = input.id;
            const quantity = parseInt(input.value);
            if (quantity >= 0) {
                selectedFoods.push({id: foodID, quantity: quantity});
            }
        });

        const formData = new FormData();
        formData.append('restaurant_id', document.getElementById('restaurantId').value);
        selectedFoods.forEach(food => {
            formData.append(`food_${food.id}`, food.quantity);
        });

        fetch('/submit-food-order/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = '/checkout/'; // Redirect to the checkout page
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
