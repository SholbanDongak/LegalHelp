import { useApp } from '../../contexts/AppContext';

export const HistoryList = () => {
  const { chatHistory, loadFromHistory, deleteHistoryItem } = useApp();
  
  if (chatHistory.length === 0) {
    return (
      <div className="empty-history">
        <div style={{ fontSize: '3rem' }}>🕒</div>
        <h3>История пуста</h3>
        <p>Ваши диалоги будут сохраняться здесь автоматически</p>
      </div>
    );
  }
  
  return (
    <div className="history-list">
      <h2>🕒 История диалогов</h2>
      <div className="list">
        {chatHistory.map(item => (
          <div key={item.id} className="history-item">
            <div className="item-content" onClick={() => loadFromHistory(item)}>
              <div style={{ fontSize: '1.5rem' }}>💬</div>
              <div className="item-info">
                <h4>{item.title}</h4>
                <p>{new Date(item.time).toLocaleString('ru-RU')}</p>
              </div>
            </div>
            <button className="delete-btn" onClick={() => deleteHistoryItem(item.id)}>
              🗑️
            </button>
          </div>
        ))}
      </div>
      
      <style>{`
        .history-list { flex: 1; overflow-y: auto; padding: 2rem; max-width: 800px; margin: 0 auto; width: 100%; }
        .history-list h2 { margin-bottom: 1.5rem; color: var(--text-primary); }
        .empty-history { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--text-secondary); gap: 1rem; }
        .list { display: flex; flex-direction: column; gap: 0.75rem; }
        .history-item { display: flex; align-items: center; gap: 1rem; padding: 1rem; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; transition: 0.2s; }
        .history-item:hover { border-color: var(--primary); background: var(--bg-tertiary); }
        .item-content { flex: 1; display: flex; align-items: center; gap: 1rem; cursor: pointer; }
        .item-info { flex: 1; }
        .item-info h4 { margin: 0 0 0.25rem 0; font-size: 1rem; color: var(--text-primary); }
        .item-info p { margin: 0; font-size: 0.85rem; color: var(--text-secondary); }
        .delete-btn { background: none; border: none; cursor: pointer; padding: 0.5rem; border-radius: 8px; transition: 0.2s; font-size: 1.2rem; }
        .delete-btn:hover { background: rgba(239, 68, 68, 0.1); }
      `}</style>
    </div>
  );
};
