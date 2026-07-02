import { useApp } from '../../contexts/AppContext';
import { FiMessageSquare, FiFileText, FiClock, FiMoon } from 'react-icons/fi';

export const Header = () => {
  const { activeTab, setActiveTab } = useApp();
  const tabs = [
    { id: 'chat', label: 'Чат', icon: FiMessageSquare },
    { id: 'generate', label: 'Документы', icon: FiFileText },
    { id: 'history', label: 'История', icon: FiClock }
  ];

  return (
    <header className="header glass">
      <div className="logo">
        <span className="icon">⚖️</span>
        <h1>LegalHelp AI</h1>
      </div>
      <nav className="tabs">
        {tabs.map(t => {
          const Icon = t.icon;
          return (
            <button key={t.id} className={`tab ${activeTab === t.id ? 'active' : ''}`} onClick={() => setActiveTab(t.id)}>
              <Icon size={18} /> {t.label}
            </button>
          );
        })}
      </nav>
      <style>{`
        .header { padding: 0.8rem 1.5rem; display: flex; justify-content: space-between; align-items: center; }
        .logo { display: flex; align-items: center; gap: 0.6rem; }
        .logo .icon { font-size: 1.6rem; }
        .logo h1 { font-size: 1.25rem; background: linear-gradient(90deg, #6366f1, #a78bfa); -webkit-background-clip: text; color: transparent; }
        .tabs { display: flex; gap: 0.5rem; background: var(--bg-secondary); padding: 0.3rem; border-radius: 10px; }
        .tab { display: flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem; background: transparent; border: none; border-radius: 8px; color: var(--text-secondary); cursor: pointer; transition: 0.2s; font-weight: 500; }
        .tab:hover { color: var(--text-primary); background: rgba(255,255,255,0.05); }
        .tab.active { background: var(--primary); color: white; box-shadow: var(--shadow); }
      `}</style>
    </header>
  );
};
