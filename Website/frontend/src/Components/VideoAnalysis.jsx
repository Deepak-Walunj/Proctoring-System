import { useEffect, useRef, useState } from "react"
import { useParams } from "react-router-dom"
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

export default function VideoAnalysis(){
    const { name } = useParams();
    const [perProcessData, setPerProcessData] = useState({
        gaze_toast: "",
        distance_toast: { toast: "", distance: 0 },
        object_toast: "",
        student_verification_toast: "",
    });
    const [finalResult, setFinalResult] = useState({
        "id": 0,
        "timestamp": 0,
        "result_faceDetection": "",
        "result_facePoints": "",
        "gazeResult": {},
        "object_detection_result": [],
        "student_verification_result": {}, 
    })
    const [image, setImage] = useState(localStorage.getItem("studentImage") || null);
    const [message, setMessage] = useState("");
    const navigate = useNavigate()
    const [vivaStarted, setVivaStarted] = useState(false)
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null);
    const animationRef = useRef(null);
    const ws = useRef(null);
    const WS_URL = import.meta.env.VITE_REACT_APP_WS_URL;

    useEffect(() => {
    if (finalResult.length > 0) {
        console.log("Final Result (from useEffect):", finalResult);
    }
}, [finalResult]);

    const startCamera = async() =>{
        try{
            let lastSent = 0;
            ws.current=new WebSocket(WS_URL);

            ws.current.onopen=()=>{
                toast.success("Websocket Opened Successfully")
            }

            ws.current.onmessage=(event)=>{
                try{
                    const data=JSON.parse(event.data)
                    // console.log("Received from backend:", data);
                    if (data.type==='fail'){
                        toast.info(data.final_toast)
                    }
                    else if (data.type==='success'){
                        // console.log(data.final_toast)
                        // toast.success(data.final_toast)
                        setPerProcessData(data.per_frame_result);
                        console.log("Per Process Data:", data.per_frame_result);
                    }

                    if (data.type==='final'){
                        setFinalResult(data.final_result);
                    }
                }catch(error){
                    toast.error("Error processing data from server", error);
                }
            }

            ws.current.onerror = (e) => {
                toast.error("WebSocket connection error", e);
            };
            ws.current.onclose = () => {
                toast.success("🛑 WebSocket Closed Successfully");
            };
            const stream=await navigator.mediaDevices.getUserMedia({video:true})
            streamRef.current=stream
            if(videoRef.current){
                videoRef.current.srcObject=stream;
            }
            const captureFrames = () =>{
                const video=videoRef.current;
                const canvas=canvasRef.current;
                const ctx=canvas?.getContext("2d");
                if (video && canvas && ctx) {
                    canvas.width=video.videoWidth;
                    canvas.height=video.videoHeight;
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    const now = Date.now();
                    if (ws.current && ws.current.readyState===WebSocket.OPEN && now-lastSent>1000){
                        const frame=canvas.toDataURL("image/jpeg")
                        ws.current.send(JSON.stringify({type:"frame", frame: frame, user_image:image}));
                        lastSent=now
                    }
                    animationRef.current=requestAnimationFrame(captureFrames);
                }
            };
            captureFrames();
        }catch(error){
            toast.error("Error starting camera", error.message);
        }
    }

    const stopCamera = () =>{
        if(streamRef.current){
            streamRef.current.getTracks().forEach((track)=>track.stop());
            streamRef.current=null
        }
        if(animationRef.current){
            cancelAnimationFrame(animationRef.current)
        }
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.close();
            toast.success("Websocket Closed On End Viva Button")
        }
    }

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

    const handleStartViva = () => {
        toast.success("Viva Started Successfully")
        setVivaStarted(true)
        startCamera()
    }

    const handleEndViva = () => {
        stopCamera()
        setVivaStarted(false)
        toast.success("Viva ended successfully")
        setMessage("Viva ended successfully")
        localStorage.clear()
        // navigate(0)
    };

    useEffect(() => {
        if (finalResult.length > 0) {
            localStorage.setItem("finalResult", JSON.stringify(finalResult));
        }
    }, [finalResult]);

    useEffect(() => {
        const stored = localStorage.getItem("finalResult");
        if (stored) setFinalResult(JSON.parse(stored));
    }, []);

    return(
        <div style={{ padding: "2rem" }}>
            <h2>Welcome, {name}</h2>
            <p>{message}</p>
            {/* <p>{image}</p> */}
            {/* {image && (
                <img
                    src={`data:image/png;base64,${image}`}
                    alt="Registered face"
                    style={{ width: "200px", height: "200px", borderRadius: "8px", marginBottom: "20px" }}
                />
            )} */}
            {!vivaStarted? 
            (   
                <button onClick={handleStartViva} style={{ padding: "10px 20px", marginTop: "10px" }}>Start Viva</button>
            ):(
                <>
                <div style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "10px",
                            zIndex: 10,
                            backgroundColor: "rgba(0,0,0,0.5)",
                            padding: "10px",
                            borderRadius: "8px",
                            color: "white",
                            fontWeight: "bold"
                    }}>
                        <div>Gaze: {perProcessData.gaze_toast || "No data"}</div>
                        <div>Object: {perProcessData.object_toast || "No data"}</div>
                        <div>Student Verification: {perProcessData.student_verification_toast || "No data"}</div>
                        <div>Distance Toast: {perProcessData.distance_toast?.toast || "No data"}</div>
                        <div>Distance: {perProcessData.distance_toast?.distance?.toFixed(2) || "0.00"} cm</div>
                    </div>
                    <div style={{ position: "relative", width: "100%", maxWidth: "640px" }}>
                        <video ref={videoRef} autoPlay muted style={{ width: "100%" }} />
                        <canvas ref={canvasRef} style={{ display: "none" }} />
                    </div>
                    <button onClick={handleEndViva} style={{ padding: "10px 20px", marginTop: "10px" }}>
                        End Viva
                    </button>
                    
                </>
            )}
            {finalResult.length > 0 && (
                <div style={{ marginTop: "20px" }}>
                    <h3>📊 Final Viva Result Summary</h3>
                    <ul>
                        {finalResult.map((item, index) => (
                            <li key={index}>{item}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}