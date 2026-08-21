const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");


/* =========================
   REGISTER
========================= */

if (registerForm) {

    registerForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const role = document.getElementById("role").value;

        const message = document.getElementById("registerMessage");

        message.textContent = "Creating account...";

        try {

            const result = await apiRequest("/Register", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password,
                    role: role
                })
            });

            console.log("Register response:", result);

            message.textContent =
                "Account created successfully!";

            setTimeout(() => {
                window.location.href = "login.html";
            }, 1000);

        } catch (error) {

            console.error("Register error:", error);

            message.textContent =
                error.message || "Registration failed.";
        }
    });
}


/* =========================
   LOGIN
========================= */

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        const message = document.getElementById("loginMessage");

        message.textContent = "Logging in...";

        try {

            const result = await apiRequest("/login", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            console.log("Login response:", result);

            message.textContent =
                "Login successful!";

            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 700);

        } catch (error) {

            console.error("Login error:", error);

            message.textContent =
                error.message || "Login failed.";
        }
    });
}
