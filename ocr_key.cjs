const { createWorker } = require('tesseract.js');
const fs = require('fs');

async function ocrPage(worker, imgPath) {
    const { data: { text } } = await worker.recognize(imgPath);
    return text.trim();
}

async function main() {
    const worker = await createWorker('chi_tra+eng', 1, { logger: m => {} });

    const pages = [
        ['5上A', 'jpg', ['p01','p02','p03','p04','p05','p50','p51','p52']],
        ['5上B', 'png', ['p01','p02','p03','p40','p41','p42']],
        ['5下A', 'jpg', ['p01','p02','p03','p53','p54','p55']],
        ['5下B', 'jpg', ['p01','p02','p03','p56','p57','p58']],
    ];

    for (const [book, ext, pageList] of pages) {
        console.log(`\n========================================`);
        console.log(`=== ${book} ===`);
        console.log(`========================================`);
        const dir = `G:/lam-fung-academy/_ocr_pages/${book}`;
        for (const p of pageList) {
            const files = fs.readdirSync(dir)
                .filter(f => f.startsWith(p) && f.endsWith(`.${ext}`))
                .sort();
            for (const f of files) {
                const imgPath = `${dir}/${f}`;
                console.log(`\n  [OCR] ${f} ...`);
                try {
                    const text = await ocrPage(worker, imgPath);
                    console.log(`\n--- ${f} ---`);
                    console.log(text.substring(0, 2000));
                } catch(e) {
                    console.log(`  ERROR: ${e.message}`);
                }
            }
        }
    }

    await worker.terminate();
    console.log('\n\n=== DONE ===');
}

main().catch(e => console.error(e));
