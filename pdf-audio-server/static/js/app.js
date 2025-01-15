const url = '/static/pdfs/slides.pdf';

let pdfDoc = null,
    currentPage = 1,
    canvas = document.getElementById('pdf-canvas'),
    ctx = canvas.getContext('2d'),
    audioPlayer = document.getElementById('audio-player');

// Log initialization
console.log('Initializing Slide Viewer...');
console.log('PDF URL:', url);

// Load PDF
pdfjsLib.getDocument(url).promise.then(pdfDoc_ => {
    pdfDoc = pdfDoc_;
    console.log('PDF loaded successfully. Total pages:', pdfDoc.numPages);
    renderPage(currentPage);
}).catch(error => {
    console.error('Error loading PDF:', error);
});

// Render the page
function renderPage(num) {
    console.log(`Rendering page ${num}...`);
    pdfDoc.getPage(num).then(page => {
        const viewport = page.getViewport({ scale: 1.5 });
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: ctx,
            viewport: viewport
        };
        const renderTask = page.render(renderContext);

        renderTask.promise.then(() => {
            console.log(`Page ${num} rendered successfully.`);

            // Load and play corresponding audio
            const slide = slides.find(s => s.slide_index === num - 1);
            if (slide) {
                console.log(`Slide found for page ${num}:`, slide);
                if (slide.audio_file) {
                    audioPlayer.src = `/${slide.audio_file}`;
                    console.log(`Audio source set to: ${audioPlayer.src}`);
                    audioPlayer.play().catch(error => {
                        console.error('Error playing audio:', error);
                    });
                } else {
                    console.log(`No audio file for page ${num}. Waiting for 1 second...`);
                    setTimeout(() => {
                        moveToNextSlide();
                    }, 1000); // Wait for 1 second before moving to the next slide
                }
            } else {
                console.warn('No slide data found for this page.');
                setTimeout(() => {
                    moveToNextSlide();
                }, 1000); // Wait for 1 second before moving to the next slide
            }
        }).catch(error => {
            console.error('Error rendering page:', error);
        });
    }).catch(error => {
        console.error(`Error getting page ${num}:`, error);
    });
}

// Automatically move to the next slide when audio ends
audioPlayer.addEventListener('ended', () => {
    console.log(`Audio finished for page ${currentPage}. Moving to next slide...`);
    moveToNextSlide();
});

// Move to the next slide
function moveToNextSlide() {
    if (currentPage < pdfDoc.numPages) {
        currentPage++;
        renderPage(currentPage);
    } else {
        console.log('Reached the last slide. No more slides to play.');
    }
}

// Button event listeners for manual navigation
document.getElementById('prev-slide').addEventListener('click', () => {
    if (currentPage <= 1) {
        console.log('Already at the first slide.');
        return;
    }
    currentPage--;
    renderPage(currentPage);
});

document.getElementById('next-slide').addEventListener('click', () => {
    if (currentPage >= pdfDoc.numPages) {
        console.log('Already at the last slide.');
        return;
    }
    currentPage++;
    renderPage(currentPage);
});
