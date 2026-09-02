
(() => {
  'use strict';
  const $ = (selector, parent = document) => parent.querySelector(selector);
  const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const storage = {
    get(key, fallback, session = false) {
      try { return JSON.parse((session ? sessionStorage : localStorage).getItem(key)) ?? fallback; }
      catch { return fallback; }
    },
    set(key, value, session = false) {
      try { (session ? sessionStorage : localStorage).setItem(key, JSON.stringify(value)); return true; }
      catch { return false; }
    }
  };
  let toastTimer;
  function toast(message) {
    const notice = $('#toast');
    notice.textContent = message;
    notice.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => notice.classList.remove('visible'), 3200);
  }

  // Only a completed guest choice or successful authentication opens the doors.
  const entrance = $('#entrance');
  const shell = $('#app-shell');
  let returnFocus;
  let entering = false;
  function showEntrance() {
    if (!entrance) { location.href = '/?entrance=1'; return; }
    returnFocus = document.activeElement;
    entering = false;
    entrance.classList.remove('opening');
    entrance.hidden = false;
    shell.inert = true;
    document.body.style.overflow = 'hidden';
    entrance.dataset.entryMode = 'choices';
    $('#enter-library').focus();
  }
  function enterLibrary(animate = true) {
    if (!entrance || entrance.hidden || entering) return;
    entering = true;
    entrance.classList.add('opening');
    const finish = () => {
      entrance.hidden = true;
      shell.inert = false;
      document.body.style.overflow = '';
      (returnFocus && returnFocus !== document.body ? returnFocus : $('#main')).focus({ preventScroll: true });
      entering = false;
    };
    if (!animate || matchMedia('(prefers-reduced-motion: reduce)').matches) finish();
    else setTimeout(finish, 1600);
  }
  if (entrance) {
    entrance.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        // Do not turn dismissing the chooser into an implicit guest choice.
        event.preventDefault();
      }
      if (event.key === 'Tab') {
        const actions = $$('button, a[href]', entrance).filter(element => element.getClientRects().length);
        if (!actions.length) { event.preventDefault(); return; }
        const first = actions[0]; const last = actions[actions.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    });
    if (entrance.dataset.entryMode === 'opening') {
      entrance.hidden = false;
      shell.inert = true;
      document.body.style.overflow = 'hidden';
      // Let the closed doors paint before the opening transition begins.
      requestAnimationFrame(() => requestAnimationFrame(() => enterLibrary()));
    } else if (entrance.dataset.entryMode === 'choices') {
      showEntrance();
    }
  }
  $$('.entrance-trigger, #reopen-doors').forEach(button => button.addEventListener('click', showEntrance));

  const sidebar = $('#sidebar');
  const menu = $('.menu-toggle');
  const scrim = $('.sidebar-scrim');
  const mobile = matchMedia('(max-width: 760px)');
  function closeSidebar() {
    sidebar.classList.remove('is-open');
    scrim.hidden = true;
    menu.setAttribute('aria-expanded', 'false');
    sidebar.inert = mobile.matches;
  }
  menu.addEventListener('click', () => {
    const opening = !sidebar.classList.contains('is-open');
    if (!opening) return closeSidebar();
    sidebar.inert = false;
    sidebar.classList.add('is-open');
    scrim.hidden = false;
    menu.setAttribute('aria-expanded', 'true');
    $('.brand', sidebar).focus();
  });
  scrim.addEventListener('click', closeSidebar);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && sidebar.classList.contains('is-open')) { closeSidebar(); menu.focus(); }
  });
  mobile.addEventListener('change', closeSidebar);
  closeSidebar();

  const form = $('#catalog-form');
  if (form) {
    form.addEventListener('submit', event => {
      const category = $('#current-category');
      category.name = event.submitter?.name === 'category' ? '' : 'category';
    });
    $('#sort').addEventListener('change', () => form.requestSubmit());
    $('[name="available"]').addEventListener('change', () => form.requestSubmit());
    $('.category-scroll').addEventListener('click', () => {
      const tabs = $('.category-tabs');
      if (tabs.scrollLeft + tabs.clientWidth >= tabs.scrollWidth - 5) tabs.scrollTo({ left: 0, behavior: 'smooth' });
      else tabs.scrollBy({ left: 230, behavior: 'smooth' });
    });
  }

  // Bookmarks are explicitly a browser-local wishlist, not account data.
  const initialSaved = storage.get('reading-room-saved', []);
  const saved = new Set(Array.isArray(initialSaved) ? initialSaved.map(String) : []);
  function refreshSaved() {
    $$('[data-save]').forEach(button => {
      const isSaved = saved.has(button.dataset.save);
      button.classList.toggle('is-saved', isSaved);
      button.setAttribute('aria-pressed', String(isSaved));
      if (button.classList.contains('dialog-save')) button.lastChild.textContent = isSaved ? ' Saved for later' : ' Save for later';
    });
    if (document.body.dataset.section === 'saved') {
      let visible = 0;
      $$('.book-card').forEach(card => {
        card.hidden = !saved.has(card.dataset.bookId);
        if (!card.hidden) visible++;
      });
      $('#saved-count').textContent = visible;
      $('#saved-empty').hidden = visible !== 0;
    }
  }
  $$('[data-save]').forEach(button => button.addEventListener('click', () => {
    const id = button.dataset.save;
    if (saved.has(id)) saved.delete(id); else saved.add(id);
    const persisted = storage.set('reading-room-saved', [...saved]);
    refreshSaved();
    toast(persisted ? (saved.has(id) ? 'A story saved for another day.' : 'Removed from your saved shelf.') : 'Saved for this page only. Browser storage is unavailable.');
  }));
  refreshSaved();

  $$('[data-detail]').forEach(button => button.addEventListener('click', () => {
    const dialog = document.getElementById(button.dataset.detail);
    if (dialog) dialog.showModal();
  }));
  $$('.book-dialog').forEach(dialog => {
    $('.dialog-close', dialog).addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    });
  });
  function changeLayout(layout) {
    $('#book-grid')?.classList.toggle('list-layout', layout === 'list');
    $$('[data-layout]').forEach(button => {
      const active = button.dataset.layout === layout;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
  }
  $$('[data-layout]').forEach(button => button.addEventListener('click', () => {
    changeLayout(button.dataset.layout);
    storage.set('reading-room-layout', button.dataset.layout);
  }));
  changeLayout(storage.get('reading-room-layout', 'grid'));
  $$('.dismiss-message').forEach(button => button.addEventListener('click', () => button.parentElement.remove()));
  // Client-side book search
  const searchInput = $("#catalog-form input[name='q']");

  console.log("SEARCH INPUT:", searchInput);

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      console.log("SEARCH INPUT CHANGED:", searchInput.value);

      const query = searchInput.value.trim().toLowerCase();

      $$('.book-card').forEach(card => {
        const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
        const author = card.querySelector('.book-info p')?.textContent.toLowerCase() || '';

        const matches =
          title.includes(query) ||
          author.includes(query);

        card.hidden = !matches;
      });
    });
  }
  // Client-side signup validation
  const registerForm = document.querySelector('input[name="email"]')?.closest('form');

  console.log("REGISTER FORM:", registerForm);
  if (registerForm) {
    registerForm.noValidate = true;

    registerForm.addEventListener('submit', event => {
      const username = registerForm.querySelector('input[name="username"]');
      const usernameError = document.getElementById('id_username-client-error');

      const email = registerForm.querySelector('input[name="email"]');
      const emailError = document.getElementById('id_email-client-error');

      const password = registerForm.querySelector('input[name="password1"]');
      const passwordError = document.getElementById('id_password1-client-error');

      // Username validation
      if (!username.value.trim()) {
        event.preventDefault();

        usernameError.textContent = 'Please enter your username.';
        usernameError.hidden = false;

        username.focus();
        return;
      }

      // Email required validation
      if (!email.value.trim()) {
        event.preventDefault();

        emailError.textContent = 'Please enter your email address.';
        emailError.hidden = false;

        email.focus();
        return;
      }

      // Email format validation
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (!emailPattern.test(email.value.trim())) {
        event.preventDefault();

        emailError.textContent = 'Please enter a valid email address.';
        emailError.hidden = false;

        email.focus();
        return;
      }

      // Password required validation
      if (!password.value.trim()) {
        event.preventDefault();

        passwordError.textContent = 'Please enter your password.';
        passwordError.hidden = false;

        password.focus();
        return;
      }

      const passwordConfirmation = registerForm.querySelector(
        'input[name="password2"]'
      );
      const passwordConfirmationError = document.getElementById(
        'id_password2-client-error'
      );

      // Password confirmation validation
      if (!passwordConfirmation.value.trim()) {
        event.preventDefault();

        passwordConfirmationError.textContent =
          'Please confirm your password.';
        passwordConfirmationError.hidden = false;

        passwordConfirmation.focus();
        return;
      }

      // Password matching validation
      if (password.value !== passwordConfirmation.value) {
        event.preventDefault();

        passwordConfirmationError.textContent =
          'Passwords do not match.';
        passwordConfirmationError.hidden = false;

        passwordConfirmation.focus();
        return;
      }








    });
  }

  // Audio is never started by the entrance or without a deliberate play action.
  const audio = $('#library-audio');
  const play = $('#music-play');
  const player = $('.music-player');
  const status = $('#music-status');
  async function toggleMusic() {
    if (!audio) { toast('The librarian has chosen a quiet room for now.'); return; }
    if (!audio.paused) { audio.pause(); return; }
    status.textContent = 'Putting the record on…';
    try { await audio.play(); }
    catch { status.textContent = 'This record could not play. Please try again.'; toast('Music could not play. Try again or ask your librarian to check the audio file.'); }
  }
  if (audio) {
    const volume = $('#music-volume');
    const mute = $('.volume-toggle');
    const savedVolume = Number(storage.get('reading-room-volume', 0.3));
    audio.volume = Number.isFinite(savedVolume) ? Math.max(0, Math.min(1, savedVolume)) : 0.3;
    volume.value = audio.volume;
    const updatePlayer = () => {
      const playing = !audio.paused;
      player.classList.toggle('is-playing', playing);
      play.setAttribute('aria-label', playing ? 'Pause library music' : 'Play library music');
      $('.play-glyph', play).textContent = playing ? 'Ⅱ' : '▶';
      status.textContent = playing ? 'Let the world wait a little.' : 'A little music for your next chapter.';
    };
    play.addEventListener('click', toggleMusic);
    audio.addEventListener('play', updatePlayer);
    audio.addEventListener('pause', updatePlayer);
    audio.addEventListener('error', () => {
      player.classList.remove('is-playing');
      play.setAttribute('aria-label', 'Retry library music');
      $('.play-glyph', play).textContent = '▶';
      status.textContent = 'Record unavailable. Please ask your librarian.';
    });
    audio.addEventListener('timeupdate', () => {
      const seconds = Math.floor(audio.currentTime);
      $('#music-time').textContent = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    });
    volume.addEventListener('input', () => {
      audio.volume = Number(volume.value);
      audio.muted = false;
      mute.setAttribute('aria-label', 'Mute music');
      mute.style.opacity = '1';
      storage.set('reading-room-volume', audio.volume);
    });
    mute.addEventListener('click', () => {
      audio.muted = !audio.muted;
      mute.setAttribute('aria-label', audio.muted ? 'Unmute music' : 'Mute music');
      mute.style.opacity = audio.muted ? '0.4' : '1';
    });
  }
  $('#corner-music')?.addEventListener('click', async () => {
    await toggleMusic();
    if (audio && !audio.paused) toast('The record is on. Make yourself at home.');
  });
})();
