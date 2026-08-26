const initialKudos = [
  { from: 'Maya Chen', fromInitial: 'M', fromClass: 'avatar-coral', to: 'Jordan Lee', toInitial: 'J', toClass: 'avatar-yellow', message: 'For jumping in to untangle the release plan and keeping us moving. You made a tricky week feel easy.', time: '12 min ago' },
  { from: 'Priya Shah', fromInitial: 'P', fromClass: 'avatar-blue', to: 'Ethan Brooks', toInitial: 'E', toClass: 'avatar-plum', message: 'Your customer notes were incredibly thoughtful. They gave the whole team a much clearer place to start.', time: '48 min ago' },
  { from: 'Sofia Garcia', fromInitial: 'S', fromClass: 'avatar-teal', to: 'Liam Wilson', toInitial: 'L', toClass: 'avatar-coral', message: 'Thank you for making space for every voice in today’s workshop. That is the kind of leadership people remember.', time: '2 hrs ago' },
  { from: 'Ethan Brooks', fromInitial: 'E', fromClass: 'avatar-plum', to: 'Maya Chen', toInitial: 'M', toClass: 'avatar-coral', message: 'For the sharp eye and generous feedback on the new onboarding flow. The details really sing now.', time: 'Yesterday' }
];
const savedKudos = JSON.parse(localStorage.getItem('kindred-kudos') || '[]').map((item, index) => ({ id: item.id || `saved-${index}`, is_visible: item.is_visible !== false, ...item }));
const kudos = [...savedKudos, ...initialKudos.map((item, index) => ({ id: `seed-${index}`, is_visible: true, ...item }))];
const feedList = document.querySelector('#feed-list');
const form = document.querySelector('#kudos-form');
const recipient = document.querySelector('#recipient');
const message = document.querySelector('#message');
const charCount = document.querySelector('#char-count');
const status = document.querySelector('#form-status');
const kudosCount = document.querySelector('#kudos-count');
const adminToggle = document.querySelector('#admin-toggle');
let isAdmin = false;

function avatarClass(name) {
  const classes = ['avatar-coral', 'avatar-yellow', 'avatar-blue', 'avatar-plum', 'avatar-teal'];
  return classes[name.charCodeAt(0) % classes.length];
}
function renderFeed() {
  const visibleKudos = kudos.filter((item) => isAdmin || item.is_visible);
  feedList.innerHTML = visibleKudos.length ? visibleKudos.map((item, index) => `<article class="feed-item${item.is_visible ? '' : ' hidden-item'}" style="animation-delay:${Math.min(index * 70, 280)}ms"><span class="avatar ${item.fromClass}">${item.fromInitial}</span><div class="feed-body"><div class="feed-top"><strong>${item.from}</strong><span class="to">celebrated</span><span class="avatar ${item.toClass}" style="width:20px;height:20px;font-size:8px">${item.toInitial}</span><strong>${item.to}</strong><span class="feed-time">${item.time}</span></div><p class="feed-message">${item.message}</p><span class="kudos-tag">✦ Team player</span>${isAdmin ? `<div class="moderation-actions"><span class="visibility-state">${item.is_visible ? 'Visible to team' : 'Hidden from team'}</span>${item.is_visible ? `<button class="moderate-button" data-action="hide" data-id="${item.id}">Hide</button>` : ''}<button class="moderate-button delete" data-action="delete" data-id="${item.id}">Delete</button></div>` : ''}</div></article>`).join('') : '<p class="empty-feed">No visible kudos right now.</p>';
  kudosCount.textContent = 20 + kudos.filter((item) => item.is_visible).length;
}
message.addEventListener('input', () => { charCount.textContent = `${message.value.length} / 180`; });
form.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!recipient.value || !message.value.trim()) { status.textContent = 'Choose a colleague and add a message first.'; status.className = 'form-status error'; return; }
  const newKudos = { from: 'Nicole Adams', fromInitial: 'N', fromClass: 'avatar-teal', to: recipient.value, toInitial: recipient.value[0], toClass: avatarClass(recipient.value), message: message.value.trim(), time: 'Just now' };
  newKudos.id = `kudos-${Date.now()}`;
  newKudos.is_visible = true;
  savedKudos.unshift(newKudos);
  localStorage.setItem('kindred-kudos', JSON.stringify(savedKudos));
  kudos.unshift(newKudos);
  renderFeed();
  form.reset();
  charCount.textContent = '0 / 180';
  status.textContent = `Kudos sent to ${newKudos.to}!`;
  status.className = 'form-status';
  document.querySelector('#feed').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

function persistKudos() {
  localStorage.setItem('kindred-kudos', JSON.stringify(kudos.filter((item) => item.id.startsWith('kudos-') || item.id.startsWith('saved-'))));
}
adminToggle.addEventListener('click', () => {
  isAdmin = !isAdmin;
  adminToggle.setAttribute('aria-pressed', String(isAdmin));
  adminToggle.classList.toggle('active', isAdmin);
  renderFeed();
});
feedList.addEventListener('click', (event) => {
  const actionButton = event.target.closest('[data-action]');
  if (!actionButton || !isAdmin) return;
  const item = kudos.find((entry) => entry.id === actionButton.dataset.id);
  if (!item) return;
  if (actionButton.dataset.action === 'delete') {
    if (!window.confirm('Delete this kudos permanently?')) return;
    kudos.splice(kudos.indexOf(item), 1);
  } else {
    item.is_visible = false;
  }
  persistKudos();
  renderFeed();
});

document.querySelector('#load-more').addEventListener('click', (event) => { event.currentTarget.textContent = 'You’re all caught up  ✓'; event.currentTarget.disabled = true; });
renderFeed();
