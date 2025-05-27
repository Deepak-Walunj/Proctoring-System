// import React, { useState, useEffect, useRef } from "react";
// import axios from "axios";
// import { toast } from "react-toastify";
// import VideoCameraFrontIcon from "@mui/icons-material/VideoCameraFront";
// import Backdrop from "@mui/material/Backdrop";
// import CircularProgress from "@mui/material/CircularProgress";
// import Typography from "@mui/material/Typography"; // Import Typography for text styling

// const URL = import.meta.env.VITE_PORT_URL;
// const WS_URL = "ws://localhost:8000/ws/proctoring/";

// const VideoAnalysis = ({ endviva, username, vivaID, vivaHandler }) => {
// const videoRef = useRef(null);
// const canvasRef = useRef(null);
// const [mediaRecorder, setMediaRecorder] = useState(null);
// const [recordedChunks, setRecordedChunks] = useState([]);
// const [signalingSocket, setSignalingSocket] = useState(null);
// const [frameInterval, setFrameInterval] = useState(null);
// const [currentInstruction, setCurrentInstruction] = useState(null);
// const [prevInstruction, setPrevInstruction] = useState(null);
// const [uploading, setUploading] = useState(false); // State to control the backdrop
// const [verificationResult, setVerificationResult] = useState(null);

// useEffect(() => {
// if (!endviva) {
//     startVideoAndRecording();
// } else {
//     stopRecordingAndCleanup();
// }
// return () => {
//     if (endviva) {
//         stopRecordingAndCleanup();
//     };
//     }
// }, [endviva]);

// const startVideoAndRecording = async () => {
// try {
//     const stream = await navigator.mediaDevices.getUserMedia({
//     video: { facingMode: "user", width: 800, height: 400 },
//     audio: true,
//     });

//     videoRef.current.srcObject = stream;

//     const chunks = [];
//     const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });
//     recorder.ondataavailable = (event) => {
//     if (event.data.size > 0) {
//         chunks.push(event.data);
//     }
//     };

//     recorder.onstop = async () => {
//     setRecordedChunks(chunks);
//     console.log("Recording complete, chunks:", chunks);
//     await uploadRecordedVideo(chunks);
//     };

//     setMediaRecorder(recorder);
//     recorder.start();

//     initWebSocket(stream);
//     toast.success("Recording and streaming started!");
//     console.log("Recording and streaming started!");
// } catch (error) {
//     console.error("Error accessing camera:", error);
//     toast.error("Failed to start camera or recording.");
// }
// };

// const stopRecordingAndCleanup = () => {
// if (mediaRecorder && mediaRecorder.state === "recording") {
//     mediaRecorder.stop();
//     toast.info("Recording stopped.");
// }
// if (videoRef.current?.srcObject) {
//     console.log("Stopping video stream...");
//     const tracks = videoRef.current.srcObject.getTracks();
//     tracks.forEach((track) => track.stop());
//     videoRef.current.srcObject = null;
// }
// if (signalingSocket) {
//     signalingSocket.close();
//     setSignalingSocket(null);
// }
// if (frameInterval) {
//     clearInterval(frameInterval);
//     setFrameInterval(null);
// }
// setRecordedChunks([]);
// };
// const initWebSocket = (stream) => {
// const socket = new WebSocket(WS_URL);
// setSignalingSocket(socket);
// if (signalingSocket) {
//     console.log("Closing WebSocket connection...");
//     signalingSocket.close();
//     setSignalingSocket(null);
//     }

// socket.onopen = () => {
//     console.log("Connected to signaling server");
//     captureAndSendFrames(stream, socket);
// };

// socket.onmessage = (message) => {
//     console.log("Raw message:", message.data);
//     try {
//         const data = JSON.parse(message.data);
//         if (data.type === "instruction") {
//             setCurrentInstruction(data.message);
//         }
//         else if (data.type === "verification") {
//             console.log("Verification Results:", data.verificationResults);
//             toast.info(data.verifyToast); 
//             setVerificationResult(data);
//         }
//     } 
//     catch (error) {
//         console.error("Error parsing message:", error);
//     }
// };

// socket.onerror = (error) => {
//     console.error("Signaling server error:", error);
// };

// socket.onclose = () => {
//     console.log("Disconnected from signaling server");
//     if (verificationResult) {
//         console.log("Final Verification Result:", verificationResult);
//     }
// };
// };

// useEffect(() => {
// console.log("Current Instruction:", currentInstruction);
// console.log("Previous Instruction:", prevInstruction);
// if (
//     currentInstruction &&
//     (prevInstruction === null || currentInstruction !== prevInstruction)
// ) {
//     setPrevInstruction(currentInstruction);
// }
// }, [currentInstruction, prevInstruction]);

// const captureAndSendFrames = (stream, socket) => {
// const canvas = document.createElement("canvas");
// const ctx = canvas.getContext("2d");
// const video = videoRef.current;

// const captureFrame = () => {
//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
//     const frameData = canvas.toDataURL("image/jpeg");
//     console.log("Sending frame:", frameData.substring(0, 100));
//     console.log(`Sending username: ${username}`);
//     if (socket.readyState === WebSocket.OPEN) {
//     socket.send(JSON.stringify({ type: "frame", frame: frameData , name: username}));
//     }
// };

