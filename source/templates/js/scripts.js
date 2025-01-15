console.log("Hello from JavaScript!");
function speakText(text, lang = 'en-US') {
    return new Promise(resolve => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      utterance.onend = resolve;
      speechSynthesis.speak(utterance);
    });
  }

  class TTSManager {
    constructor() {
      this.queue = [];
      this.isSpeaking = false;
    }
    speak(text, lang = 'en-US') {
      this.queue.push({ text, lang });
      this.processQueue();
    }
    processQueue() {
      if (this.isSpeaking || this.queue.length === 0) return;
      this.isSpeaking = true;
      const { text, lang } = this.queue.shift();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      utterance.onend = () => { this.isSpeaking = false; this.processQueue(); };
      utterance.onerror = (e) => { console.error(e.error); this.isSpeaking = false; this.processQueue(); };
      speechSynthesis.speak(utterance);
    }
  }

  const slideService = {
    slides: [],
    totalSlides: 0
  };

  async function loadSlides() {
    try {
      const response = await fetch('http://localhost:8000/api/slides');
      const data = await response.json();
      slideService.slides = data.slides;
      slideService.totalSlides = data.totalSlides;
      console.log('Slides loaded:', slideService);
    } catch (error) {
      console.error('Error fetching slides:', error);
    }
  }

  const controlSlide = {
    navigateSlide(slideNumber) {
      console.log(`Navigating to slide ${slideNumber + 1}`);
      // Update iframe or other UI elements as needed
    }
  };

  const questionHandler = {
    questionQueue: [],
    processQuestions() {
      while (this.questionQueue.length) {
        const q = this.questionQueue.shift();
        console.log("Processing question:", q);
        // Process the question as needed
      }
    },
    hasQuestions() {
      return this.questionQueue.length > 0;
    }
  };

  class SlideNarrationFSM {
    constructor(slideService, ttsManager, questionHandler, controlSlide) {
      this.state = "START";
      this.slideService = slideService;
      this.ttsManager = ttsManager;
      this.questionHandler = questionHandler;
      this.controlSlide = controlSlide;
      this.currentSlide = 0;
      this.totalSlides = slideService.totalSlides;
      this.interruptFlag = false;
      this.running = true;
    }

    saveState() {
      const stateData = { state: this.state, currentSlide: this.currentSlide };
      localStorage.setItem('fsmState', JSON.stringify(stateData));
      console.log("State saved:", stateData);
    }

    loadState() {
      const stateData = localStorage.getItem('fsmState');
      if (stateData) {
        const data = JSON.parse(stateData);
        this.state = data.state || "START";
        this.currentSlide = data.currentSlide || 0;
        console.log("State loaded:", data);
        if (this.state === "END") {
          this.state = "START";
          this.currentSlide = 0;
          console.log("Restarting...");
        }
      } else {
        console.log("No saved state. Starting fresh.");
        this.state = "START";
        this.currentSlide = 0;
      }
    }

    start() {
      console.log("Session Started.");
      this.loadState();
      this.transition("SLIDE_NARRATION");
    }

    async slideNarration() {
      while (this.currentSlide < this.totalSlides && this.running) {
        const slide = this.slideService.slides[this.currentSlide];
        const slideText = slide.speakerNotes || "No text available";
        this.controlSlide.navigateSlide(this.currentSlide);
        
        await speakText(slideText, 'zh-CN'); 
        // Simulate waiting time for TTS to finish (adjust as needed)
        await new Promise(resolve => setTimeout(resolve, 3000));

        this.interruptFlag = this.questionHandler.hasQuestions();
        if (this.interruptFlag) {
          this.transition("QUESTION");
          return;
        }
        this.currentSlide += 1;
      }
      this.transition("END");
    }

    question() {
      console.log("[QUESTION] Handling user question(s).");
      this.questionHandler.processQuestions();
      this.transition("RESUME");
    }

    resume() {
      console.log("[RESUME] Resuming slide narration...");
      this.currentSlide += 1;
      this.transition("SLIDE_NARRATION");
    }

    transition(nextState) {
      console.log(`[Transition] Moving from ${this.state} to ${nextState}.`);
      this.state = nextState;
      this.saveState();
      if (this.state === "SLIDE_NARRATION") {
        this.slideNarration();
      } else if (this.state === "QUESTION") {
        this.question();
      } else if (this.state === "RESUME") {
        this.resume();
      } else if (this.state === "END") {
        this.running = false;
        console.log("Session Ended. Thank you for participating!");
      }
    }
  }

  const ttsManager = new TTSManager();

  const socket = io();
  socket.on('slide_update', (data) => {
    const iframe = document.getElementById('slidesIframe');
    // Update the iframe src based on slide update (adjust as necessary)
    iframe.src = `https://docs.google.com/presentation/d/YOUR_PRESENTATION_ID/embed?start=false&loop=false&delayms=60000#slide=id.${data.objectId}`;
  });

  const messagesDiv = document.getElementById('messages');
  const questionInput = document.getElementById('questionInput');
  const sendButton = document.getElementById('sendButton');

  function appendMessage(text, sender = "系统", speakIt = false) {
    const msgElem = document.createElement('div');
    msgElem.textContent = sender + ": " + text;
    messagesDiv.appendChild(msgElem);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    if (speakIt) {
      ttsManager.speak(text, "zh-CN");
    }
  }

  sendButton.addEventListener('click', () => {
    const question = questionInput.value.trim();
    if (question) {
      appendMessage(question, "You");
      questionHandler.questionQueue.push(question);

      fetch('/new_question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      })
      .then(response => response.json())
      .then(data => {
        if (data.answer) {
          appendMessage(data.answer, "Answer", true);
        } else if (data.error) {
          appendMessage("Error: " + data.error, "System");
        }
      })
      .catch(error => {
        console.error('Error:', error);
        appendMessage("Error sending question: " + error, "System");
      });
      questionInput.value = '';
    }
  });

  document.getElementById('startProcessButton').addEventListener('click', async () => {
    await loadSlides();  
    const fsm = new SlideNarrationFSM(slideService, ttsManager, questionHandler, controlSlide);
    fsm.totalSlides = slideService.totalSlides;  
    fsm.start();
  });

  appendMessage("等待课堂开始。", "系统", true);