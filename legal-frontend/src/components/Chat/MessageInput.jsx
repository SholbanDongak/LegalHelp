import { useState, useRef } from 'react';
import { useApp } from '../../contexts/AppContext';
import { FiSend, FiPaperclip, FiX, FiPlus } from 'react-icons/fi';

export const MessageInput = () => {
  const { addMessage, isLoading, setIsLoading, clearChat, messages } = useApp();
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const fileRef = useRef(null);
  
  const hasUserMessages = messages.some(m => m.sender === 'user');
  
  const sendMessage = async () => {
    if (!text.trim() && !file) return;
    
    const userMsg = { text: text || `📎 Файл: ${file.name}`, sender: 'user' };
    addMessage(userMsg);
    const currentText = text;
    setText('');
    setFile(null);
    setIsLoading(true);
    
    try {
      // Используем новый эндпоинт /api/chat с AI-агентом
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentText,
          history: messages.slice(-10).map(m => ({ role: m.sender === 'bot' ? 'assistant' : 'user', content: m.text }))
        })
      });
      
      const data = await res.json();
      const answer = data.response || data.draft_answer || 'Ответ получен';
      
      // Сохраняем сообщение с метаданными AI-агента
      addMessage({ 
        text: answer, 
        sender: 'bot',
        agentMetadata: data.agent_metadata || null
      });
    } catch (e) {
      addMessage({ text: '❌ Ошибка соединения с сервером', sender: 'bot' });
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  
  return (
    <div className="input-area">
      {file && (
        <div className="file-preview">
          📎 {file.name}
          <button onClick={() => setFile(null)}><FiX /></button>
        </div>
      )}
      <div className="input-row">
        {hasUserMessages && (
          <button className="icon-btn" onClick={clearChat} title="Новый диалог (сохранит текущий в историю)">
            <FiPlus size={20} />
          </button>
        )}
        <button className="icon-btn" onClick={() => fileRef.current.click()} title="Прикрепить файл">
          <FiPaperclip size={20} />
        </button>
        <input type="file" ref={fileRef} hidden onChange={(e) => setFile(e.target.files[0])} accept=".pdf,.png,.jpg,.jpeg" />
        
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Опишите вашу ситуацию..."
          rows="1"
          disabled={isLoading}
        />
        
        <button className="send-btn" onClick={sendMessage} disabled={isLoading} title="Отправить">
          {isLoading ? '⏳' : <FiSend size={20} />}
        </button>
      </div>
      <style>{`
        .input-area { padding: 1rem 1.5rem; border-top: 1px solid var(--border); background: var(--bg-secondary); flex-shrink: 0; }
        .file-preview { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem; background: var(--bg-tertiary); border-radius: 8px; margin-bottom: 0.5rem; font-size: 0.9rem; color: var(--text-primary); }
        .file-preview button { background: none; border: none; color: var(--text-secondary); cursor: pointer; padding: 0; display: flex; align-items: center; }
        .input-row { display: flex; gap: 0.75rem; align-items: center; }
        textarea { flex: 1; padding: 0.75rem 1rem; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 12px; color: var(--text-primary); font-family: inherit; font-size: 0.95rem; resize: none; min-height: 44px; max-height: 120px; }
        textarea:focus { outline: none; border-color: var(--primary); }
        .icon-btn { width: 44px; height: 44px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 12px; color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s; flex-shrink: 0; }
        .icon-btn:hover { background: var(--border); color: var(--text-primary); }
        .send-btn { width: 44px; height: 44px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border: none; border-radius: 12px; color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s; flex-shrink: 0; }
        .send-btn:hover:not(:disabled) { transform: scale(1.05); }
        .send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
      `}</style>
    </div>
  );
};
