import { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Привет! Я AI-ассистент LegalHelp. Задайте ваш вопрос.', sender: 'bot' }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = { id: Date.now(), text: inputText, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          company_name: 'ООО Ромашка',
          inn: '1234567890',
          document_type: 'other',
          manual_text: inputText
        })
      });
      const data = await response.json();
      const botMessage = { id: Date.now(), text: data.draft_answer, sender: 'bot' };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Ошибка:', error);
      const errorMessage = { id: Date.now(), text: 'Извините, произошла ошибка. Проверьте, запущен ли бэкенд.', sender: 'bot' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>⚖️ LegalHelp — Ваш юридический ассистент</h2>
      </div>
      <div className="messages-container">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            <div className="message-content">{msg.text}</div>
          </div>
        ))}
        {isLoading && <div className="message bot"><div className="message-content">Печатаю...</div></div>}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Опишите вашу ситуацию или задайте вопрос..."
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading}>Отправить</button>
      </div>
    </div>
  );
}

export default App;
