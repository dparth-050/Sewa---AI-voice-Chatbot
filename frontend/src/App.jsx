import { useState } from "react";
import axios from "axios";
import { Mic, Send, Volume2, Square, LoaderCircle, Landmark } from "lucide-react";

const API = "http://localhost:8000";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "નમસ્તે! હું ગુજરાત રેવન્યુ AI સહાયક છું. જમીન રેકોર્ડ, અરજી પ્રક્રિયા અથવા જરૂરી દસ્તાવેજો વિશે હું કેવી રીતે મદદ કરી શકું?" }
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [recording, setRecording] = useState(false);
  const [recorder, setRecorder] = useState(null);

  async function sendMessage(text = input) {
    const question = text.trim();
    if (!question || busy) return;
    setMessages(m => [...m, { role: "user", text: question }]);
    setInput("");
    setBusy(true);
    try {
      const { data } = await axios.post(`${API}/api/chat`, { message: question });
      setMessages(m => [...m, {
        role: "assistant", text: data.answer,
        sources: data.sources || [], verified: data.verified_context_found
      }]);
    } catch (e) {
      setMessages(m => [...m, { role: "assistant", text: "માફ કરશો, હાલમાં AI સેવા ઉપલબ્ધ નથી. કૃપા કરીને થોડી વાર પછી ફરી પ્રયાસ કરો." }]);
    } finally { setBusy(false); }
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const media = new MediaRecorder(stream);
      const chunks = [];
      media.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
      media.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(chunks, { type: media.mimeType || "audio/webm" });
        const form = new FormData();
        form.append("audio", blob, "recording.webm");
        setBusy(true);
        try {
          const { data } = await axios.post(`${API}/api/voice/transcribe`, form);
          setInput(data.text || "");
        } catch {
          setMessages(m => [...m, { role: "assistant", text: "અવાજ સમજવામાં મુશ્કેલી પડી. કૃપા કરીને ફરી બોલો." }]);
        } finally { setBusy(false); }
      };
      media.start();
      setRecorder(media);
      setRecording(true);
    } catch {
      alert("માઇક્રોફોન પરવાનગી આપો અને HTTPS અથવા localhost નો ઉપયોગ કરો.");
    }
  }

  function stopRecording() {
    if (recorder && recorder.state !== "inactive") recorder.stop();
    setRecording(false);
  }

  async function speak(text) {
    try {
      const response = await axios.post(`${API}/api/voice/speak`, { message: text }, { responseType: "blob" });
      const url = URL.createObjectURL(response.data);
      const audio = new Audio(url);
      audio.onended = () => URL.revokeObjectURL(url);
      await audio.play();
    } catch { alert("ગુજરાતી અવાજ હાલમાં ઉપલબ્ધ નથી."); }
  }

  return <main className="page">
    <header className="topbar">
      <div className="brand"><Landmark size={28}/><div><strong>ગુજરાત રેવન્યુ AI</strong><small>નાગરિક સહાયતા કેન્દ્ર · 24/7</small></div></div>
      <span className="status">● AI સહાયક ઉપલબ્ધ</span>
    </header>
    <section className="hero">
      <p className="eyebrow">REVENUE DEPARTMENT · GUJARAT</p>
      <h1>તમારી જમીન અને મહેસૂલ સેવાઓ હવે સરળતાથી</h1>
      <p>ગુજરાતીમાં બોલો અથવા લખો. અરજી પ્રક્રિયા, દસ્તાવેજો અને જમીન રેકોર્ડ વિશે માર્ગદર્શન મેળવો.</p>
      <div className="quick">
        {["7/12 ઉતારા વિશે માહિતી આપો", "NA પ્રક્રિયા માટે કયા દસ્તાવેજો જોઈએ?", "iORA અરજી કેવી રીતે કરવી?"].map(q =>
          <button key={q} className="chip" onClick={() => sendMessage(q)}>{q}</button>)}
      </div>
    </section>
    <section className="chat">
      <div className="chat-head"><div><b>વાતચીત</b><small> · ગુજરાતી સહાયક</small></div><span>સામાન્ય માર્ગદર્શન</span></div>
      <div className="messages">
        {messages.map((m, i) => <div key={i} className={`message ${m.role}`}>
          <div className="bubble">{m.text}
            {m.sources?.length > 0 && <div className="sources">સંદર્ભ: {m.sources.join(", ")}</div>}
            {m.role === "assistant" && <button className="listen" title="જવાબ સાંભળો" onClick={() => speak(m.text)}><Volume2 size={16}/> સાંભળો</button>}
          </div>
        </div>)}
        {busy && <div className="typing"><LoaderCircle className="spin" size={16}/> જવાબ તૈયાર થઈ રહ્યો છે...</div>}
      </div>
      <div className="composer">
        <button className={`mic ${recording ? "recording" : ""}`} onClick={recording ? stopRecording : startRecording} title={recording ? "રેકોર્ડિંગ બંધ કરો" : "ગુજરાતીમાં બોલો"}>
          {recording ? <Square size={19}/> : <Mic size={20}/>}
        </button>
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && sendMessage()} placeholder="તમારો પ્રશ્ન ગુજરાતીમાં લખો..." />
        <button className="send" onClick={() => sendMessage()} disabled={!input.trim() || busy}><Send size={19}/></button>
      </div>
      <p className="disclaimer">આ પ્રોટોટાઇપ સામાન્ય માર્ગદર્શન આપે છે. કાનૂની/સરકારી નિર્ણય માટે સત્તાવાર માહિતીની પુષ્ટિ કરો. ખાનગી અરજીની સ્થિતિ અહીં હજી લાઇવ જોડાયેલી નથી.</p>
    </section>
    <footer>Gujarati Revenue AI · Student prototype for PS000216</footer>
  </main>;
}
