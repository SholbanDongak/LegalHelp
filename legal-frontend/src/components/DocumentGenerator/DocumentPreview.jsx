import { useApp } from '../../contexts/AppContext';
import { FiDownload, FiCopy, FiX, FiFileText } from 'react-icons/fi';

export const DocumentPreview = () => {
  const { generatedDoc, setGeneratedDoc } = useApp();
  
  if (!generatedDoc) return null;
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedDoc.filled_text);
    alert('Текст скопирован!');
  };
  
  return (
    <div className="preview-overlay" onClick={() => setGeneratedDoc(null)}>
      <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
        <div className="preview-header">
          <div className="title">
            <FiFileText size={24} />
            <div>
              <h3>Документ сгенерирован</h3>
              <p>Тип: {generatedDoc.doc_type} • Уверенность: {(generatedDoc.confidence * 100).toFixed(0)}%</p>
            </div>
          </div>
          <button className="close-btn" onClick={() => setGeneratedDoc(null)}>
            <FiX size={24} />
          </button>
        </div>
        
        <div className="preview-content">
          <pre>{generatedDoc.filled_text}</pre>
        </div>
        
        <div className="preview-actions">
          {generatedDoc.docx_url && (
            <a href={`http://localhost:8000${generatedDoc.docx_url}`} download className="download-btn docx">
              <FiDownload /> Скачать DOCX
            </a>
          )}
          {generatedDoc.pdf_url && (
            <a href={`http://localhost:8000${generatedDoc.pdf_url}`} download className="download-btn pdf">
              <FiDownload /> Скачать PDF
            </a>
          )}
          <button className="copy-btn" onClick={copyToClipboard}>
            <FiCopy /> Копировать текст
          </button>
        </div>
      </div>
      
      <style>{`
        .preview-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.2s; }
        .preview-modal { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 16px; width: 90%; max-width: 800px; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
        .preview-header { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem; border-bottom: 1px solid var(--border); }
        .title { display: flex; align-items: center; gap: 1rem; }
        .title svg { color: var(--primary); }
        .title h3 { margin: 0; font-size: 1.2rem; }
        .title p { margin: 0; font-size: 0.85rem; color: var(--text-secondary); }
        .close-btn { background: none; border: none; color: var(--text-secondary); cursor: pointer; padding: 0.5rem; border-radius: 8px; transition: 0.2s; }
        .close-btn:hover { background: var(--bg-tertiary); color: var(--text-primary); }
        .preview-content { flex: 1; overflow-y: auto; padding: 1.5rem; }
        .preview-content pre { background: var(--bg-primary); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border); font-family: 'Courier New', monospace; font-size: 0.9rem; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; color: var(--text-primary); }
        .preview-actions { display: flex; gap: 0.75rem; padding: 1.5rem; border-top: 1px solid var(--border); }
        .download-btn, .copy-btn { flex: 1; padding: 0.75rem 1.5rem; border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: 0.2s; text-decoration: none; }
        .download-btn.docx { background: linear-gradient(135deg, #2563eb, #3b82f6); color: white; }
        .download-btn.pdf { background: linear-gradient(135deg, #dc2626, #ef4444); color: white; }
        .copy-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border); }
        .download-btn:hover, .copy-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
      `}</style>
    </div>
  );
};
