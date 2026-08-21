const API_BASE_URL = "http://127.0.0.1:8000";

async function apiRequest(endpoint, options = {}) {

    try {

        const response = await fetch(
            `${API_BASE_URL}${endpoint}`,
            {
                ...options,
                credentials: "include"
            }
        );

        const text = await response.text();

        let data = null;

        try {
            data = text ? JSON.parse(text) : null;
        } catch {
            data = text;
        }

        console.log("API:", endpoint);
        console.log("Status:", response.status);
        console.log("Response:", data);

        if (!response.ok) {

            if (data && typeof data === "object" && data.detail) {

                if (Array.isArray(data.detail)) {

                    const messages = data.detail.map(item =>
                        item.msg || JSON.stringify(item)
                    );

                    throw new Error(messages.join(", "));
                }

                throw new Error(String(data.detail));
            }

            throw new Error(
                `Request failed: ${response.status}`
            );
        }

        return data;

    } catch (error) {

        console.error("API Request Error:", error);

        throw error;
    }
}

