import { useApp } from '../../contexts/AppContext';
import { FiFileText } from 'react-icons/fi';

// Маппинг типов документов на человекочитаемые названия
const DOC_TYPE_LABELS = {
  'claim_civil_general': 'Исковое заявление (общее)',
  'claim_consumer': 'Иск о защите прав потребителей',
  'claim_labor_wage': 'Иск о взыскании зарплаты',
  'claim_labor_reinstatement': 'Иск о восстановлении на работе',
  'claim_divorce': 'Иск о расторжении брака',
  'claim_alimony': 'Иск о взыскании алиментов',
  'admin_claim_kas': 'Административное исковое заявление',
  'complaint_koap': 'Жалоба на постановление по КоАП',
  'application_for_court_order': 'Заявление о судебном приказе',
  'objection_to_court_order': 'Возражение на судебный приказ',
  'appeal_civil': 'Апелляционная жалоба',
  'cassation_civil': 'Кассационная жалоба',
  'special_proceeding_fact': 'Заявление об установлении факта'
};

export const MessageList = () => {
  const { messages, openDocumentGenerator } = useApp();
  
  return (
    <div className="message-list">
      {messages.map(msg => (
        <div key={msg.id} className={`message ${msg.sender}`}>
          <div className="avatar">
            {msg.sender === 'bot' ? '🤖' : '👤'}
          </div>
          <div className="content">
            <div className="text">{msg.text}</div>
            {msg.sender === 'bot' && msg.id !== 1 && (
              <button 
                className="suggest-doc-btn"
                onClick={() => {
                  const lastUserMsg = [...messages].reverse().find(m => m.sender === 'user');
                  const query = lastUserMsg?.text || msg.text;
                  
                  // Если есть метаданные от AI-агента — используем их
                  if (msg.agentMetadata) {
                    openDocumentGenerator({
                      docQuery: query,
                      chatMessages: messages.map(m => ({ text: m.text, sender: m.sender })),
                      suggestedDocType: msg.agentMetadata.doc_type,
                      prefillData: {
                        docType: msg.agentMetadata.doc_type,
                        docLabel: msg.agentMetadata.doc_label,
                        entities: msg.agentMetadata.entities,
                        duty: msg.agentMetadata.duty
                      }
                    });
                  } else {
                    // Старая логика — без метаданных
                    openDocumentGenerator({
                      docQuery: query,
                      chatMessages: messages.map(m => ({ text: m.text, sender: m.sender })),
                      suggestedDocType: null
                    });
                  }
                }}
              >
                <FiFileText size={14} />
                {msg.agentMetadata 
                  ? `📄 Составить: ${DOC_TYPE_LABELS[msg.agentMetadata.doc_type] || msg.agentMetadata.doc_label} (госпошлина: ${msg.agentMetadata.duty?.duty?.toLocaleString('ru-RU')} ₽)`
                  : 'Составить документ по этой ситуации'}
              </button>
            )}
            <div className="time">
              {new Date(msg.time).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        </div>
      ))}
      <style>{`
        .message-list { flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
        .message { display: flex; gap: 0.75rem; max-width: 85%; animation: fadeIn 0.3s ease-out; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .message.bot { align-self: flex-start; }
        .avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1.2rem; background: var(--bg-tertiary); }
        .content { display: flex; flex-direction: column; gap: 0.4rem; }
        .text { padding: 0.75rem 1rem; border-radius: 12px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; }
        .message.user .text { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border-bottom-right-radius: 4px; }
        .message.bot .text { background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border); border-bottom-left-radius: 4px; }
        .time { font-size: 0.75rem; color: var(--text-secondary); padding: 0 0.5rem; }
        .message.user .time { text-align: right; }
        .suggest-doc-btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.4rem 0.75rem; background: transparent; border: 1px solid var(--primary); color: var(--primary); border-radius: 8px; cursor: pointer; font-size: 0.8rem; transition: 0.2s; align-self: flex-start; margin-top: 0.25rem; }
        .suggest-doc-btn:hover { background: var(--primary); color: white; }
      `}</style>
    </div>
  );
};
