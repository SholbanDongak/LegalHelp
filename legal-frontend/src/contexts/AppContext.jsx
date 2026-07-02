import { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const useApp = () => useContext(AppContext);

export const AppProvider = ({ children }) => {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([
    { id: 1, text: 'Привет! Я AI-ассистент LegalHelp. Опишите вашу юридическую ситуацию.', sender: 'bot', time: new Date() }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [docQuery, setDocQuery] = useState('');
  const [prefillData, setPrefillData] = useState(null);
  const [chatHistory, setChatHistory] = useState(() => {
    const saved = localStorage.getItem('legalhelp_history');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('legalhelp_history', JSON.stringify(chatHistory));
  }, [chatHistory]);

  const addMessage = (msg) => setMessages(prev => [...prev, { ...msg, id: Date.now(), time: new Date() }]);
  
  const saveChatToHistory = () => {
    const userMessages = messages.filter(m => m.sender === 'user');
    if (userMessages.length === 0) return false;
    
    const title = userMessages[0]?.text?.slice(0, 50) || 'Диалог';
    const newItem = {
      id: Date.now(),
      title,
      messages: [...messages],
      time: new Date().toISOString()
    };
    setChatHistory(prev => [newItem, ...prev].slice(0, 20));
    return true;
  };
  
  const clearChat = () => {
    saveChatToHistory();
    setMessages([{ id: 1, text: 'Новый диалог начат.', sender: 'bot', time: new Date() }]);
  };
  
  const loadFromHistory = (historyItem) => {
    setMessages(historyItem.messages);
    setActiveTab('chat');
  };
  
  const deleteHistoryItem = (id) => {
    setChatHistory(prev => prev.filter(item => item.id !== id));
  };

  const generateDocument = async (query, docType = null, userFields = null) => {
    if (!query?.trim()) {
      return { success: false, error: 'Пустой запрос' };
    }
    
    setIsGenerating(true);
    setGeneratedDoc(null);
    
    try {
      const requestBody = {
        query,
        output_format: 'both'
      };
      
      if (docType) {
        requestBody.force_doc_type = docType;
      }
      
      if (userFields && Object.keys(userFields).length > 0) {
        requestBody.user_fields = userFields;
      }
      
      const res = await fetch('http://localhost:8000/api/generate-document', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      
      const data = await res.json();
      
      if (data.success && data.filled_text) {
        setGeneratedDoc(data);
        return data;
      } else {
        const errorMsg = data.error || 'Не удалось сгенерировать документ';
        return { success: false, error: errorMsg };
      }
    } catch (e) {
      return { success: false, error: 'Ошибка соединения: ' + e.message };
    } finally {
      setIsGenerating(false);
    }
  };
  
  const clearPrefillData = () => setPrefillData(null);
  
  const openDocumentGenerator = (data) => {
    // data может быть строкой (query) или объектом с полными данными
    if (typeof data === 'string') {
      setDocQuery(data);
      setPrefillData({ docQuery: data });
    } else if (data && typeof data === 'object') {
      setDocQuery(data.docQuery || '');
      setPrefillData(data);
    }
    setGeneratedDoc(null);
    setActiveTab('generate');
  };
  
  return (
    <AppContext.Provider value={{
      activeTab, setActiveTab,
      messages, setMessages, addMessage, clearChat, saveChatToHistory,
      chatHistory, loadFromHistory, deleteHistoryItem,
      isLoading, setIsLoading,
      generatedDoc, setGeneratedDoc, isGenerating, generateDocument,
      docQuery, setDocQuery, openDocumentGenerator, prefillData, clearPrefillData
    }}>
      {children}
    </AppContext.Provider>
  );
};
