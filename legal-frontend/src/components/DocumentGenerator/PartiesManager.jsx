import { useState } from 'react';
import { DOC_TYPE_CONFIG } from './docTypeConfig';

export const PartiesManager = ({ parties, setParties, docType }) => {
  const config = DOC_TYPE_CONFIG[docType] || {};
  const availableRoles = Object.entries(config.parties || {});
  
  const [selectedRole, setSelectedRole] = useState(availableRoles[0]?.[0] || 'plaintiff');
  
  const addParty = () => {
    const roleConfig = config.parties?.[selectedRole] || { label: 'Участник', icon: '👤' };
    const newParty = {
      id: Date.now(),
      type: selectedRole,
      typeLabel: roleConfig.label,
      entity_type: 'individual',
      name: '',
      address: '',
      phone: '',
      email: '',
      // Для физических лиц
      passport_series: '',
      passport_number: '',
      passport_issued_by: '',
      passport_date: '',
      snils: '',
      birth_date: '',
      // Для юридических лиц
      inn: '',
      ogrn: '',
      kpp: '',
      legal_address: '',
      director_name: ''
    };
    setParties([...parties, newParty]);
  };
  
  const updateParty = (id, field, value) => {
    setParties(parties.map(p => p.id === id ? { ...p, [field]: value } : p));
  };
  
  const removeParty = (id) => {
    setParties(parties.filter(p => p.id !== id));
  };
  
  const renderPartyCard = (party) => {
    const roleConfig = config.parties?.[party.type] || { label: 'Участник', icon: '👤' };
    
    return (
      <div key={party.id} style={{ padding: '1rem', background: 'var(--bg-tertiary)', border: '1px solid var(--border)', borderRadius: '8px', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '1.2rem' }}>{roleConfig.icon}</span>
            <select
              value={party.type}
              onChange={(e) => updateParty(party.id, 'type', e.target.value)}
              style={{ padding: '0.4rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }}
            >
              {availableRoles.map(([key, cfg]) => (
                <option key={key} value={key}>{cfg.label}</option>
              ))}
            </select>
            
            <select
              value={party.entity_type}
              onChange={(e) => updateParty(party.id, 'entity_type', e.target.value)}
              style={{ padding: '0.4rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }}
            >
              <option value="individual">Физическое лицо</option>
              <option value="legal">Юридическое лицо</option>
            </select>
          </div>
          <button
            onClick={() => removeParty(party.id)}
            style={{ background: 'rgba(239, 68, 68, 0.1)', border: 'none', color: '#ef4444', padding: '0.4rem 0.8rem', borderRadius: '6px', cursor: 'pointer', fontSize: '0.9rem' }}
          >
            Удалить
          </button>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>
              {party.entity_type === 'individual' ? '👤 ФИО' : '🏢 Наименование'}
            </label>
            <input type="text" value={party.name} onChange={(e) => updateParty(party.id, 'name', e.target.value)}
              placeholder={party.entity_type === 'individual' ? 'Иванов Иван Иванович' : 'ООО "Ромашка"'}
              style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
          </div>
          
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>📍 Адрес</label>
            <input type="text" value={party.address} onChange={(e) => updateParty(party.id, 'address', e.target.value)}
              placeholder="г. Москва, ул. Ленина, д. 1, кв. 1"
              style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
          </div>
          
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>📞 Телефон</label>
            <input type="tel" value={party.phone} onChange={(e) => updateParty(party.id, 'phone', e.target.value)}
              placeholder="+7 (999) 123-45-67"
              style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
          </div>
          
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>📧 Email</label>
            <input type="email" value={party.email} onChange={(e) => updateParty(party.id, 'email', e.target.value)}
              placeholder="example@mail.ru"
              style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
          </div>
        </div>
        
        {party.entity_type === 'individual' && (
          <div style={{ padding: '0.75rem', background: 'rgba(99, 102, 241, 0.05)', borderRadius: '6px', marginTop: '0.75rem' }}>
            <div style={{ fontSize: '0.9rem', color: 'var(--primary)', fontWeight: '600', marginBottom: '0.75rem' }}>📄 Паспортные данные</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>🎂 Дата рождения</label>
                <input type="date" value={party.birth_date} onChange={(e) => updateParty(party.id, 'birth_date', e.target.value)}
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>🔢 Серия паспорта</label>
                <input type="text" value={party.passport_series} onChange={(e) => updateParty(party.id, 'passport_series', e.target.value)}
                  placeholder="4510" maxLength="4"
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>🔢 Номер паспорта</label>
                <input type="text" value={party.passport_number} onChange={(e) => updateParty(party.id, 'passport_number', e.target.value)}
                  placeholder="123456" maxLength="6"
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>🏛️ Кем выдан</label>
                <input type="text" value={party.passport_issued_by} onChange={(e) => updateParty(party.id, 'passport_issued_by', e.target.value)}
                  placeholder="ОВД района Тверской г. Москвы"
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>📅 Дата выдачи</label>
                <input type="date" value={party.passport_date} onChange={(e) => updateParty(party.id, 'passport_date', e.target.value)}
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>🆔 СНИЛС</label>
                <input type="text" value={party.snils} onChange={(e) => updateParty(party.id, 'snils', e.target.value)}
                  placeholder="123-456-789 00"
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
            </div>
          </div>
        )}
        
        {party.entity_type === 'legal' && (
          <div style={{ padding: '0.75rem', background: 'rgba(16, 185, 129, 0.05)', borderRadius: '6px', marginTop: '0.75rem' }}>
            <div style={{ fontSize: '0.9rem', color: '#10b981', fontWeight: '600', marginBottom: '0.75rem' }}>🏢 Реквизиты юридического лица</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>🔢 ИНН</label>
                <input type="text" value={party.inn} onChange={(e) => updateParty(party.id, 'inn', e.target.value)}
                  placeholder="7707083893" maxLength="12"
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>🔢 ОГРН</label>
                <input type="text" value={party.ogrn} onChange={(e) => updateParty(party.id, 'ogrn', e.target.value)}
                  placeholder="1027700132195" maxLength="13"
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>🔢 КПП</label>
                <input type="text" value={party.kpp} onChange={(e) => updateParty(party.id, 'kpp', e.target.value)}
                  placeholder="770701001" maxLength="9"
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>👤 Руководитель</label>
                <input type="text" value={party.director_name} onChange={(e) => updateParty(party.id, 'director_name', e.target.value)}
                  placeholder="Иванов Иван Иванович"
                  style={{ width: '100%', padding: '0.6rem 0.8rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };
  
  if (!docType || availableRoles.length === 0) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>👥</div>
        <p>Сначала выберите тип документа</p>
      </div>
    );
  }
  
  // Группируем стороны по ролям
  const partiesByRole = availableRoles.map(([roleKey, roleConfig]) => {
    const roleParties = parties.filter(p => p.type === roleKey);
    return { roleKey, roleConfig, parties: roleParties };
  }).filter(g => g.parties.length > 0);
  
  return (
    <div>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <select
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value)}
          style={{ padding: '0.5rem 0.8rem', background: 'var(--bg-tertiary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }}
        >
          {availableRoles.map(([key, cfg]) => (
            <option key={key} value={key}>{cfg.icon} {cfg.label}</option>
          ))}
        </select>
        <button
          onClick={addParty}
          style={{ padding: '0.5rem 1rem', background: 'var(--primary)', border: 'none', borderRadius: '6px', color: 'white', cursor: 'pointer', fontSize: '0.9rem', fontWeight: '500' }}
        >
          ➕ Добавить участника
        </button>
      </div>
      
      {partiesByRole.map(({ roleKey, roleConfig, parties: roleParties }) => (
        <div key={roleKey} style={{ marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.9rem', color: 'var(--primary)', fontWeight: '600', marginBottom: '0.5rem' }}>
            {roleConfig.icon} {roleConfig.label} ({roleParties.length})
          </div>
          {roleParties.map(renderPartyCard)}
        </div>
      ))}
      
      {parties.length === 0 && (
        <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>👥</div>
          <p>Добавьте участников процесса</p>
        </div>
      )}
    </div>
  );
};
