(() => {
  'use strict';
  document.querySelectorAll('[data-cover-image]').forEach(image => {
    const show = () => {
      if (image.naturalWidth > 1 && image.naturalHeight > 1) {
        image.hidden = false;
        image.parentElement.classList.add('cover-loaded');
      } else {
        hide();
      }
    };
    const hide = () => {
      image.hidden = true;
      image.parentElement.classList.remove('cover-loaded');
    };
    image.addEventListener('load', show);
    image.addEventListener('error', hide);
    if (image.complete) show();
  });
})();
