import { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { PartiesManager } from './PartiesManager';
import { DOC_TYPE_CONFIG, DOC_TEMPLATES_GROUPED } from './docTypeConfig';
import { detectDocumentType } from '../../utils/documentTypeDetector';

export const GeneratorForm = () => {
  const { generateDocument, isGenerating, generatedDoc, docQuery, setDocQuery, prefillData, clearPrefillData } = useApp();
  const [selectedType, setSelectedType] = useState('');
  const [fields, setFields] = useState({});
  const [parties, setParties] = useState([]);
  const [status, setStatus] = useState('');
  const [statusType, setStatusType] = useState('');
  
  const [step3Data, setStep3Data] = useState({});
  
  // Применяем prefillData из контекста (при переходе из чата)
  useEffect(() => {
    if (prefillData) {
      // Если тип документа не указан — определяем автоматически
      if (!prefillData.docType && prefillData.docQuery) {
        const detected = detectDocumentType(prefillData.docQuery);
        setSelectedType(detected.docType);
        setStatus(`🔍 Автоматически определён тип: ${DOC_TYPE_CONFIG[detected.docType]?.label || detected.docType} (уверенность: ${(detected.confidence * 100).toFixed(0)}%)`);
        setStatusType('info');
      } else if (prefillData.docType) {
        setSelectedType(prefillData.docType);
        setStatus('Данные из чата подставлены автоматически');
        setStatusType('info');
      }
      
      if (prefillData.parties) {
        setParties(prefillData.parties);
      }
      if (prefillData.step3Data) {
        setStep3Data(prefillData.step3Data);
      }
      if (prefillData.docQuery) {
        setDocQuery(prefillData.docQuery);
        // Подставляем описание в factual_circumstances
        setStep3Data(prev => ({ ...prev, factual_circumstances: prefillData.docQuery }));
      }
      
      clearPrefillData();
    }
  }, [prefillData]);
  
  // При смене типа документа — сбрасываем step3Data, но сохраняем parties
  useEffect(() => {
    if (selectedType) {
      setStep3Data({});
    }
  }, [selectedType]);
  
  const currentConfig = DOC_TYPE_CONFIG[selectedType] || {};
  const step3Fields = currentConfig.step3Fields || {};
  
  const formatParties = () => {
    if (parties.length === 0) return { plaintiffs: '', defendants: '', third_parties: '' };
    
    const result = {};
    Object.keys(currentConfig.parties || {}).forEach(roleKey => {
      const roleParties = parties.filter(p => p.type === roleKey);
      if (roleParties.length > 0) {
        result[roleKey] = roleParties.map(p => {
          if (p.entity_type === 'individual') {
            let info = p.name || '___________';
            if (p.birth_date) info += ', ' + new Date(p.birth_date).toLocaleDateString('ru-RU');
            if (p.address) info += ', адрес: ' + p.address;
            if (p.phone) info += ', тел: ' + p.phone;
            if (p.passport_series && p.passport_number) {
              info += ', паспорт: ' + p.passport_series + ' ' + p.passport_number;
              if (p.passport_issued_by) info += ', выдан ' + p.passport_issued_by;
              if (p.passport_date) info += ' ' + new Date(p.passport_date).toLocaleDateString('ru-RU');
            }
            if (p.snils) info += ', СНИЛС: ' + p.snils;
            return info;
          } else {
            let info = p.name || '___________';
            if (p.inn) info += ', ИНН: ' + p.inn;
            if (p.ogrn) info += ', ОГРН: ' + p.ogrn;
            if (p.address) info += ', адрес: ' + p.address;
            if (p.director_name) info += ', в лице ' + p.director_name;
            return info;
          }
        }).join('\n');
      }
    });
    
    return result;
  };
  
  const handleGenerate = async () => {
    if (!selectedType) {
      setStatus('Выберите тип документа');
      setStatusType('error');
      return;
    }
    
    setStatus('Генерирую документ...');
    setStatusType('info');
    
    const partiesFormatted = formatParties();
    
    const userFields = {
      ...fields,
      ...step3Data,
      ...partiesFormatted
    };
    
    Object.keys(userFields).forEach(key => {
      if (!userFields[key]) delete userFields[key];
    });
    
    const query = step3Data.factual_circumstances || docQuery || 'Составь документ типа ' + selectedType;
    const result = await generateDocument(query, selectedType, userFields);
    
    if (result?.success) {
      setStatus('Документ успешно сгенерирован!');
      setStatusType('success');
    } else {
      setStatus('Ошибка: ' + (result?.error || 'Не удалось сгенерировать документ'));
      setStatusType('error');
    }
  };
  
  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '2rem', maxWidth: '1100px', margin: '0 auto', width: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <div style={{ fontSize: '2.5rem' }}>📄</div>
        <h2 style={{ fontSize: '1.8rem', marginBottom: '0.5rem', background: 'linear-gradient(90deg, #6366f1, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Генерация юридических документов
        </h2>
        <p style={{ color: 'var(--text-secondary)' }}>Заполните все поля для создания документа</p>
      </div>
      
      <div style={{ marginBottom: '2rem', padding: '1.5rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px' }}>
        <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)', fontSize: '1.1rem' }}>📋 Шаг 1. Выберите тип документа</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '400px', overflowY: 'auto', paddingRight: '0.5rem' }}>
          {Object.entries(DOC_TEMPLATES_GROUPED).map(([category, templates]) => (
            <div key={category}>
              <div style={{ fontWeight: '600', color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '0.95rem', padding: '0.25rem 0', borderBottom: '1px solid var(--border)' }}>
                {category}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                {templates.map(t => (
                  <button
                    key={t.value}
                    onClick={() => setSelectedType(t.value)}
                    style={{
                      padding: '0.5rem 0.9rem',
                      background: selectedType === t.value ? 'var(--primary)' : 'var(--bg-tertiary)',
                      color: selectedType === t.value ? 'white' : 'var(--text-primary)',
                      border: '1px solid ' + (selectedType === t.value ? 'var(--primary)' : 'var(--border)'),
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '0.85rem'
                    }}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {selectedType && (
        <div style={{ marginBottom: '2rem', padding: '1.5rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px' }}>
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)', fontSize: '1.1rem' }}>👥 Шаг 2. Участники процесса</h3>
          <PartiesManager parties={parties} setParties={setParties} docType={selectedType} />
        </div>
      )}
      
      {selectedType && Object.keys(step3Fields).length > 0 && (
        <div style={{ marginBottom: '2rem', padding: '1.5rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px' }}>
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)', fontSize: '1.1rem' }}>📝 Шаг 3. {currentConfig.step3Title || 'Содержание документа'}</h3>
          
          {Object.entries(step3Fields).map(([key, fieldConfig]) => (
            <div key={key} style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginBottom: '1rem' }}>
              <label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: '500' }}>{fieldConfig.label}</label>
              {fieldConfig.type === 'textarea' ? (
                <textarea
                  value={step3Data[key] || ''}
                  onChange={(e) => setStep3Data({ ...step3Data, [key]: e.target.value })}
                  placeholder={fieldConfig.placeholder || ''}
                  rows={fieldConfig.rows || 3}
                  style={{ padding: '0.65rem 0.9rem', background: 'var(--bg-tertiary)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)', fontSize: '0.95rem', fontFamily: 'inherit', resize: 'vertical' }}
                />
              ) : (
                <input
                  type={fieldConfig.type || 'text'}
                  value={step3Data[key] || ''}
                  onChange={(e) => setStep3Data({ ...step3Data, [key]: e.target.value })}
                  placeholder={fieldConfig.placeholder || ''}
                  style={{ padding: '0.65rem 0.9rem', background: 'var(--bg-tertiary)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)', fontSize: '0.95rem' }}
                />
              )}
            </div>
          ))}
        </div>
      )}
      
      <button onClick={handleGenerate} disabled={isGenerating || !selectedType} style={{ width: '100%', padding: '1rem 2rem', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', border: 'none', borderRadius: '12px', color: 'white', fontSize: '1.05rem', fontWeight: '600', cursor: 'pointer', marginTop: '1rem', opacity: (isGenerating || !selectedType) ? '0.5' : '1' }}>
        {isGenerating ? '⏳ Генерирую...' : '✨ Сгенерировать документ'}
      </button>
      
      {status && (
        <div style={{ padding: '1rem', borderRadius: '8px', marginTop: '1rem', fontWeight: '500', background: statusType === 'success' ? 'rgba(16, 185, 129, 0.15)' : statusType === 'error' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(99, 102, 241, 0.15)', borderLeft: '4px solid ' + (statusType === 'success' ? '#10b981' : statusType === 'error' ? '#ef4444' : '#6366f1'), color: statusType === 'success' ? '#10b981' : statusType === 'error' ? '#ef4444' : '#a5b4fc' }}>
          {status}
        </div>
      )}
      
      {generatedDoc && (
        <div style={{ marginTop: '2rem', padding: '1.5rem', background: 'var(--bg-secondary)', border: '1px solid #10b981', borderRadius: '12px' }}>
          <h3 style={{ color: '#10b981', marginBottom: '0.5rem' }}>✅ Документ: {generatedDoc.doc_type}</h3>
          <p>Уверенность: {(generatedDoc.confidence * 100).toFixed(0)}%</p>
          <pre style={{ background: 'var(--bg-primary)', padding: '1rem', borderRadius: '8px', overflow: 'auto', maxHeight: '400px', color: 'var(--text-primary)', fontFamily: 'Courier New, monospace', fontSize: '0.9rem', lineHeight: '1.6', whiteSpace: 'pre-wrap', margin: '1rem 0' }}>
            {generatedDoc.filled_text}
          </pre>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            {generatedDoc.docx_url && (
              <a href={'http://localhost:8000' + generatedDoc.docx_url} download style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', color: 'white', textDecoration: 'none', fontWeight: '600', background: 'linear-gradient(135deg, #2563eb, #3b82f6)', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                📥 Скачать DOCX
              </a>
            )}
            {generatedDoc.pdf_url && (
              <a href={'http://localhost:8000' + generatedDoc.pdf_url} download style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', color: 'white', textDecoration: 'none', fontWeight: '600', background: 'linear-gradient(135deg, #dc2626, #ef4444)', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                📥 Скачать PDF
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
