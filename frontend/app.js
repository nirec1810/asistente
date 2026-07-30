/* ========================================
   Adam Voice Assistant — App Logic
   ======================================== */

(() => {
  'use strict';

  const API_URL = window.location.origin + '/api';

  // ---- DOM refs ----
  const canvas = document.getElementById('waveform');
  const ctx = canvas.getContext('2d');
  const waveformState = document.getElementById('waveformState');
  const headerStatus = document.getElementById('headerStatus');
  const messages = document.getElementById('messages');
  const chatArea = document.getElementById('chatArea');
  const textInput = document.getElementById('textInput');
  const sendBtn = document.getElementById('sendBtn');
  const voiceBtn = document.getElementById('voiceBtn');
  const clearChat = document.getElementById('clearChat');
  const menuBtn = document.getElementById('menuBtn');
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const commandItems = document.querySelectorAll('.command-item');

  // ---- State ----
  let state = 'idle';
  let animationId = null;
  let phase = 0;
  let targetAmplitudes = [];
  let currentAmplitudes = [];
  let currentContext = null;
  let recognition = null;
  let synth = window.speechSynthesis;
  let speaking = false;

  // ---- Voice Recognition (Web Speech API) ----
  function initVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;

    const rec = new SpeechRecognition();
    rec.lang = 'es-ES';
    rec.continuous = false;
    rec.interimResults = false;

    rec.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log('Voice recognized:', transcript);
      handleInput(transcript);
    };

    rec.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setState('idle');
      voiceBtn.classList.remove('active');
      if (event.error === 'not-allowed') {
        addMessage('Permiso de micrófono denegado. Habilita el acceso en tu navegador.', 'assistant');
      } else if (event.error !== 'no-speech') {
        addMessage('No se pudo reconocer tu voz. Intenta de nuevo.', 'assistant');
      }
    };

    rec.onend = () => {
      setState('idle');
      voiceBtn.classList.remove('active');
    };

    return rec;
  }

  recognition = initVoiceRecognition();

  // ---- Speech Synthesis ----
  function speak(text) {
    return new Promise((resolve) => {
      if (!synth) {
        resolve();
        return;
      }

      synth.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'es-ES';
      utterance.rate = 1;
      utterance.pitch = 1;

      const voices = synth.getVoices();
      const spanishVoice = voices.find(v => v.lang.startsWith('es'));
      if (spanishVoice) {
        utterance.voice = spanishVoice;
      }

      utterance.onend = () => {
        speaking = false;
        resolve();
      };

      utterance.onerror = () => {
        speaking = false;
        resolve();
      };

      speaking = true;
      synth.speak(utterance);
    });
  }

  // Preload voices
  if (synth) {
    synth.onvoiceschanged = () => synth.getVoices();
  }

  // ---- Waveform ----
  function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = 120 * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = '120px';
    ctx.scale(dpr, dpr);
  }

  function initAmplitudes(count) {
    targetAmplitudes = Array.from({ length: count }, () => 0);
    currentAmplitudes = Array.from({ length: count }, () => 0);
  }

  function getWaveformConfig(s) {
    switch (s) {
      case 'listening':
        return { color: '#00E5FF', speed: 0.04, amplitude: 0.7, segments: 64, noise: 0.4 };
      case 'thinking':
        return { color: '#FF6B35', speed: 0.06, amplitude: 0.3, segments: 48, noise: 0.2 };
      case 'speaking':
        return { color: '#FF6B35', speed: 0.05, amplitude: 0.9, segments: 80, noise: 0.15 };
      default:
        return { color: '#00E5FF', speed: 0.015, amplitude: 0.15, segments: 48, noise: 0 };
    }
  }

  function drawWaveform() {
    const w = canvas.width / (window.devicePixelRatio || 1);
    const h = canvas.height / (window.devicePixelRatio || 1);
    const config = getWaveformConfig(state);

    ctx.clearRect(0, 0, w, h);

    if (targetAmplitudes.length !== config.segments) {
      initAmplitudes(config.segments);
    }

    for (let i = 0; i < config.segments; i++) {
      const noise = (Math.random() - 0.5) * config.noise;
      const wave = Math.sin(phase + i * 0.15) * config.amplitude;
      targetAmplitudes[i] = wave + noise;
    }

    for (let i = 0; i < config.segments; i++) {
      currentAmplitudes[i] += (targetAmplitudes[i] - currentAmplitudes[i]) * 0.12;
    }

    const gradient = ctx.createLinearGradient(0, 0, w, 0);
    gradient.addColorStop(0, 'transparent');
    gradient.addColorStop(0.2, config.color + '20');
    gradient.addColorStop(0.5, config.color + '40');
    gradient.addColorStop(0.8, config.color + '20');
    gradient.addColorStop(1, 'transparent');

    const barWidth = w / config.segments;
    const centerY = h / 2;

    for (let i = 0; i < config.segments; i++) {
      const x = i * barWidth;
      const barH = Math.abs(currentAmplitudes[i]) * centerY * 0.8;

      ctx.fillStyle = gradient;
      ctx.fillRect(x + 1, centerY - barH, barWidth - 2, barH * 2);
    }

    ctx.strokeStyle = config.color + '30';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(w, centerY);
    ctx.stroke();

    phase += config.speed;
    animationId = requestAnimationFrame(drawWaveform);
  }

  // ---- State management ----
  function setState(newState) {
    state = newState;
    const labels = {
      idle: 'En espera',
      listening: 'Escuchando...',
      thinking: 'Pensando...',
      speaking: 'Hablando...'
    };
    const headerLabels = {
      idle: 'Listo para escuchar',
      listening: 'Escuchando tu comando...',
      thinking: 'Procesando...',
      speaking: 'Respondiendo...'
    };
    waveformState.textContent = labels[newState];
    waveformState.className = 'waveform-state' + (newState !== 'idle' ? ' ' + newState : '');
    headerStatus.textContent = headerLabels[newState];
  }

  // ---- Messages ----
  function addMessage(text, role) {
    const msg = document.createElement('div');
    msg.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'assistant' ? '◆' : 'Tú';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;

    msg.appendChild(avatar);
    msg.appendChild(content);
    messages.appendChild(msg);

    chatArea.scrollTop = chatArea.scrollHeight;

    const welcome = document.querySelector('.welcome-msg');
    if (welcome) welcome.style.display = 'none';
  }

  // ---- API calls ----
  async function sendCommand(command) {
    try {
      const response = await fetch(`${API_URL}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending command:', error);
      return {
        response: 'No se pudo conectar con el asistente. Verifica que el servidor esté ejecutándose.',
        state: 'complete',
        context: null
      };
    }
  }

  async function sendFollowUp(response_text, context) {
    try {
      const response = await fetch(`${API_URL}/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response: response_text, context })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending follow-up:', error);
      return {
        response: 'No se pudo conectar con el asistente.',
        state: 'complete',
        context: null
      };
    }
  }

  async function handleInput(text) {
    if (!text.trim()) return;

    addMessage(text, 'user');
    textInput.value = '';

    setState('thinking');

    let result;
    if (currentContext) {
      result = await sendFollowUp(text, currentContext);
    } else {
      result = await sendCommand(text);
    }

    setState('speaking');
    addMessage(result.response, 'assistant');

    if (result.state === 'waiting_input' && result.context) {
      currentContext = result.context;
      headerStatus.textContent = 'Esperando tu respuesta...';
    } else {
      currentContext = null;
    }

    await speak(result.response);
    setState('idle');
  }

  // ---- Events ----
  sendBtn.addEventListener('click', () => handleInput(textInput.value));

  textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      handleInput(textInput.value);
    }
  });

  voiceBtn.addEventListener('click', () => {
    if (!recognition) {
      addMessage('Tu navegador no soporta reconocimiento de voz. Usa Chrome o Edge.', 'assistant');
      return;
    }

    if (state === 'listening') {
      recognition.stop();
      setState('idle');
      voiceBtn.classList.remove('active');
    } else {
      setState('listening');
      voiceBtn.classList.add('active');
      recognition.start();
    }
  });

  clearChat.addEventListener('click', () => {
    messages.innerHTML = '';
    currentContext = null;
    if (synth) synth.cancel();
    const welcome = document.querySelector('.welcome-msg');
    if (welcome) welcome.style.display = '';
  });

  menuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });

  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.remove('open');
  });

  commandItems.forEach(item => {
    item.addEventListener('click', () => {
      const cmd = item.dataset.command;
      textInput.value = cmd;
      handleInput(cmd);
      sidebar.classList.remove('open');
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'k') {
      e.preventDefault();
      messages.innerHTML = '';
      currentContext = null;
      if (synth) synth.cancel();
      const welcome = document.querySelector('.welcome-msg');
      if (welcome) welcome.style.display = '';
    }
  });

  document.addEventListener('click', (e) => {
    if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== menuBtn) {
      sidebar.classList.remove('open');
    }
  });

  // ---- Init ----
  resizeCanvas();
  initAmplitudes(48);
  drawWaveform();

  window.addEventListener('resize', () => {
    resizeCanvas();
  });
})();
