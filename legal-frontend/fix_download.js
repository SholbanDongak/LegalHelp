const fs = require('fs');
const path = './src/App.jsx';
let content = fs.readFileSync(path, 'utf8');

const downloadFunction = `
const downloadAsDocx = async (text, filename) => {
  const { Packer, Document, Paragraph, TextRun } = require('docx');
  const paragraphs = text.split('\\n').map(line => {
    if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
      return new Paragraph({ bullet: { level: 0 }, children: [new TextRun(line.trim().substring(1).trim())] });
    }
    return new Paragraph({ children: [new TextRun(line)] });
  });
  const doc = new Document({ sections: [{ children: paragraphs }] });
  const blob = await Packer.toBlob(doc);
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.href = url;
  link.download = \`\${filename}.docx\`;
  link.click();
  URL.revokeObjectURL(url);
};
`;

// Заменяем старую функцию (ищем по ключевым словам)
if (content.includes('const downloadAsDocx =')) {
  const start = content.indexOf('const downloadAsDocx =');
  const end = content.indexOf(';', start) + 1;
  content = content.slice(0, start) + downloadFunction + content.slice(end);
}
fs.writeFileSync(path, content);
console.log('Функция скачивания обновлена');
