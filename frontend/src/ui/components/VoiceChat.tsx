
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
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = "es-ES";
            recognition.interimResults = false;

            recognition.onstart = () => {
                setState("listening");
            };

            recognition.onend = () => {
                // If we were just listening and it stopped without processing (e.g. silence), go back to waiting
                // But if we have a result, handleResult will fire before onend usually.
                // We'll handle state transition in onresult.
                // If state is still listening, it means no result.
                // setState(prev => prev === "listening" ? "waiting" : prev);
            };

            recognition.onresult = async (event: any) => {
                const text = event.results[0][0].transcript;
                setTranscript(text);
                handleUserMessage(text);
            };

            recognitionRef.current = recognition;
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.abort();
            }
            synthesisRef.current.cancel();
        };
    }, []);

    const handleUserMessage = async (text: string) => {
        setState("thinking");
        try {
            const res = await sendChatMessage({
                message: text,
                session_id: sessionId,
                user_id: user?.user_id
            });

            onUpdateSession(res.session_id);
            setResponse(res.response);
            speakResponse(res.response);
        } catch (e) {
            console.error(e);
            speakResponse("Lo siento, hubo un error. Intenta de nuevo.");
        }
    };

    const speakResponse = (text: string) => {
        setState("speaking");
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "es-ES";
        utterance.onend = () => {
            setState("waiting");
        };
        synthesisRef.current.speak(utterance);
    };

    const startListening = () => {
        if (recognitionRef.current) {
            try {
                recognitionRef.current.start();
            } catch (e) {
                // If already started
                console.log(e);
            }
        } else {
            alert("Tu navegador no soporta reconocimiento de voz.");
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

                {/* Status Text/Transcript */}
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
