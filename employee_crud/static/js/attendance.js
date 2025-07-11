document.addEventListener('DOMContentLoaded', () => {

    const scanButton = document.getElementById('scan-btn');

    if (scanButton) {
        scanButton.addEventListener('click', () => {
            const employeeId = document.getElementById('employee_id').value;

            if (!employeeId) {
                alert("Please enter or scan Employee ID");
                return;
            }

            fetch('/attendance/mark', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ employee_id: employeeId })
            })
            .then(response => response.json())
            .then(data => {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = `<strong>${data.status}</strong> at ${data.time}`;
                statusDiv.style.display = "block";
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

});
