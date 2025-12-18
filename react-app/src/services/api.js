
const API_BASE_URL = 'http://localhost:5000';

export const fetchLatestData = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/data/latest`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error fetching data:", error);
        return null;
    }
};

export const fetchDeviceData = async (deviceId, limit = 20) => {
    try {
        const response = await fetch(`${API_BASE_URL}/data/device/${deviceId}?limit=${limit}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        return result.data;
    } catch (error) {
        console.error(`Error fetching data for ${deviceId}:`, error);
        return [];
    }
};

export const fetchServerStats = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching stats:", error);
        return null;
    }
}
