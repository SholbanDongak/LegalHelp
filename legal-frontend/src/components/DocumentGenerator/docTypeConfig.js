// Конфигурация типов документов: роли, заголовки, поля
export const DOC_TYPE_CONFIG = {
  // ============ ГПК: ИСКОВОЕ ПРОИЗВОДСТВО ============
  'claim_civil_general': {
    category: 'ГПК: Исковое производство',
    label: 'Исковое заявление (общее)',
    parties: {
      plaintiff: { label: 'Истец', icon: '👤' },
      defendant: { label: 'Ответчик', icon: '🏢' },
      third_party: { label: 'Третье лицо', icon: '👥' }
    },
    step3Title: 'Содержание искового заявления',
    step3Fields: {
      claim_title: { label: '📌 Наименование иска', placeholder: 'о взыскании суммы долга по договору займа' },
      factual_circumstances: { label: '📖 Фактические обстоятельства', placeholder: 'Подробно опишите: что произошло, когда, кто участвовал...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование (ссылки на законы)', placeholder: 'ст. 309, 310, 807, 810 ГК РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Предмет иска (требования)', placeholder: 'Взыскать с Ответчика в пользу Истца сумму долга...', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '3200', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Копия искового заявления...', type: 'textarea', rows: 4 }
    }
  },
  'application_for_court_order': {
    category: 'ГПК: Приказное производство',
    label: 'Заявление о судебном приказе',
    parties: {
      creditor: { label: 'Взыскатель', icon: '👤' },
      debtor: { label: 'Должник', icon: '🏢' }
    },
    step3Title: 'Обоснование требования о выдаче судебного приказа',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'о выдаче судебного приказа о взыскании денежных средств' },
      factual_circumstances: { label: '📖 Обстоятельства возникновения долга', placeholder: 'Между взыскателем и должником заключён...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'ст. 121, 122, 124 ГПК РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Требование', placeholder: 'Выдать судебный приказ о взыскании с должника...', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб., 50% от обычной)', placeholder: '1600', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Документы, подтверждающие требование...', type: 'textarea', rows: 4 }
    }
  },
  'objection_to_court_order': {
    category: 'ГПК: Приказное производство',
    label: 'Возражение на судебный приказ',
    parties: {
      debtor: { label: 'Должник (заявитель)', icon: '👤' },
      creditor: { label: 'Взыскатель', icon: '🏢' }
    },
    step3Title: 'Основания возражения against судебного приказа',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'Возражение относительно вынесения судебного приказа' },
      factual_circumstances: { label: '📖 Обстоятельства дела', placeholder: 'Мировым судьёй вынесен судебный приказ №... от...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'ст. 128, 129 ГПК РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Отменить судебный приказ мирового судьи...', type: 'textarea', rows: 3 },
      attachments: { label: '📎 Приложения', placeholder: '1. Копия судебного приказа...', type: 'textarea', rows: 4 }
    }
  },
  'appeal_civil': {
    category: 'ГПК: Апелляция',
    label: 'Апелляционная жалоба (ГПК)',
    parties: {
      applicant: { label: 'Заявитель (лицо, подающее жалобу)', icon: '👤' },
      other_parties: { label: 'Другие участники дела', icon: '👥' }
    },
    step3Title: 'Доводы апелляционной жалобы',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'Апелляционная жалоба на решение суда' },
      factual_circumstances: { label: '📖 Обстоятельства дела и содержание решения', placeholder: 'Решением суда от... по делу №... отказано в...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Доводы жалобы (несоответствие выводов суда обстоятельствам дела)', placeholder: 'ст. 320, 327.1, 328 ГПК РФ', type: 'textarea', rows: 3 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Отменить решение суда первой инстанции и принять новое...', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '300 (для физлиц)', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Копия обжалуемого решения...', type: 'textarea', rows: 4 }
    }
  },
  'cassation_civil': {
    category: 'ГПК: Кассация',
    label: 'Кассационная жалоба (ГПК)',
    parties: {
      applicant: { label: 'Заявитель', icon: '👤' },
      other_parties: { label: 'Другие участники дела', icon: '👥' }
    },
    step3Title: 'Доводы кассационной жалобы',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'Кассационная жалоба' },
      factual_circumstances: { label: '📖 История дела', placeholder: 'Решением суда от... постановлением апелляционной инстанции от...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Доводы (существенное нарушение норм материального/процессуального права)', placeholder: 'ст. 379.7, 390 ГПК РФ', type: 'textarea', rows: 3 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Отменить решение суда и постановление апелляции...', type: 'textarea', rows: 3 },
      attachments: { label: '📎 Приложения', placeholder: '1. Заверенные копии судебных актов...', type: 'textarea', rows: 4 }
    }
  },
  // ============ КАС: АДМИНИСТРАТИВНОЕ СУДОПРОИЗВОДСТВО ============
  'admin_claim_kas': {
    category: 'КАС: Административное исковое производство',
    label: 'Административное исковое заявление',
    parties: {
      plaintiff: { label: 'Административный истец', icon: '👤' },
      defendant: { label: 'Административный ответчик (орган/должностное лицо)', icon: '🏛️' },
      third_party: { label: 'Заинтересованное лицо', icon: '👥' }
    },
    step3Title: 'Содержание административного искового заявления',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'Об оспаривании решения/действия органа власти' },
      factual_circumstances: { label: '📖 Обстоятельства дела', placeholder: 'Каким решением/действием нарушены права...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'ст. 218, 219, 220 КАС РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Требования', placeholder: 'Признать незаконным решение/действие...', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '300 (для физлиц)', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Копия оспариваемого решения...', type: 'textarea', rows: 4 }
    }
  },
  'appeal_admin_procedure': {
    category: 'КАС: Апелляция',
    label: 'Апелляционная жалоба (КАС)',
    parties: {
      applicant: { label: 'Заявитель', icon: '👤' },
      other_parties: { label: 'Другие участники', icon: '👥' }
    },
    step3Title: 'Доводы апелляционной жалобы (КАС)',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'Апелляционная жалоба на решение суда' },
      factual_circumstances: { label: '📖 Обстоятельства дела', placeholder: 'Решением суда от... по административному делу №...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Доводы жалобы', placeholder: 'ст. 300, 301, 302, 303, 310 КАС РФ', type: 'textarea', rows: 3 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Отменить решение суда первой инстанции...', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '150', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Копия обжалуемого решения...', type: 'textarea', rows: 4 }
    }
  },
  'cassation_kas': {
    category: 'КАС: Кассация',
    label: 'Кассационная жалоба (КАС)',
    parties: {
      applicant: { label: 'Заявитель', icon: '👤' },
      other_parties: { label: 'Другие участники', icon: '👥' }
    },
    step3Title: 'Доводы кассационной жалобы (КАС)',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'Кассационная жалоба' },
      factual_circumstances: { label: '📖 История дела', placeholder: 'Решением суда от... апелляционным постановлением от...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Доводы', placeholder: 'ст. 376, 379 КАС РФ', type: 'textarea', rows: 3 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Отменить судебные акты...', type: 'textarea', rows: 3 },
      attachments: { label: '📎 Приложения', placeholder: '1. Заверенные копии судебных актов...', type: 'textarea', rows: 4 }
    }
  },
  // ============ КоАП ============
  'complaint_koap': {
    category: 'КоАП: Жалоба на постановление',
    label: 'Жалоба на постановление по КоАП',
    parties: {
      applicant: { label: 'Заявитель (лицо, в отношении которого возбуждено дело)', icon: '👤' },
      victim: { label: 'Потерпевший', icon: '👥' },
      official: { label: 'Должностное лицо (орган, вынесший постановление)', icon: '🏛️' }
    },
    step3Title: 'Доводы жалобы на постановление',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'Жалоба на постановление по делу об административном правонарушении' },
      factual_circumstances: { label: '📖 Обстоятельства дела', placeholder: 'Постановлением №... от... по делу №... привлечён к ответственности по ст. ... КоАП РФ', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Доводы жалобы', placeholder: 'ст. 30.1, 30.2, 30.7 КоАП РФ', type: 'textarea', rows: 3 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Отменить постановление и прекратить производство по делу', type: 'textarea', rows: 3 },
      attachments: { label: '📎 Приложения', placeholder: '1. Копия обжалуемого постановления...', type: 'textarea', rows: 4 }
    }
  },
  // ============ ОСОБОЕ ПРОИЗВОДСТВО ============
  'special_proceeding_fact': {
    category: 'Особое производство',
    label: 'Заявление об установлении факта, имеющего юридическое значение',
    parties: {
      applicant: { label: 'Заявитель', icon: '👤' },
      interested: { label: 'Заинтересованное лицо', icon: '👥' }
    },
    step3Title: 'Обоснование необходимости установления юридического факта',
    step3Fields: {
      claim_title: { label: '📌 Какой факт необходимо установить', placeholder: 'Об установлении факта родственных отношений / принадлежности документов / нахождения на иждивении' },
      factual_circumstances: { label: '📖 Обстоятельства, подтверждающие факт', placeholder: 'Для получения наследства / пенсии / иных прав необходимо установить факт...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'ст. 264, 265, 266, 267 ГПК РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Цель установления факта', placeholder: 'Факт необходим для...', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '300', type: 'number' },
      attachments: { label: '📎 Приложения (документы, подтверждающие факт)', placeholder: '1. Свидетельства, справки, показания свидетелей...', type: 'textarea', rows: 4 }
    }
  },
  'special_proceeding_other': {
    category: 'Особое производство',
    label: 'Заявление по делу особого производства (иное)',
    parties: {
      applicant: { label: 'Заявитель', icon: '👤' },
      interested: { label: 'Заинтересованное лицо', icon: '👥' }
    },
    step3Title: 'Обоснование заявления',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'Заявление об усыновлении / признании безвестно отсутствующим / ограничении дееспособности' },
      factual_circumstances: { label: '📖 Обстоятельства дела', placeholder: 'Подробно опишите ситуацию...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'Глава 27-38 ГПК РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Прошу', placeholder: '...', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '300', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. ...', type: 'textarea', rows: 4 }
    }
  },
  // ============ СЕМЕЙНОЕ ПРАВО ============
  'claim_divorce': {
    category: 'Семейное право',
    label: 'Исковое заявление о расторжении брака',
    parties: {
      plaintiff: { label: 'Истец (супруг/супруга)', icon: '👤' },
      defendant: { label: 'Ответчик (супруг/супруга)', icon: '👤' },
      third_party: { label: 'Третье лицо (органы опеки и пр.)', icon: '🏛️' }
    },
    step3Title: 'Содержание заявления о расторжении брака',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'О расторжении брака' },
      factual_circumstances: { label: '📖 Обстоятельства семейной жизни', placeholder: 'Брак зарегистрирован... Совместная жизнь прекращена с... Примирение невозможно...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'ст. 21, 22, 23, 24 СК РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Расторгнуть брак между...', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '600', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Свидетельство о браке\n2. Свидетельства о рождении детей...', type: 'textarea', rows: 4 }
    }
  },
  'claim_alimony': {
    category: 'Семейное право',
    label: 'Исковое заявление о взыскании алиментов',
    parties: {
      plaintiff: { label: 'Истец (родитель/опекун)', icon: '👤' },
      defendant: { label: 'Ответчик (родитель)', icon: '👤' },
      third_party: { label: 'Третье лицо', icon: '👥' }
    },
    step3Title: 'Содержание заявления о взыскании алиментов',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'О взыскании алиментов на содержание ребёнка' },
      factual_circumstances: { label: '📖 Обстоятельства дела', placeholder: 'В браке/вне брака родился ребёнок... Ответчик уклоняется от содержания...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'ст. 80, 81, 83 СК РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Взыскать алименты в размере 1/4 (1/3, 1/2) заработка...', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '150', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Свидетельство о рождении ребёнка...', type: 'textarea', rows: 4 }
    }
  },
  // ============ ТРУДОВОЕ ПРАВО ============
  'claim_labor_wage': {
    category: 'Трудовое право',
    label: 'Иск о взыскании заработной платы',
    parties: {
      plaintiff: { label: 'Истец (работник)', icon: '👤' },
      defendant: { label: 'Ответчик (работодатель)', icon: '🏢' },
      third_party: { label: 'Третье лицо', icon: '👥' }
    },
    step3Title: 'Содержание искового заявления о взыскании заработной платы',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'О взыскании заработной платы' },
      factual_circumstances: { label: '📖 Обстоятельства дела', placeholder: 'Работаю у Ответчика с... по настоящее время. Зарплата не выплачивалась за период...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'ст. 136, 236, 392 ТК РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Взыскать задолженность по заработной плате за период... в размере... руб. и компенсацию', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '0 (освобождён по ст. 393 ТК РФ)', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Трудовой договор\n2. Расчёт задолженности...', type: 'textarea', rows: 4 }
    }
  },
  'claim_labor_reinstatement': {
    category: 'Трудовое право',
    label: 'Иск о восстановлении на работе',
    parties: {
      plaintiff: { label: 'Истец (работник)', icon: '👤' },
      defendant: { label: 'Ответчик (работодатель)', icon: '🏢' },
      third_party: { label: 'Третье лицо', icon: '👥' }
    },
    step3Title: 'Содержание искового заявления о восстановлении на работе',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'О восстановлении на работе и взыскании среднего заработка за время вынужденного прогула' },
      factual_circumstances: { label: '📖 Обстоятельства увольнения', placeholder: 'Работал в должности... Приказом №... от... уволен по п.... С увольнением не согласен, т.к....', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'ст. 391, 394 ТК РФ', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Прошу', placeholder: 'Восстановить на работе, взыскать средний заработок за время вынужденного прогула', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '0 (освобождён по ст. 393 ТК РФ)', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Копия приказа об увольнении\n2. Трудовая книжка...', type: 'textarea', rows: 4 }
    }
  },
  // ============ ЗАЩИТА ПРАВ ПОТРЕБИТЕЛЕЙ ============
  'claim_consumer': {
    category: 'Защита прав потребителей',
    label: 'Иск о защите прав потребителей',
    parties: {
      plaintiff: { label: 'Истец (потребитель)', icon: '👤' },
      defendant: { label: 'Ответчик (продавец/исполнитель/изготовитель)', icon: '🏢' },
      third_party: { label: 'Третье лицо', icon: '👥' }
    },
    step3Title: 'Содержание искового заявления о защите прав потребителей',
    step3Fields: {
      claim_title: { label: '📌 Наименование', placeholder: 'О возврате денежных средств / замене товара / устранении недостатков' },
      factual_circumstances: { label: '📖 Обстоятельства дела', placeholder: 'Дата покупки, товар/услуга, выявленные недостатки, обращение к продавцу...', type: 'textarea', rows: 6 },
      legal_basis: { label: '⚖️ Правовое обоснование', placeholder: 'ст. 4, 18, 29 Закона РФ "О защите прав потребителей"', type: 'textarea', rows: 2 },
      claim_subject: { label: '🎯 Прошу (включая моральный вред и штраф 50%)', placeholder: 'Взыскать стоимость товара, неустойку, компенсацию морального вреда, штраф 50%', type: 'textarea', rows: 3 },
      state_duty: { label: '💰 Госпошлина (руб.)', placeholder: '0 (если цена иска до 1 млн, ст. 17 ЗоЗПП)', type: 'number' },
      attachments: { label: '📎 Приложения', placeholder: '1. Чек, договор\n2. Претензия с отметкой о вручении...', type: 'textarea', rows: 4 }
    }
  }
};

// Группировка по категориям для UI
export const DOC_TEMPLATES_GROUPED = Object.entries(DOC_TYPE_CONFIG).reduce((acc, [value, config]) => {
  if (!acc[config.category]) acc[config.category] = [];
  acc[config.category].push({ value, label: config.label });
  return acc;
}, {});
