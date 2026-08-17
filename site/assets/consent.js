/* Hestora cookie consent + Microsoft Clarity loader
 * ------------------------------------------------------------------
 * Uses Clarity's ConsentV2 API so that consent state is signalled
 * explicitly rather than implied by whether the tag was loaded.
 *
 * COOKIELESS_BEFORE_CONSENT (below):
 *   true  - Clarity loads for everyone but starts in cookieless mode
 *           (analytics_Storage: "denied"). No cookies, no persistent
 *           storage, no cross-session identity: Clarity assigns a
 *           throwaway ID per page view. Scroll depth and heatmaps are
 *           captured for all visitors; full session stitching only
 *           after "Accept analytics".
 *   false - Original behaviour: Clarity does not load at all until the
 *           visitor clicks "Accept analytics".
 *
 * Flip to false for the strictest reading of PECR. See cookies.html,
 * which must stay consistent with whichever setting is live.
 * ------------------------------------------------------------------ */
(function () {
  var KEY = 'hestora-consent';
  var CLARITY_PROJECT = 'xwogofit57';
  var COOKIELESS_BEFORE_CONSENT = true;

  var clarityLoaded = false;

  function loadClarity() {
    if (clarityLoaded) return;
    clarityLoaded = true;
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CLARITY_PROJECT);
  }

  /* Signal consent state to Clarity. Queued by the stub above if the
     tag has not finished loading, so it is safe to call immediately. */
  function signalConsent(granted) {
    if (typeof window.clarity !== 'function') return;
    try {
      window.clarity('consentv2', {
        ad_Storage: 'denied',
        analytics_Storage: granted ? 'granted' : 'denied'
      });
    } catch (e) {}
  }

  function readChoice() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function writeChoice(value) {
    try { localStorage.setItem(KEY, value); } catch (e) {}
  }

  function showBanner() {
    if (document.getElementById('hestora-consent-banner')) return;

    var b = document.createElement('div');
    b.id = 'hestora-consent-banner';
    b.setAttribute('role', 'dialog');
    b.setAttribute('aria-label', 'Cookie consent');
    b.innerHTML =
      '<style>' +
      '#hestora-consent-banner{position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#1B3A2F;color:#fff;font-family:Inter,system-ui,sans-serif;box-shadow:0 -4px 24px rgba(0,0,0,.25)}' +
      '#hestora-consent-banner .hcb-in{max-width:1100px;margin:0 auto;padding:18px 24px;display:flex;align-items:center;gap:20px;flex-wrap:wrap}' +
      '#hestora-consent-banner p{margin:0;font-size:14px;line-height:1.55;flex:1 1 420px;color:rgba(255,255,255,.92)}' +
      '#hestora-consent-banner a{color:#8fd3bf}' +
      '#hestora-consent-banner .hcb-btns{display:flex;gap:10px;flex-wrap:wrap}' +
      '#hestora-consent-banner button{font-family:Manrope,Inter,sans-serif;font-weight:700;font-size:14px;border-radius:8px;padding:10px 18px;cursor:pointer;border:0}' +
      '#hestora-consent-banner .hcb-accept{background:#F59435;color:#1A1A1A}' +
      '#hestora-consent-banner .hcb-accept:hover{background:#ffa64f}' +
      '#hestora-consent-banner .hcb-decline{background:transparent;color:#fff;border:1.5px solid rgba(255,255,255,.5)}' +
      '#hestora-consent-banner .hcb-decline:hover{border-color:#fff}' +
      '</style>' +
      '<div class="hcb-in">' +
      '<p><strong>Cookies at Hestora.</strong> We’d like to use Microsoft Clarity analytics to understand how visitors use our site and improve it. No advertising, no cross-site tracking. See our <a href="cookies.html">Cookie Policy</a>.</p>' +
      '<div class="hcb-btns">' +
      '<button type="button" class="hcb-decline">Essential only</button>' +
      '<button type="button" class="hcb-accept">Accept analytics</button>' +
      '</div></div>';

    document.body.appendChild(b);

    function close(value) {
      writeChoice(value);
      b.remove();
      if (value === 'accepted') {
        loadClarity();
        signalConsent(true);
      } else {
        signalConsent(false);
      }
    }
    b.querySelector('.hcb-accept').addEventListener('click', function () { close('accepted'); });
    b.querySelector('.hcb-decline').addEventListener('click', function () { close('declined'); });
  }

  function whenReady(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  /* Lets cookies.html offer a real "change your choice" control instead
     of telling people to clear their browser data. */
  window.hestoraCookieSettings = function () {
    try { localStorage.removeItem(KEY); } catch (e) {}
    whenReady(showBanner);
  };

  var choice = readChoice();

  if (choice === 'accepted') {
    loadClarity();
    signalConsent(true);
    return;
  }

  if (choice === 'declined') {
    /* Respect the explicit refusal: do not load Clarity at all. */
    return;
  }

  /* No choice recorded yet. */
  if (COOKIELESS_BEFORE_CONSENT) {
    loadClarity();
    signalConsent(false);
  }
  whenReady(showBanner);
})();
