const machineCards = document.getElementById("machine-cards");
const machineSelect = document.getElementById("machine-select");
const fleetPill = document.getElementById("fleet-pill");
const connectionLabel = document.getElementById("connection-label");
const connectionDot = document.getElementById("connection-dot");
const selectedMachineStatus = document.getElementById("selected-machine-status");
const canvas = document.getElementById("trend-chart");
const ctx = canvas.getContext("2d");

let selectedMachine = "";

function formatTime(isoTimestamp) {
  return new Date(isoTimestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function statusForReading(reading) {
  if (!reading) return { label: "No data", className: "status-warning" };
  if (reading.vibration > 3.5 || reading.acoustic > 72 || reading.power_draw > 18) {
    return { label: "Warning", className: "status-warning" };
  }
  return { label: "OK", className: "status-ok" };
}

function setConnectionState(isHealthy) {
  connectionLabel.textContent = isHealthy ? "Live" : "Disconnected";
  connectionDot.className = `status-dot ${isHealthy ? "status-live" : "status-error"}`;
}

function renderMachineCards(readings) {
  fleetPill.textContent = `${readings.length} machines`;

  if (!readings.length) {
    machineCards.innerHTML = '<div class="empty-state">Waiting for simulator data...</div>';
    return;
  }

  machineCards.innerHTML = readings
    .map((reading) => {
      const status = statusForReading(reading);
      return `
        <article class="machine-card">
          <div class="machine-topline">
            <h3>${reading.machine_id}</h3>
            <span class="machine-status ${status.className}">${status.label}</span>
          </div>
          <div class="metric-row">
            <div class="metric">
              <span class="metric-label">Vibration</span>
              <strong class="metric-value">${reading.vibration.toFixed(1)} mm/s</strong>
            </div>
            <div class="metric">
              <span class="metric-label">Acoustic</span>
              <strong class="metric-value">${reading.acoustic.toFixed(1)} dB</strong>
            </div>
            <div class="metric">
              <span class="metric-label">Power Draw</span>
              <strong class="metric-value">${reading.power_draw.toFixed(1)} kW</strong>
            </div>
          </div>
          <p class="machine-timestamp">Updated ${formatTime(reading.timestamp)}</p>
        </article>
      `;
    })
    .join("");
}

function renderMachineOptions(readings) {
  const ids = readings.map((reading) => reading.machine_id);

  if (!selectedMachine && ids.length) {
    selectedMachine = ids[0];
  }
  if (selectedMachine && !ids.includes(selectedMachine)) {
    selectedMachine = ids[0] || "";
  }

  machineSelect.innerHTML = ids
    .map((machineId) => {
      const selected = machineId === selectedMachine ? "selected" : "";
      return `<option value="${machineId}" ${selected}>${machineId}</option>`;
    })
    .join("");

  const currentReading = readings.find((item) => item.machine_id === selectedMachine);
  const status = statusForReading(currentReading);
  selectedMachineStatus.textContent = status.label;
  selectedMachineStatus.className = `pill ${status.className}`;
}

function drawChart(readings) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!readings.length) {
    ctx.fillStyle = "#5e6a73";
    ctx.font = "16px Segoe UI";
    ctx.fillText("No readings yet for this machine.", 24, 40);
    return;
  }

  const ordered = [...readings].reverse();
  const values = ordered.map((reading) => reading.vibration);
  const minValue = Math.min(...values) - 2;
  const maxValue = Math.max(...values) + 2;
  const chartLeft = 48;
  const chartRight = canvas.width - 24;
  const chartTop = 24;
  const chartBottom = canvas.height - 38;

  ctx.strokeStyle = "rgba(31, 41, 51, 0.18)";
  ctx.lineWidth = 1;
  for (let i = 0; i < 4; i += 1) {
    const y = chartTop + ((chartBottom - chartTop) / 3) * i;
    ctx.beginPath();
    ctx.moveTo(chartLeft, y);
    ctx.lineTo(chartRight, y);
    ctx.stroke();
  }

  ctx.strokeStyle = "#0d6b68";
  ctx.lineWidth = 3;
  ctx.beginPath();

  ordered.forEach((reading, index) => {
    const x =
      chartLeft + ((chartRight - chartLeft) / Math.max(ordered.length - 1, 1)) * index;
    const y =
      chartBottom -
      ((reading.vibration - minValue) / Math.max(maxValue - minValue, 1)) *
        (chartBottom - chartTop);

    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });

  ctx.stroke();

  ordered.forEach((reading, index) => {
    const x =
      chartLeft + ((chartRight - chartLeft) / Math.max(ordered.length - 1, 1)) * index;
    const y =
      chartBottom -
      ((reading.vibration - minValue) / Math.max(maxValue - minValue, 1)) *
        (chartBottom - chartTop);

    ctx.fillStyle = "#0d6b68";
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  });

  ctx.fillStyle = "#5e6a73";
  ctx.font = "12px Segoe UI";
  ctx.fillText(`${maxValue.toFixed(1)} mm/s`, 8, chartTop + 4);
  ctx.fillText(`${minValue.toFixed(1)} mm/s`, 8, chartBottom);
  ctx.fillText(formatTime(ordered[0].timestamp), chartLeft, canvas.height - 12);
  ctx.fillText(formatTime(ordered[ordered.length - 1].timestamp), chartRight - 54, canvas.height - 12);
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`);
  }
  return response.json();
}

async function refreshDashboard() {
  try {
    const latest = await fetchJson("/latest");

    setConnectionState(true);
    renderMachineCards(latest);
    renderMachineOptions(latest);

    if (selectedMachine) {
      const readings = await fetchJson(`/readings?machine_id=${encodeURIComponent(selectedMachine)}&limit=20`);
      drawChart(readings);
    } else {
      drawChart([]);
    }
  } catch (error) {
    console.error(error);
    setConnectionState(false);
  }
}

machineSelect.addEventListener("change", (event) => {
  selectedMachine = event.target.value;
  refreshDashboard();
});

refreshDashboard();
setInterval(refreshDashboard, 3000);
