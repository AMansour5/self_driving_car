// ---- Configuration ---------------------------------------------------------
const ROSBRIDGE_URL = `ws://${location.hostname || 'localhost'}:9090`;
const CAMS = {  // panel id -> CompressedImage topic (from jpeg_relay.py)
  front: '/carla/camera/image_raw/compressed',
  rear:  '/carla/camera_rear/image_raw/compressed',
  left:  '/carla/camera_left/image_raw/compressed',
  right: '/carla/camera_right/image_raw/compressed',
};
const THROTTLE_MS = 100;  // max 10 fps per camera over the websocket
const STALE_MS = 2000;    // no frame for this long -> "No signal"
const DEADZONE = 0.05;
const AXIS_NAMES = ['LX', 'LY', 'RX', 'RY'];
const N_BUTTONS = 16;
// ---------------------------------------------------------------------------

const $ = id => document.getElementById(id);
let ros, connected = false, modeTopic, joyTopic, mode = 'manual', toastTimer;
const latest = {}, shown = {}, lastSeen = {};

function showToast(text) {
  $('toast').textContent = text;
  $('toast').classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => $('toast').classList.remove('show'), 2500);
}

// ---- ROS connection (auto-reconnect) ----
function setRos(ok) {
  connected = ok;
  $('dot-ros').classList.toggle('ok', ok);
  $('ros-text').textContent = ok ? 'ROS CONNECTED' : 'ROS DISCONNECTED';
}

function connect() {
  ros = new ROSLIB.Ros({ url: ROSBRIDGE_URL });
  ros.on('connection', () => { setup(); setRos(true); });
  ros.on('close', () => { setRos(false); setTimeout(connect, 2000); });
  ros.on('error', () => {});  // 'close' always follows and handles the retry
}

function setup() {
  modeTopic = new ROSLIB.Topic({ ros, name: '/control_mode', messageType: 'std_msgs/msg/String', latch: true });
  joyTopic = new ROSLIB.Topic({ ros, name: '/joy', messageType: 'sensor_msgs/msg/Joy' });
  for (const [name, topic] of Object.entries(CAMS)) {
    new ROSLIB.Topic({
      ros, name: topic, messageType: 'sensor_msgs/msg/CompressedImage',
      throttle_rate: THROTTLE_MS, queue_length: 1,
    }).subscribe(msg => { latest[name] = msg; });  // keep only the newest frame
  }
}

// ---- Camera rendering: base64 JPEG -> <img>, one update per animation frame ----
function render() {
  const now = performance.now();
  for (const name of Object.keys(CAMS)) {
    const img = $('cam-' + name), msg = latest[name];
    if (msg && msg !== shown[name]) {
      img.src = 'data:image/jpeg;base64,' + msg.data;
      shown[name] = msg;
      lastSeen[name] = now;
    }
    img.parentElement.classList.toggle('live', now - (lastSeen[name] ?? -Infinity) < STALE_MS);
  }
  requestAnimationFrame(render);
}

// ---- Mode ----
function publishMode() {
  if (connected) modeTopic.publish(new ROSLIB.Message({ data: mode }));
}

function setMode(m, announce = true) {
  mode = m;
  const manual = m === 'manual';
  $('mode').textContent = manual ? 'MANUAL' : 'AUTONOMOUS';
  $('mode').classList.toggle('auto', !manual);
  $('btn-manual').classList.toggle('active', manual);
  $('btn-auto').classList.toggle('active', !manual);
  $('joy-row').classList.toggle('hidden', !manual);
  $('gamepad-panel').classList.toggle('hidden', !manual);
  publishMode();
  if (announce) showToast('Phase set to ' + m.toUpperCase() + ' ✓');
}

$('btn-manual').onclick = () => setMode('manual');
$('btn-auto').onclick = () => setMode('autonomous');

// ---- Gamepad visual (built once; CSS draws the bars from --v) ----
AXIS_NAMES.forEach((n, i) => {
  $('axes').insertAdjacentHTML('beforeend',
    `<div><div class="axis-label">${n}</div><div class="axis-track"><div class="axis-fill" id="ax${i}"></div></div></div>`);
});
for (let i = 0; i < N_BUTTONS; i++) {
  $('btn-grid').insertAdjacentHTML('beforeend', `<div class="btn-cell" id="btn-${i}"></div>`);
}

// ---- Joystick: browser Gamepad API (Bluetooth pad paired to the laptop) ----
const getPad = () => [...navigator.getGamepads()].find(p => p);

function pollJoystick() {
  const pad = getPad();
  $('dot-joy').classList.toggle('ok', !!pad);
  $('joy-text').textContent = pad ? 'JOYSTICK CONNECTED' : 'JOYSTICK NOT CONNECTED';
  if (!pad || mode !== 'manual') return;

  const axes = pad.axes.map(a => (Math.abs(a) < DEADZONE ? 0 : a));
  AXIS_NAMES.forEach((_, i) => $('ax' + i).style.setProperty('--v', axes[i] ?? 0));
  for (let i = 0; i < N_BUTTONS; i++) {
    $('btn-' + i).classList.toggle('active', !!pad.buttons[i]?.pressed);
  }

  if (connected) {
    const ms = Date.now();
    joyTopic.publish(new ROSLIB.Message({
      header: { stamp: { sec: Math.floor(ms / 1000), nanosec: (ms % 1000) * 1e6 }, frame_id: '' },
      axes,
      buttons: pad.buttons.map(b => (b.pressed ? 1 : 0)),
    }));
  }
}

setMode('manual', false);
connect();
requestAnimationFrame(render);
setInterval(pollJoystick, 50);   // 20 Hz
setInterval(publishMode, 1000);  // heartbeat so late subscribers learn the mode