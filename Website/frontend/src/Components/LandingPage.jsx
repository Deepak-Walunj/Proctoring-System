import { useNavigate } from "react-router-dom";

export const LandingPage = () => {
    const navigate = useNavigate();

    const handleButton = () => {
        navigate("/InputDetails");
    };

    return (
        <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif", display:"flex", flexDirection:"column", alignItems:"center"}} >
            <h1>AI Proctoring System</h1>
            <p style={{ fontSize: "1.2rem", textAlign: "center", maxWidth: "600px" }}>
                Welcome to our AI-powered Online Proctoring System! This system uses advanced AI models like <strong>MediaPipe BlazeFace</strong> 
                for face detection, <strong>EfficientDet</strong> for object detection, and <strong>DeepFace SFace</strong> for facial verification.
            </p>

            <p>
                <strong>Features include:</strong>
            </p>
            <ul>
                <li>🎯 Accurate face detection and landmark tracking</li>
                <li>🧍‍♂️ Gaze direction analysis (Left, Right, Up, Down)</li>
                <li>📏 Real-time face-to-camera distance monitoring</li>
                <li>📸 Clean profile capture for registration</li>
                <li>🛑 Detection of cheating materials (mobile, notes, etc.)</li>
                <li>🧠 Face verification using SFace every 10 seconds</li>
            </ul>

            <p>
                Click below to begin the exam by submitting your information.
            </p>

            <button onClick={handleButton} style={{ padding: "10px 20px", fontSize: "16px" }}>
                Start Proctoring
            </button>
        </div>
    );
};
