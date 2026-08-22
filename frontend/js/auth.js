const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");


/* =========================
   REGISTER
========================= */

if (registerForm) {

    registerForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const username = document.getElementById("username").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const role = document.getElementById("role").value;

        const message = document.getElementById("registerMessage");

        message.textContent = "Creating account...";
        message.className = "message";

        try {

            console.log("Sending registration request...");

            const result = await apiRequest("/Register", {
                method: "POST",

                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    username: username,
                    password: password,
                    role: role
                })
            });

            console.log("Register response:", result);

            message.textContent = "Account created successfully!";
            message.className = "message success";

            setTimeout(() => {
                window.location.href = "login.html";
            }, 1000);

        } catch (error) {

            console.error("Register error:", error);

            message.textContent =
                error.message || "Registration failed.";

            message.className = "message error";
        }
    });
}


/* =========================
   LOGIN
========================= */

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        const message = document.getElementById("loginMessage");

        message.textContent = "Logging in...";
        message.className = "message";

        try {

            console.log("Sending login request...");

            const result = await apiRequest("/login", {
                method: "POST",

                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            console.log("Login response:", result);

            message.textContent = "Login successful!";
            message.className = "message success";

            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 700);

        } catch (error) {

            console.error("Login error:", error);

            message.textContent =
                error.message || "Login failed.";

            message.className = "message error";
        }
    });
}