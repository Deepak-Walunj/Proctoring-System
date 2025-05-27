import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export default function InputDetails() {
    const [name, setName] = useState("");
    const navigate = useNavigate();

    const handleStartProctoring = () => {
        if (!name.trim()) {
            toast.error("Please enter your name.");
            return;
        }
        navigate(`/video-analysis/${encodeURIComponent(name)}`);
    };

    return (
        <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
            <h3>Enter Your Details</h3>
            <p>Please provide your full name to begin the proctoring session.</p>

            <input
                type="text"
                placeholder="Enter your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{ padding: "8px", fontSize: "16px", marginRight: "10px" }}
            />

            <button
                onClick={handleStartProctoring}
                style={{ padding: "10px 20px", fontSize: "16px" }}
            >
                Start Proctoring
            </button>

            <div style={{ marginTop: "2rem" }}>
                <h4>Features Activated in This System:</h4>
                <ul>
                    <li>✅ Face alignment using eye landmarks for clean database entries</li>
                    <li>🔍 Gaze tracking for looking left/right/up/down</li>
                    <li>📏 Real-time face-to-camera distance monitoring</li>
                    <li>🧍‍♂️ Ensures only one face inside bounding box</li>
                    <li>📸 Profile image capture, crop, and save with MediaPipe</li>
                    <li>💻 Object detection to identify cheating materials</li>
                    <li>🧠 Face verification every 10s using DeepFace SFace</li>
                </ul>
            </div>
        </div>
    );
}
