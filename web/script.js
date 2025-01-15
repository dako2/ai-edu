// Load the Google API client library
gapi.load('client:auth2', async () => {
  await gapi.client.init({
    apiKey: 'YOUR_API_KEY', // Replace with your API Key
    clientId: 'YOUR_CLIENT_ID', // Replace with your OAuth 2.0 Client ID
    discoveryDocs: ['https://slides.googleapis.com/$discovery/rest?version=v1'],
    scope: 'https://www.googleapis.com/auth/presentations.readonly',
  });

  // Authenticate the user
  const authInstance = gapi.auth2.getAuthInstance();
  await authInstance.signIn();

  // Get slides data
  const presentationId = '104e06duvtskYpkflvm0FgJ31YhTvSslnUFSCMxQtYmI'; // Replace with your Presentation ID
  const slidesData = await gapi.client.slides.presentations.get({
    presentationId: presentationId,
  });

  // Extract slide IDs and speaker notes
  const slides = slidesData.result.slides.map((slide, index) => ({
    id: slide.objectId,
    speakerNotes: slide.slideProperties?.notesPage?.notesProperties?.speakerNotes
      ? slide.slideProperties.notesPage.notesProperties.speakerNotes.text
      : 'No speaker notes',
    index: index + 1,
  }));

  console.log('Slides Data:', slides);

  // Initialize slide control
  controlSlide(slides);
});

// Function to navigate slides
function controlSlide(slides) {
  let currentIndex = 0;

  function showSlide(index) {
    if (index < 0 || index >= slides.length) {
      console.error('Invalid slide index');
      return;
    }
    currentIndex = index;
    const iframe = document.getElementById('slidesIframe');
    iframe.src = `https://docs.google.com/presentation/d/104e06duvtskYpkflvm0FgJ31YhTvSslnUFSCMxQtYmI/embed#slide=id.${slides[currentIndex].id}`;
    console.log(`Navigated to slide ${index + 1}`);
    console.log('Speaker Notes:', slides[currentIndex].speakerNotes);
  }

  // Example navigation controls
  document.getElementById('nextSlide').addEventListener('click', () => showSlide(currentIndex + 1));
  document.getElementById('prevSlide').addEventListener('click', () => showSlide(currentIndex - 1));
  showSlide(currentIndex); // Show the first slide
}

