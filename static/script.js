let mediaRecorder;
let audioChunks = [];

const recordBtn = document.getElementById("recordBtn");
const sendBtn = document.getElementById("sendBtn");
const recordStatus = document.getElementById("recordStatus");
const userPlayback = document.getElementById("userPlayback");
const responseAudio = document.getElementById("responseAudio");

recordBtn.addEventListener("click", async () => {
  try {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      recordBtn.textContent = "🎤 Start Recording";
      recordStatus.textContent = "Recording stopped";
      return;
    }

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

      // Playback for recorded user audio
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

    mediaRecorder.start();
    recordBtn.textContent = "⏹️ Stop Recording";
    recordStatus.textContent = "Recording...";
  } catch (error) {
    console.error("🎤 Microphone access denied or failed:", error);
    alert("Unable to access microphone. Please allow microphone permissions.");
  }
});
