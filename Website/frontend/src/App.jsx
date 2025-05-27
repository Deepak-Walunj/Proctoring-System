import {LandingPage} from './Components/LandingPage.jsx';
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import InputDetails from './Components/InputDetails.jsx';
import VideoAnalysis from './Components/VideoAnalysis.jsx';
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/InputDetails" element={<InputDetails />} />
          <Route path="/video-analysis/:name" element={<VideoAnalysis />} />
          {/* Add more routes as needed */}
        </Routes>
      </BrowserRouter>
      <ToastContainer position="top-right" autoClose={3000} />
    </>
    
  );
}
