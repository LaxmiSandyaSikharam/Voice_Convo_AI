let mediaRecorder;
let audioChunks = [];

const recordBtn = document.getElementById("recordBtn");
const sendBtn = document.getElementById("sendBtn");
const recordStatus = document.getElementById("recordStatus");
const userPlayback = document.getElementById("userPlayback");
const responseAudio = document.getElementById("responseAudio");

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

const resetBtn = document.getElementById("resetBtn");
const resetStatus = document.getElementById("resetStatus");

// === Voice Recording & Send Logic ===
recordBtn.addEventListener("click", async () => {
  try {
    // If already recording → stop
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      recordBtn.textContent = "🎤 Start Recording";
      recordStatus.textContent = "Recording stopped";
      return;
    }

    // Request mic access
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const audioUrl = URL.createObjectURL(audioBlob);

      // Show recorded audio for playback
      userPlayback.src = audioUrl;
      userPlayback.style.display = "block";

      sendBtn.disabled = false;

      sendBtn.onclick = async () => {
        sendBtn.disabled = true;

        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.webm");

        try {
          const response = await fetch("/converse", {
            method: "POST",
            body: formData,
          });

          const data = await response.json();

          if (data.audio) {
            // Force reload by bypassing browser cache
            responseAudio.pause();
            responseAudio.src = "";
            responseAudio.load();

            responseAudio.src = data.audio + "?t=" + new Date().getTime();
            responseAudio.style.display = "block";
            responseAudio.play();
          } else {
            alert("Agent did not return audio.");
          }
        } catch (err) {
          console.error("❌ Error during fetch:", err);
          alert("Failed to send audio to the server.");
        } finally {
          sendBtn.disabled = false;
        }
      };
    };

    // Start recording
    mediaRecorder.start();
    recordBtn.textContent = "⏹️ Stop Recording";
    recordStatus.textContent = "Recording...";
  } catch (error) {
    console.error("🎤 Microphone access denied or failed:", error);
    alert("Unable to access microphone. Please allow microphone permissions.");
  }
});

// === Upload RAG Docs ===
uploadBtn.addEventListener("click", async () => {
  if (!fileInput.files.length) {
    alert("Please select a CSV file before uploading.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  uploadStatus.textContent = "⏳ Uploading...";

  try {
    const response = await fetch("/upload_rag_docs", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (data.status === "success") {
      uploadStatus.textContent = `✅ File '${fileInput.files[0].name}' uploaded and indexed successfully!`;
    } else {
      uploadStatus.textContent = "❌ Upload failed: " + (data.error || "Unknown error");
    }
  } catch (err) {
    console.error("❌ Upload error:", err);
    uploadStatus.textContent = "❌ Upload failed (network error)";
  }
});

// === Reset Conversation ===
resetBtn.addEventListener("click", async () => {
  resetStatus.textContent = "⏳ Resetting...";
  try {
    const response = await fetch("/reset", { method: "POST" });
    const data = await response.json();
    if (data.status === "reset successful") {
      resetStatus.textContent = "✅ Conversation reset!";
    } else {
      resetStatus.textContent = "❌ Reset failed.";
    }
  } catch (err) {
    console.error("❌ Reset error:", err);
    resetStatus.textContent = "❌ Reset failed (network error)";
  }
});
