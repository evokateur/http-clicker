const clickSound = document.getElementById("click-sound");
const tvStatus = document.getElementById("tv-status");

function playClick() {
  clickSound.currentTime = 0;
  clickSound.play().catch(() => {});
}

async function press(button, path, onResult) {
  playClick();
  button.disabled = true;
  try {
    const response = await fetch(path, { method: "POST" });
    const data = await response.json();
    if (onResult) onResult(data);
  } catch (err) {
    if (onResult) onResult({ status: "failed", message: "Connection error." });
  } finally {
    button.disabled = false;
  }
}

document.getElementById("tv").addEventListener("pointerdown", (e) => {
  e.preventDefault();
  press(e.currentTarget, "/tv", (data) => {
    tvStatus.textContent = data.message || " ";
  });
});

document.getElementById("ch-up").addEventListener("pointerdown", (e) => {
  e.preventDefault();
  press(e.currentTarget, "/channel-up");
});

document.getElementById("ch-down").addEventListener("pointerdown", (e) => {
  e.preventDefault();
  press(e.currentTarget, "/channel-down");
});
