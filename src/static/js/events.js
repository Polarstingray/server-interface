import { apiPost, apiGet } from './api.js';

async function createVm() {
    const payload = {
        name: getVal("create_input1"),
        memory: getVal("create_input2"),
        vcpus: getVal("create_input3"),
        os: getVal("create_input4"),
        network: getVal("create_input5"),
        disk_path: getVal("create_input6"),
        iso: getVal("create_input7")
    };

    // Basic validation
    if (!payload.name) return showError("create_output", "VM name required");
    if (isNaN(payload.memory) || isNaN(payload.vcpus))
        return showError("create_output", "Memory and vCPUs must be numbers");

    try {
        const data = await apiPost("/vm/create", payload);

        showJson("create_output", data);
        await loadVms();
    } catch (err) {
        showError("create_output", err);
    }
}

function getVal(id) {
    return document.getElementById(id).value.trim();
}

function showJson(id, data) {
    document.getElementById(id).textContent = JSON.stringify(data, null, 2);
}

function showError(id, err) {
    document.getElementById(id).textContent = `${err}`;
}

async function loadVms() {
    const vmList = document.getElementById("vm-list");
    vmList.innerHTML = "";

    try {
    const data = await apiGet("/vm/list");
    
    Object.keys(data).forEach(vmName => {
        const li = document.createElement("li");
        li.id = vmName;
        li.innerHTML = `
        <p>${vmName}</p>
        <button data-name="${vmName}" class="start">Start</button>
        <button data-name="${vmName}" class="stop">Stop</button>
        <button data-name="${vmName}" class="reboot">Reboot</button>
        <pre id="${vmName}_state">${data[vmName].state}</pre>
        `;
        vmList.appendChild(li);
    });
    } catch (err) {
        return showError("vm-list", err);
    }
}

document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("start")) {
        await handleVmAction(e.target.dataset.name, "start");
    } else if (e.target.classList.contains("stop")) {
        await handleVmAction(e.target.dataset.name, "stop");
    } else if (e.target.classList.contains("reboot")) {
        await handleVmAction(e.target.dataset.name, "reboot")
    } else if (e.target.classList.contains("create_vm")) {
        e.preventDefault();
        await createVm();
    }
});

async function handleVmAction(name, action) {
    try {
        await apiPost(`/vm/${encodeURIComponent(name)}/${action}`);
        await updateState(name);
    } catch (err) {
        showError(`${name}_state`, err);
    }
}

async function updateState(name) {
    try {
        const data = await apiGet(`/vm/${encodeURIComponent(name)}/state`);
        // showJson(`${name}_state`, data);
        document.getElementById(`${name}_state`).innerText = data;
    } catch (err) {
        showError(`${name}_state`, err);
    }
}

window.addEventListener("load", loadVms);