// const interval = setInterval(captureFrame, 1000);
// setFrameInterval(interval);
// };

// const uploadRecordedVideo = async (chunks) => {
// if (!chunks || chunks.length === 0) {
//     console.error("No chunks available for upload.");
//     return;
// }

// const blob = new Blob(chunks, { type: "video/webm" });
// console.log("Blob size:", blob.size);
// console.log("Blob type:", blob.type);

// const formData = new FormData();
// formData.append("video", blob, "recording.mp4");
// formData.append("username", username);
// formData.append("vivaID", vivaID);

// let token = "";

// try {
//     const response = await axios.get(`${URL}/get-csrf-token`);
//     token = response.data.csrfToken;
//     console.log("CSRF token fetched:", token);
// } catch (error) {
//     console.error("Error fetching CSRF token:", error);
// }

// try {
//     setUploading(true); // Show the backdrop
//     const response = await axios.post(
//     `${URL}/candidate/upload_video/`,
//     formData,
//     {
//         headers: {
//         "X-CSRFToken": token,
//         },
//     }
//     );

//     if (response.status === 200) {
//     toast.success("Video uploaded successfully!");
//     console.log("Video uploaded successfully!");
//     } else {
//     toast.error("Failed to upload video.");
//     console.error("Upload failed:", response);
//     }
// } catch (error) {
//     toast.error("Error uploading video.");
//     console.error("Error:", error);
// } finally {
//     setUploading(false); // Hide the backdrop
//     // window.location.reload();
// }
// };



// return (
// <div className="bg-white shadow-md border rounded-md w-full h-full p-2 border-black relative">
//     {/* Backdrop for Uploading */}
//     <Backdrop
//     sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
//     open={uploading}
//     onClick={() => {}}
//     >
//     <div style={{ textAlign: "center" }}>
//         <CircularProgress color="inherit" />
//         <Typography variant="body1" sx={{ mt: 2 }}>
//         Do not reload the screen. Processing of uploading video.
//         </Typography>
//     </div>
//     </Backdrop>

//     <div className="relative w-full h-full">
//     <p className="absolute top-0 left-1/2 transform -translate-x-1/2 text-xs sm:text-xs md:text-xl lg:text-xl font-semibold text-center text-black bg-gray-100 p-1 rounded-md z-10">
//         {currentInstruction}
//     </p>
//     {verificationResult && (
//     <div className="absolute top-16 left-1/2 transform -translate-x-1/2 bg-red-500 text-white p-2 rounded-md shadow-md z-20">
//         <p>{verificationResult.message}</p>
//     </div>
//     )}
//     {/* Video Element */}
//     <video ref={videoRef} autoPlay muted className="w-full h-full object-fill" />
//     <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-full object-fill" />
//     <VideoCameraFrontIcon
//         className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2"
//         style={{ fontSize: "3rem", color: "black" }}
//     />
//     </div>

//     {/* End Viva Button */}
//     <button
//         className="absolute bottom-4 right-4 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
//         onClick={() => {
//             stopRecordingAndCleanup();
//             vivaHandler();
//         }}
//     >
//         End Viva
//     </button>

// </div>
// );
// };

// export default VideoAnalysis;
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

export default function VideoAnalysis(){
    const { name } = useParams();
    const [image, setImage] = useState(localStorage.getItem("studentImage") || null);
    const [message, setMessage] = useState("");
    const [isMounted, setIsMounted] = useState(true);
    const navigate = useNavigate()

    useEffect(() => {
        if(!localStorage.getItem("studentImage")){
        const fetchImage = async()=>{
            try{
                const response=await axios.get(`http://localhost:8000/api/fetch-image/${encodeURIComponent(name)}`)
                if (response.data.success && response.data.base64) {
                    localStorage.setItem("studentImage", response.data.base64)
                    toast.success("✅ Image fetched successfully!")
                    setImage(response.data.base64);
                    setMessage("✅ Image fetched successfully!");
                    
                } else {
                    toast.error(`❌ ${response.data.message}`)
                    setImage(null)
                    setMessage(`❌ ${response.data.message}`);
                    navigate("/InputDetails")
                }
            }
            catch(error){
                toast.error(error.message)
                setMessage(error)
                navigate("/InputDetails")
            }
        }
        fetchImage()
    }else{
        toast.info("✅ Image loaded from cache.");
        setMessage("✅ Image loaded from cache.");
    }
    },[name, navigate])

    const handleEndViva = () => {
        toast.success("Viva ended successfully")
        setMessage("Viva ended successfully")
        setIsMounted(false);
        localStorage.clear()
        navigate("/InputDetails")
    };

    if (!isMounted) return null;

    return(
        <div style={{ padding: "2rem" }}>
            <h2>Welcome, {name}</h2>
            <p>{message}</p>
            {image && (
                <img
                    src={`data:image/png;base64,${image}`}
                    alt="Registered face"
                    style={{ width: "200px", height: "200px", borderRadius: "8px", marginBottom: "20px" }}
                />
            )}
            <button onClick={handleEndViva} style={{ padding: "10px 20px", marginTop: "10px" }}>
                End Viva
            </button>
        </div>
    )
}