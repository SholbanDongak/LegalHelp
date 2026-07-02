import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useApp } from '../../contexts/AppContext';

export const ChatWindow = () => {
  const { isLoading } = useApp();
  
  return (
    <div className="chat-window">
      <MessageList />
      {isLoading && (
        <div className="typing-indicator">
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
      )}
      <MessageInput />
      <style>{`
        .chat-window { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .typing-indicator { position: absolute; bottom: 100px; left: 1.5rem; display: flex; gap: 4px; padding: 0.75rem 1rem; background: var(--bg-secondary); border-radius: 12px; border: 1px solid var(--border); }
        .dot { width: 8px; height: 8px; background: var(--text-secondary); border-radius: 50%; animation: bounce 1.4s infinite; }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-8px); } }
      `}</style>
    </div>
  );
};
