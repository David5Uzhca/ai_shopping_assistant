
import { useEffect, useState, useRef } from "react";
import { ChatResponse, sendChatMessage } from "../../lib/api";

type VoiceChatProps = {
    sessionId: string | null;
    user: any;
    onClose: () => void;
    onUpdateSession: (newSessionId: string) => void;
};

type PetState = "waiting" | "listening" | "thinking" | "speaking";

export function VoiceChat({ sessionId, user, onClose, onUpdateSession }: VoiceChatProps) {
    const [state, setState] = useState<PetState>("waiting");
    const [transcript, setTranscript] = useState("");
    const [response, setResponse] = useState("");

    // Speech Recognition Setup
    const recognitionRef = useRef<any>(null);
    const synthesisRef = useRef<SpeechSynthesis>(window.speechSynthesis);

    useEffect(() => {
        // Initialize Speech Recognition
        console.log("[VOICE] Initializing SpeechRecognition...");

        // Fix #1: Load voices proactively
        const loadVoices = () => {
            const voices = window.speechSynthesis.getVoices();
            console.log("[VOICE] 🎙️ Available voices:", voices.length);
        };
        window.speechSynthesis.onvoiceschanged = loadVoices;
        loadVoices();

        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = "es-ES";
            recognition.interimResults = false;

            recognition.onstart = () => {
                console.log("[VOICE] 🟢 Recognition started (Listening)");
                setState("listening");
            };

            recognition.onend = () => {
                console.log("[VOICE] 🔴 Recognition ended");
                // Si termina y seguíamos escuchando, volvemos a waiting.
                // Si cambiamos a "thinking" (en onresult), no tocamos el estado.
                setState(prev => prev === "listening" ? "waiting" : prev);
            };

            recognition.onerror = (event: any) => {
                console.error("[VOICE] ⚠️ Recognition Error:", event.error);
                setState("waiting");
                if (event.error === 'not-allowed') {
                    alert("Permiso de micrófono denegado.");
                }
            };

            recognition.onresult = (event: any) => {
                const text = event.results[0][0].transcript;
                console.log("[VOICE] 📝 Transcript received:", text);
                setTranscript(text);
                // Transición inmediata a thinking para evitar race conditions con onend
                setState("thinking");
                handleUserMessage(text);
            };

            recognitionRef.current = recognition;
        } else {
            console.warn("[VOICE] Speech Recognition API NOT supported in this browser.");
        }

        return () => {
            console.log("[VOICE] Cleanup component");
            if (recognitionRef.current) {
                recognitionRef.current.abort();
            }
            synthesisRef.current.cancel();
        };
    }, []);

    const handleUserMessage = async (text: string) => {
        console.log("[VOICE] 🚀 Sending message to API:", text);
        setState("thinking");
        try {
            const res = await sendChatMessage({
                message: text,
                session_id: sessionId,
                user_id: user?.user_id,
                generate_audio: true // Solicitar audio ElevenLabs
            });

            console.log("[VOICE] ✅ API Response received:", res);
            onUpdateSession(res.session_id);
            setResponse(res.response);

            if (res.audio) {
                console.log("[VOICE] 🔊 Playing ElevenLabs Audio...");
                const audio = new Audio("data:audio/mpeg;base64," + res.audio);

                audio.onplay = () => {
                    console.log("[VOICE] ▶️ Audio playing");
                    setState("speaking");
                };

                audio.onended = () => {
                    console.log("[VOICE] ⏹️ Audio finished");
                    setState("waiting");
                };

                audio.onerror = (e) => {
                    console.error("[VOICE] ❌ Audio playback error:", e);
                    setState("waiting");
                };

                await audio.play();
            } else {
                console.warn("[VOICE] ⚠️ No audio received, falling back to browser TTS");
                speakResponse(res.response); // Fallback
            }

        } catch (e: any) {
            console.error("[VOICE] ❌ API Error:", e);
            speakResponse("Lo siento, hubo un error. Intenta de nuevo.");
        }
    };

    const speakResponse = (text: string) => {
        console.log("[VOICE] 🗣️ Speaking response:", text);
        // Cancelar cualquier lectura anterior para que hable lo nuevo inmediatamente
        synthesisRef.current.cancel();

        // Fix #2: Select Voice
        const voices = synthesisRef.current.getVoices();
        const spanishVoice = voices.find(v => v.lang.startsWith("es"));

        if (!spanishVoice) {
            console.warn("[VOICE] ⚠️ No Spanish voice found, using default");
        } else {
            console.log("[VOICE] 🗣️ Using voice:", spanishVoice.name);
        }

        setState("speaking");
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "es-ES";

        if (spanishVoice) {
            utterance.voice = spanishVoice;
        }

        utterance.volume = 1;
        utterance.rate = 1;
        utterance.pitch = 1;

        utterance.onstart = () => {
            console.log("[VOICE] 🔊 Speech started");
            setState("speaking");
        };

        utterance.onend = () => {
            console.log("[VOICE] 🔇 Speaking finished");
            setState("waiting");
        };

        utterance.onerror = (e) => {
            console.error("[VOICE] ❌ Speech Error:", e);
            setState("waiting");
        };

        synthesisRef.current.speak(utterance);
    };

    // Fix #3: Unlock Audio Context
    const unlockAudio = () => {
        const AudioContext = (window as any).AudioContext || (window as any).webkitAudioContext;
        if (AudioContext) {
            const ctx = new AudioContext();
            if (ctx.state === "suspended") {
                ctx.resume().then(() => console.log("[VOICE] 🔊 AudioContext resumed"));
            }
        }
    };

    const startListening = async () => {
        console.log("[VOICE] Start listening requested");
        unlockAudio(); // Try to unlock audio

        if (!recognitionRef.current) {
            alert("Tu navegador no soporta reconocimiento de voz.");
            return;
        }

        const hasPermission = await requestMicPermission();
        if (!hasPermission) return;

        try {
            recognitionRef.current.start();
        } catch (e) {
            console.log("[VOICE] Recognition start error (already started?):", e);
        }
    };


    const requestMicPermission = async () => {
        console.log("[VOICE] Requesting Mic Permission...");
        try {
            await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log("[VOICE] ✅ Mic Permission GRANTED");
            return true;
        } catch (err) {
            console.error("[VOICE] 🚫 Mic Permission DENIED", err);
            alert("Debes permitir el micrófono para usar esta función.");
            return false;
        }
    };


    // Determine Image
    const getPetImage = () => {
        switch (state) {
            case "listening": return "/pet/petListen.png";
            case "speaking": return "/pet/petTalk.png";
            case "thinking": return "/pet/petWait.png"; // Or distinct thinking image
            default: return "/pet/petWait.png";
        }
    };



    return (
        <div className="voiceChatOverlay">
            <h1 className="voiceTitle">ShopiBOT</h1>

            <div className="petContainer">
                <img
                    src={getPetImage()}
                    alt="Pet Avatar"
                    className={`petImage ${state}`}
                />

                <div className="petStatus">
                    {state === "listening" && <p className="listening">Escuchando...</p>}
                    {state === "thinking" && <p className="thinking">Pensando...</p>}
                    {state === "speaking" && <p className="speaking">Hablando...</p>}
                    {state === "waiting" && transcript && <p className="lastMsg">"{transcript}"</p>}
                </div>
            </div>

            <div className="voiceControls">
                <button className="btn btnSecondary" onClick={onClose}>
                    Chat
                </button>
                <button
                    className={`btn btnPrimary ${state === "listening" ? "active" : ""}`}
                    onClick={startListening}
                    disabled={state === "thinking" || state === "speaking"}
                >
                    {state === "listening" ? "Escuchando..." : "Hablar 🎤"}
                </button>
            </div>

            <style>{`
        .voiceChatOverlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: var(--bg-body); /* Usar mismo fondo que el chat */
            z-index: 999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--text-main); /* Usar color de texto principal */
        }
        .voiceTitle {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 2rem;
            color: var(--brand); /* Color de marca */
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .petContainer {
            position: relative;
            width: 300px;
            height: 300px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 2rem;
        }
        .petImage {
            width: 100%;
            height: auto;
            object-fit: contain;
            transition: transform 0.2s ease;
            filter: drop-shadow(0 10px 15px rgba(0,0,0,0.2));
        }
        .petImage.speaking {
            animation: bounce 0.5s infinite alternate;
        }
        @keyframes bounce {
            from { transform: translateY(0); }
            to { transform: translateY(-10px); }
        }
        .voiceControls {
            display: flex;
            gap: 1rem;
            margin-top: 20px;
        }
        .petStatus {
            position: absolute;
            bottom: -40px;
            width: 100%;
            text-align: center;
            font-size: 1.2rem;
            font-weight: 500;
            color: var(--text-muted);
        }
        .petStatus p {
            margin: 0;
        }
        .listening { color: var(--brand); }
        .speaking { color: #10b981; }
      `}</style>
        </div>
    );
}
