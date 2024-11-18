async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
    });

    const data = await response.json();
    alert(data.message);
}

async function sendEmails() {
    const emailData = {
        email: "youremail@gmail.com",
        password: "yourpassword",
        emails: [
            { to: "example@gmail.com", subject: "Test", body: "Hello!" },
        ],
    };

    const response = await fetch('http://127.0.0.1:5000/send-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData),
    });

    const data = await response.json();
    alert(data.message);
}

async function scheduleEmails() {
    const emailData = {
        email: "youremail@gmail.com",
        password: "yourpassword",
        emails: [
            { to: "example@gmail.com", subject: "Test", body: "Hello!" },
        ],
        interval: 10,
    };

    const response = await fetch('http://127.0.0.1:5000/schedule-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData),
    });

    const data = await response.json();
    alert(data.message);
}
