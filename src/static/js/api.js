

async function apiPost(endpoint, data={}) {
    const res = await fetch(`/api${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    if (!res.ok) {
        return `HTTP error! status: ${res.status}`;
    }
    const resData = await res.json();
    if (!resData.status) {
        throw new Error(`${resData.message}\n${resData.error}` || "Unknown error");
    }
    return resData.data;
}

async function apiGet(endpoint) {
    const res = await fetch(`/api${endpoint}`);
    if (!res.ok) {
        return `HTTP error! status: ${res.status}`;
    }
    const resData = await res.json();
    if (!resData.status) {
        throw new Error(`${resData.message}\n${resData.error}` || "Unknown error");
    }
    return resData.data;
}


export { apiPost, apiGet };