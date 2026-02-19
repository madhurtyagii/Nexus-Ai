import { useState, useRef, useEffect } from 'react';
import { Mic, Square, Loader2, Volume2, VolumeX } from 'lucide-react';
import { voiceAPI } from '../../services/api';
import toast from 'react-hot-toast';

export default function VoiceRecorder({ onTranscription, disabled }) {
    const [isRecording, setIsRecording] = useState(false);
    const [isTranscribing, setIsTranscribing] = useState(false);
    const [autoSpeak, setAutoSpeak] = useState(() => {
        return localStorage.getItem('nexus_auto_speak') === 'true';
    });

    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);

    useEffect(() => {
        localStorage.setItem('nexus_auto_speak', autoSpeak);
    }, [autoSpeak]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
                await handleTranscription(audioBlob);

                // Stop all tracks to release microphone
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (error) {
            console.error('Microphone access denied:', error);
            toast.error('Could not access microphone');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const handleTranscription = async (blob) => {
        setIsTranscribing(true);
        const formData = new FormData();
        formData.append('file', blob, 'recording.webm');

        try {
            const response = await voiceAPI.transcribe(formData);
            if (response.data.text) {
                onTranscription(response.data.text);
            }
        } catch (error) {
            console.error('Transcription failed:', error);
            toast.error('Failed to transcribe audio');
        } finally {
            setIsTranscribing(false);
        }
    };

    const toggleAutoSpeak = () => {
        const newValue = !autoSpeak;
        setAutoSpeak(newValue);
        toast.success(newValue ? 'Auto-speak enabled' : 'Auto-speak disabled');
    };

    return (
        <div className="flex items-center gap-2">
            <button
                type="button"
                onClick={toggleAutoSpeak}
                className={`p-2 rounded-lg transition-all ${autoSpeak
                        ? 'text-primary-400 bg-primary-400/10'
                        : 'text-dark-500 hover:text-dark-300'
                    }`}
                title={autoSpeak ? "Auto-speak enabled" : "Auto-speak disabled"}
            >
                {autoSpeak ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
            </button>

            <button
                type="button"
                disabled={disabled || isTranscribing}
                onClick={isRecording ? stopRecording : startRecording}
                className={`p-2 rounded-xl transition-all relative group ${isRecording
                        ? 'bg-red-500/10 text-red-500'
                        : 'text-dark-400 hover:text-primary-400 hover:bg-primary-500/10'
                    } disabled:opacity-30`}
            >
                {isRecording && (
                    <span className="absolute inset-0 rounded-xl bg-red-500/20 animate-ping" />
                )}

                {isTranscribing ? (
                    <Loader2 className="w-6 h-6 animate-spin text-primary-400" />
                ) : isRecording ? (
                    <Square className="w-6 h-6 fill-current" />
                ) : (
                    <Mic className="w-6 h-6 transition-transform group-hover:scale-110" />
                )}
            </button>
        </div>
    );
}
