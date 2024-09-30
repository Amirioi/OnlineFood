document.addEventListener("DOMContentLoaded", function () {
    const orderElements = document.querySelectorAll(".order");
    orderElements.forEach(orderElement => {
        const orderId = orderElement.dataset.orderId;
        const changeStatusBtn = orderElement.querySelector(".change-status-btn");
        changeStatusBtn.addEventListener("click", function () {
            changeOrderStatus(orderId);
        });
    });

    function changeOrderStatus(orderId) {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/restaurant/mark_as_delivering/", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    window.location.reload()
                } else {
                    console.error("Failed to update order status");
                }
            }
        };
        xhr.send(JSON.stringify({order_id: orderId}));
    }
});


function refreshPage() {
    location.reload();
}

setTimeout(refreshPage, 120000);