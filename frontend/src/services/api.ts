// Frontend API wrapper
const API_URL = "http://localhost:8000/api/v1";

export async function checkHealth() {
    const res = await fetch(`${API_URL}/health`);
    return res.json();
}
