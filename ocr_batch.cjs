const { createWorker } = require('tesseract.js');
const fs = require('fs');
const path = require('path');

const BOOKS = [
    { name: '5上A', dir: 'G:/lam-fung-academy/_ocr_pages/5上A' },
    { name: '5上B', dir: 'G:/lam-fung-academy/_ocr_pages/5上B' },
    { name: '5下A', dir: 'G:/lam-fung-academy/_ocr_pages/5下A' },
    { name: '5下B', dir: 'G:/lam-fung-academy/_ocr_pages/5下B' },
];

async function main() {
    const worker = await createWorker('chi_tra+eng', 1, {
        logger: m => {}
    });
    
    for (const book of BOOKS) {
        console.log(`\n=== ${book.name} ===`);
        const files = fs.readdirSync(book.dir)
            .filter(f => f.endsWith('.jpg'))
            .sort();
        
        const results = [];
        for (const file of files) {
            const imgPath = path.join(book.dir, file);
            try {
                const { data: { text } } = await worker.recognize(imgPath);
                const clean = text.trim();
                results.push(`--- ${file} ---\n${clean}`);
                process.stdout.write(`\r  ${file}: ${clean.substring(0, 60).replace(/\n/g, ' ')}...`);
            } catch(e) {
                results.push(`--- ${file} ---\n[ERROR: ${e.message}]`);
            }
        }
        
        const outPath = `G:/lam-fung-academy/_ocr_text/${book.name}.txt`;
        fs.mkdirSync('G:/lam-fung-academy/_ocr_text', { recursive: true });
        fs.writeFileSync(outPath, results.join('\n\n'), 'utf-8');
        console.log(`\n  Saved ${results.length} pages to ${outPath}`);
    }
    
    await worker.terminate();
    console.log('\n\nAll done!');
}

main().catch(e => console.error('Fatal:', e));
