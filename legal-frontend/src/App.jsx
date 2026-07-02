import { AppProvider, useApp } from './contexts/AppContext';
import { Header } from './components/Layout/Header';
import { ChatWindow } from './components/Chat/ChatWindow';
import { GeneratorForm } from './components/DocumentGenerator/GeneratorForm';
import { HistoryList } from './components/Layout/HistoryList';

const MainContent = () => {
  const { activeTab } = useApp();
  
  return (
    <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: '#0b1120' }}>
      {activeTab === 'chat' && <ChatWindow />}
      {activeTab === 'generate' && <GeneratorForm />}
      {activeTab === 'history' && <HistoryList />}
    </main>
  );
};

function App() {
  return (
    <AppProvider>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#0b1120' }}>
        <Header />
        <MainContent />
      </div>
    </AppProvider>
  );
}

export default App;
