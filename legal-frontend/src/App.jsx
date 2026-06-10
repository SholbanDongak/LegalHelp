import { useState, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Привет! Я AI-ассистент LegalHelp. Задайте ваш вопрос или отправьте документ.', sender: 'bot' }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [docType, setDocType] = useState('other');
  const [judicialData, setJudicialData] = useState({
    subtype: 'objection_to_court_order',
    order_number: '', order_date: '', court_name: '', debtor_name: '', claimant_name: '', grounds: '',
    case_number: '', first_court_name: '', appeal_court_name: '', decision_date: '', plaintiff_name: '', defendant_name: '',
    admin_plaintiff: '', admin_defendant: '', resolution_number: '', resolution_date: '', authority_name: '', person_name: '', article: '',
    lower_courts: '', cassation_court: '', applicant: '', marriage_date: '', act_number: '', separation_date: '', employment_date: '',
    wage_period: '', wage_amount: '', product_name: '', defect_description: '', contract_number: '', amount: '', evidence: '', moral_damage: '', punishment: ''
  });
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const handleJudicialChange = (field, value) => {
    setJudicialData(prev => ({ ...prev, [field]: value }));
  };

  const cleanData = (obj) => {
    const result = {};
    for (const key in obj) {
      if (obj[key] && typeof obj[key] === 'string' && obj[key].trim() !== '') {
        result[key] = obj[key];
      } else if (obj[key] && typeof obj[key] !== 'string') {
        result[key] = obj[key];
      }
    }
    return result;
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => alert('Ответ скопирован')).catch(() => alert('Ошибка копирования'));
  };

  const downloadAsTxt = (text, filename) => {
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${filename}.txt`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const sendMessage = async () => {
    let userMessageText = '';
    let requestBody = {};
    if (docType === 'judicial_review') {
      const queryData = { subtype: judicialData.subtype, ...cleanData(judicialData) };
      userMessageText = `[${judicialData.subtype}] ` + JSON.stringify(queryData);
      requestBody = {
        company_name: 'ООО Ромашка',
        inn: '1234567890',
        document_type: 'judicial_review',
        manual_text: JSON.stringify(queryData)
      };
    } else {
      userMessageText = inputText.trim() || (selectedFile ? 'Отправлен файл' : '');
      requestBody = {
        company_name: 'ООО Ромашка',
        inn: '1234567890',
        document_type: docType,
        manual_text: inputText.trim()
      };
    }
    if (!userMessageText && !selectedFile) return;
    const userMessage = { id: Date.now(), text: userMessageText, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    try {
      let response;
      if (selectedFile && docType !== 'judicial_review') {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('company_name', 'ООО Ромашка');
        formData.append('inn', '1234567890');
        formData.append('document_type', docType);
        response = await fetch('http://localhost:8000/api/process', { method: 'POST', body: formData });
      } else {
        response = await fetch('http://localhost:8000/api/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams(requestBody)
        });
      }
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const botMessage = { id: Date.now(), text: data.draft_answer, sender: 'bot' };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error(error);
      const errorMessage = { id: Date.now(), text: 'Ошибка: ' + error.message, sender: 'bot' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setSelectedFile(null);
    }
  };

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const triggerFileInput = () => fileInputRef.current.click();
  const triggerCameraInput = () => cameraInputRef.current.click();

  const clearSelectedFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  const renderJudicialFields = () => {
    const sub = judicialData.subtype;
    if (sub === 'objection_to_court_order') {
      return (
        <>
          <input placeholder="Номер приказа" value={judicialData.order_number} onChange={e => handleJudicialChange('order_number', e.target.value)} />
          <input placeholder="Дата вынесения" value={judicialData.order_date} onChange={e => handleJudicialChange('order_date', e.target.value)} />
          <input placeholder="Мировой суд / участок" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Должник" value={judicialData.debtor_name} onChange={e => handleJudicialChange('debtor_name', e.target.value)} />
          <input placeholder="Взыскатель" value={judicialData.claimant_name} onChange={e => handleJudicialChange('claimant_name', e.target.value)} />
          <textarea rows="3" placeholder="Основания (причина несогласия)" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'appeal_civil') {
      return (
        <>
          <input placeholder="Номер дела" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <input placeholder="Суд первой инстанции" value={judicialData.first_court_name} onChange={e => handleJudicialChange('first_court_name', e.target.value)} />
          <input placeholder="Апелляционный суд" value={judicialData.appeal_court_name} onChange={e => handleJudicialChange('appeal_court_name', e.target.value)} />
          <input placeholder="Дата решения" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <textarea rows="3" placeholder="Основания обжалования" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'cassation_civil') {
      return (
        <>
          <input placeholder="Номер дела" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <input placeholder="Суды, прошедшие инстанции" value={judicialData.lower_courts} onChange={e => handleJudicialChange('lower_courts', e.target.value)} />
          <input placeholder="Суд кассационной инстанции" value={judicialData.cassation_court} onChange={e => handleJudicialChange('cassation_court', e.target.value)} />
          <input placeholder="Дата обжалуемого акта" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <input placeholder="Заявитель" value={judicialData.applicant} onChange={e => handleJudicialChange('applicant', e.target.value)} />
          <textarea rows="3" placeholder="Основания для кассации" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'supervisory_complaint') {
      return (
        <>
          <input placeholder="Номер дела" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <input placeholder="Судебные акты" value={judicialData.lower_courts} onChange={e => handleJudicialChange('lower_courts', e.target.value)} />
          <input placeholder="Заявитель" value={judicialData.applicant} onChange={e => handleJudicialChange('applicant', e.target.value)} />
          <textarea rows="3" placeholder="Основания для пересмотра" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'private_complaint') {
      return (
        <>
          <input placeholder="Номер дела" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <input placeholder="Суд, вынесший определение" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Дата определения" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <input placeholder="Заявитель" value={judicialData.applicant} onChange={e => handleJudicialChange('applicant', e.target.value)} />
          <textarea rows="3" placeholder="Что обжалуется" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_civil_general') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <textarea rows="3" placeholder="Суть иска / требования" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'admin_claim_kas') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Административный истец" value={judicialData.admin_plaintiff} onChange={e => handleJudicialChange('admin_plaintiff', e.target.value)} />
          <input placeholder="Административный ответчик" value={judicialData.admin_defendant} onChange={e => handleJudicialChange('admin_defendant', e.target.value)} />
          <input placeholder="Дата решения" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <textarea rows="3" placeholder="Оспариваемое решение / действие" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'appeal_admin_procedure') {
      return (
        <>
          <input placeholder="Номер дела" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <input placeholder="Суд первой инстанции" value={judicialData.first_court_name} onChange={e => handleJudicialChange('first_court_name', e.target.value)} />
          <input placeholder="Апелляционный суд" value={judicialData.appeal_court_name} onChange={e => handleJudicialChange('appeal_court_name', e.target.value)} />
          <input placeholder="Дата решения" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <input placeholder="Административный истец" value={judicialData.admin_plaintiff} onChange={e => handleJudicialChange('admin_plaintiff', e.target.value)} />
          <input placeholder="Административный ответчик" value={judicialData.admin_defendant} onChange={e => handleJudicialChange('admin_defendant', e.target.value)} />
          <textarea rows="3" placeholder="Основания обжалования" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'complaint_koap') {
      return (
        <>
          <input placeholder="Номер постановления" value={judicialData.resolution_number} onChange={e => handleJudicialChange('resolution_number', e.target.value)} />
          <input placeholder="Дата вынесения" value={judicialData.resolution_date} onChange={e => handleJudicialChange('resolution_date', e.target.value)} />
          <input placeholder="Орган / суд" value={judicialData.authority_name} onChange={e => handleJudicialChange('authority_name', e.target.value)} />
          <input placeholder="Лицо, привлекаемое к ответственности" value={judicialData.person_name} onChange={e => handleJudicialChange('person_name', e.target.value)} />
          <input placeholder="Статья КоАП" value={judicialData.article} onChange={e => handleJudicialChange('article', e.target.value)} />
          <textarea rows="3" placeholder="Основания жалобы" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_divorce') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="Дата регистрации брака" value={judicialData.marriage_date} onChange={e => handleJudicialChange('marriage_date', e.target.value)} />
          <textarea rows="3" placeholder="Основания иска" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_alimony') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="Лицо, на которое взыскиваются алименты" value={judicialData.applicant} onChange={e => handleJudicialChange('applicant', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_parental_rights') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="Данные о детях" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_labor_wage') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец (работник)" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик (работодатель)" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="Период задолженности" value={judicialData.wage_period} onChange={e => handleJudicialChange('wage_period', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_labor_reinstatement') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец (работник)" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик (работодатель)" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="Дата увольнения" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_housing') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="Адрес жилого помещения" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_land') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="Кадастровый номер / адрес" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_consumer') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="Товар / услуга" value={judicialData.product_name} onChange={e => handleJudicialChange('product_name', e.target.value)} />
          <input placeholder="Стоимость" value={judicialData.amount} onChange={e => handleJudicialChange('amount', e.target.value)} />
          <input placeholder="Недостаток" value={judicialData.defect_description} onChange={e => handleJudicialChange('defect_description', e.target.value)} />
          <input placeholder="Моральный вред" value={judicialData.moral_damage} onChange={e => handleJudicialChange('moral_damage', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_tax') {
      return (
        <>
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Налоговый орган" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="Номер решения" value={judicialData.resolution_number} onChange={e => handleJudicialChange('resolution_number', e.target.value)} />
          <input placeholder="Дата решения" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'claim_arbitration') {
      return (
        <>
          <input placeholder="Арбитражный суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Истец" value={judicialData.plaintiff_name} onChange={e => handleJudicialChange('plaintiff_name', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <input placeholder="ИНН" value={judicialData.applicant} onChange={e => handleJudicialChange('applicant', e.target.value)} />
          <input placeholder="Сумма" value={judicialData.amount} onChange={e => handleJudicialChange('amount', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'appeal_arbitration') {
      return (
        <>
          <input placeholder="Номер дела" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <input placeholder="Суд первой инстанции" value={judicialData.first_court_name} onChange={e => handleJudicialChange('first_court_name', e.target.value)} />
          <input placeholder="Апелляционный суд" value={judicialData.appeal_court_name} onChange={e => handleJudicialChange('appeal_court_name', e.target.value)} />
          <input placeholder="Дата решения" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'cassation_arbitration') {
      return (
        <>
          <input placeholder="Номер дела" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <input placeholder="Суды, прошедшие инстанции" value={judicialData.lower_courts} onChange={e => handleJudicialChange('lower_courts', e.target.value)} />
          <input placeholder="Суд кассационной инстанции" value={judicialData.cassation_court} onChange={e => handleJudicialChange('cassation_court', e.target.value)} />
          <input placeholder="Дата обжалуемого акта" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <textarea rows="3" placeholder="Основания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'application_for_court_order') {
      return (
        <>
          <input placeholder="Мировой суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Взыскатель" value={judicialData.claimant_name} onChange={e => handleJudicialChange('claimant_name', e.target.value)} />
          <input placeholder="Должник" value={judicialData.debtor_name} onChange={e => handleJudicialChange('debtor_name', e.target.value)} />
          <input placeholder="Сумма требования" value={judicialData.amount} onChange={e => handleJudicialChange('amount', e.target.value)} />
          <textarea rows="3" placeholder="Основания взыскания" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    if (sub === 'application_to_cancel_default_judgment') {
      return (
        <>
          <input placeholder="Номер дела" value={judicialData.case_number} onChange={e => handleJudicialChange('case_number', e.target.value)} />
          <input placeholder="Суд" value={judicialData.court_name} onChange={e => handleJudicialChange('court_name', e.target.value)} />
          <input placeholder="Дата заочного решения" value={judicialData.decision_date} onChange={e => handleJudicialChange('decision_date', e.target.value)} />
          <input placeholder="Ответчик" value={judicialData.defendant_name} onChange={e => handleJudicialChange('defendant_name', e.target.value)} />
          <textarea rows="3" placeholder="Причины пропуска срока" value={judicialData.grounds} onChange={e => handleJudicialChange('grounds', e.target.value)} />
        </>
      );
    }
    return null;
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>⚖️ LegalHelp — Юридический AI-ассистент + составление документов</h2>
      </div>

      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            <div className="message-content">{msg.text}</div>
            {msg.sender === 'bot' && (
              <div className="message-actions">
                <button onClick={() => copyToClipboard(msg.text)}>📋 Копировать</button>
                <button onClick={() => downloadAsTxt(msg.text, `response_${idx}`)}>📥 Скачать .txt</button>
              </div>
            )}
          </div>
        ))}
        {isLoading && <div className="message bot"><div className="message-content">Генерирую ответ...</div></div>}
      </div>

      <div className="input-area">
        <div className="file-buttons">
          <button onClick={triggerFileInput} disabled={isLoading} className="attach-button" title="Выбрать файл">📁</button>
          <input type="file" ref={fileInputRef} onChange={handleFileSelect} style={{ display: 'none' }} accept=".pdf,.png,.jpg,.jpeg" />
          <button onClick={triggerCameraInput} disabled={isLoading} className="attach-button" title="Сделать фото">📸</button>
          <input type="file" ref={cameraInputRef} onChange={handleFileSelect} style={{ display: 'none' }} accept="image/*" capture="environment" />
          {selectedFile && (
            <div className="selected-file-info">
              📎 Файл: {selectedFile.name.length > 30 ? selectedFile.name.substring(0, 27) + '...' : selectedFile.name}
              <button onClick={clearSelectedFile} className="clear-file">✖</button>
            </div>
          )}
        </div>

        <select value={docType} onChange={(e) => setDocType(e.target.value)} disabled={isLoading}>
          <option value="other">Общий вопрос</option>
          <option value="judicial_review">Судебный документ (жалоба, возражение)</option>
        </select>

        <textarea
          rows="3"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Введите ваш вопрос или опишите ситуацию..."
          disabled={isLoading}
        />

        <button onClick={sendMessage} disabled={isLoading}>Отправить</button>

        {docType === 'judicial_review' && (
          <div className="judicial-details">
            <label>Тип документа:
              <select value={judicialData.subtype} onChange={e => handleJudicialChange('subtype', e.target.value)}>
                <optgroup label="Гражданский процесс (ГПК)">
                  <option value="objection_to_court_order">Возражение на судебный приказ</option>
                  <option value="appeal_civil">Апелляционная жалоба (гражданское дело)</option>
                  <option value="cassation_civil">Кассационная жалоба (ГПК)</option>
                  <option value="supervisory_complaint">Надзорная жалоба (ГПК)</option>
                  <option value="private_complaint">Частная жалоба на определение суда</option>
                  <option value="claim_civil_general">Исковое заявление (общее)</option>
                  <option value="application_for_court_order">Заявление о выдаче судебного приказа</option>
                  <option value="application_to_cancel_default_judgment">Заявление об отмене заочного решения</option>
                </optgroup>
                <optgroup label="Административное судопроизводство (КАС)">
                  <option value="admin_claim_kas">Административное исковое заявление (КАС)</option>
                  <option value="appeal_admin_procedure">Апелляционная жалоба (КАС)</option>
                  <option value="cassation_civil">Кассационная жалоба (КАС)</option>
                </optgroup>
                <optgroup label="Дела об административных правонарушениях (КоАП)">
                  <option value="complaint_koap">Жалоба на постановление по делу об АП</option>
                </optgroup>
                <optgroup label="Семейное право (СК)">
                  <option value="claim_divorce">Исковое заявление о расторжении брака</option>
                  <option value="claim_alimony">Исковое заявление о взыскании алиментов</option>
                  <option value="claim_parental_rights">Исковое заявление о лишении родительских прав</option>
                </optgroup>
                <optgroup label="Трудовое право (ТК)">
                  <option value="claim_labor_wage">Исковое заявление о взыскании зарплаты</option>
                  <option value="claim_labor_reinstatement">Исковое заявление о восстановлении на работе</option>
                </optgroup>
                <optgroup label="Жилищное право (ЖК)">
                  <option value="claim_housing">Исковое заявление по жилищному спору</option>
                </optgroup>
                <optgroup label="Земельное право (ЗК)">
                  <option value="claim_land">Исковое заявление по земельному спору</option>
                </optgroup>
                <optgroup label="Защита прав потребителей">
                  <option value="claim_consumer">Исковое заявление о защите прав потребителей</option>
                </optgroup>
                <optgroup label="Налоговое право">
                  <option value="claim_tax">Исковое заявление по налоговому спору</option>
                </optgroup>
                <optgroup label="Арбитражный процесс (АПК)">
                  <option value="claim_arbitration">Исковое заявление в арбитражный суд</option>
                  <option value="appeal_arbitration">Апелляционная жалоба (АПК)</option>
                  <option value="cassation_arbitration">Кассационная жалоба (АПК)</option>
                </optgroup>
              </select>
            </label>
            <div className="fields-grid">
              {renderJudicialFields()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;