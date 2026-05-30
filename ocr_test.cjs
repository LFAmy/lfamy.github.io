const { createWorker } = require('tesseract.js');

async function main() {
    console.log('Creating OCR worker for Chinese...');
    const worker = await createWorker('chi_tra+eng', 1, {
        logger: m => {
            if (m.status === 'recognizing text') {
                process.stdout.write(`\rOCR: ${Math.round(m.progress * 100)}%`);
            }
        }
    });
    
    const imgPath = 'G:/lam-fung-academy/_ocr_pages/5上A/p01_img0.jpg';
    console.log(`OCR on: ${imgPath}`);
    
    const { data: { text } } = await worker.recognize(imgPath);
    console.log('\n\n=== OCR RESULT ===');
    console.log(text);
    
    await worker.terminate();
    console.log('\nDone!');
}

main().catch(e => console.error('Error:', e));
