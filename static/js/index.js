(function () {
  "use strict";
  var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Navbar burger toggle
  var burger = document.querySelector(".nav-burger");
  var navLinks = document.querySelector(".nav-links");
  if (burger && navLinks) {
    burger.addEventListener("click", function () {
      var open = navLinks.classList.toggle("is-open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    navLinks.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        navLinks.classList.remove("is-open");
        burger.setAttribute("aria-expanded", "false");
      });
    });
  }

  function updateToggleBtn(video) {
    var wrap = video.closest(".clip-wrap");
    if (!wrap) return;
    var btn = wrap.querySelector(".clip-toggle-btn");
    if (!btn) return;
    var playing = !video.paused && !video.ended;
    btn.classList.toggle("is-playing", playing);
    btn.setAttribute("aria-pressed", playing ? "true" : "false");
    btn.setAttribute("aria-label", playing ? "Pause video" : "Play video");
    var lbl = btn.querySelector(".clip-toggle-lbl");
    if (lbl) lbl.textContent = playing ? "Pause" : "Play";
  }

  function syncClipControls() {
    var isPhone = window.innerWidth <= 768;
    document.querySelectorAll("video.example-clip").forEach(function (v) {
      if (isPhone) {
        v.removeAttribute("controls");
      } else {
        v.setAttribute("controls", "");
      }
      updateToggleBtn(v);
    });
  }

  document.querySelectorAll("video.example-clip").forEach(function (v) {
    v.addEventListener("play", function () { updateToggleBtn(v); });
    v.addEventListener("pause", function () { updateToggleBtn(v); });
    v.addEventListener("ended", function () { updateToggleBtn(v); });
    v.addEventListener("click", function () {
      if (window.innerWidth <= 768) {
        if (v.paused) v.play().catch(function () {});
        else v.pause();
      }
    });
  });

  // Focusable Play/Pause toggle button on phones (Tab -> Enter/Space never advances carousel)
  document.querySelectorAll(".clip-toggle-btn").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var wrap = btn.closest(".clip-wrap");
      var v = wrap && wrap.querySelector("video");
      if (!v) return;
      if (v.paused) {
        v.play().catch(function () {
          v.setAttribute("controls", "");
        });
      } else {
        v.pause();
      }
      updateToggleBtn(v);
    });
    btn.addEventListener("keydown", function (e) {
      if (e.key === " " || e.key === "Enter") {
        e.stopPropagation();
      }
    });
  });

  // Synced segment jump strips
  document.querySelectorAll(".synced-video").forEach(function (vid) {
    var segs = [];
    try { segs = JSON.parse(vid.getAttribute("data-segments") || "[]"); } catch (e) {}
    var card = vid.closest(".card-media-col");
    if (!card || !segs.length) return;
    var btns = Array.prototype.slice.call(card.querySelectorAll(".obj-seg"));
    function highlight(t) {
      var activeIdx = -1;
      for (var i = 0; i < segs.length; i++) {
        if (t >= segs[i].start && t < segs[i].end) { activeIdx = i; break; }
        if (i === segs.length - 1 && t >= segs[i].start && t <= segs[i].end + 0.15) { activeIdx = i; }
      }
      btns.forEach(function (b, bi) {
        b.classList.toggle("is-active", bi === activeIdx);
        if (bi === activeIdx) b.setAttribute("aria-current", "true");
        else b.removeAttribute("aria-current");
      });
    }
    vid.addEventListener("timeupdate", function () { highlight(vid.currentTime || 0); });
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        var st = parseFloat(b.getAttribute("data-start") || "0");
        if (isNaN(st)) return;
        var noAuto = vid.hasAttribute("data-no-autoplay");
        var targetT = st + 0.05;
        function applySeek() {
          vid.currentTime = targetT;
          highlight(targetT);
          if (noAuto) {
            vid.pause();
            updateToggleBtn(vid);
          } else {
            vid.play().catch(function () {});
          }
        }
        if (vid.readyState >= 1) {
          applySeek();
        } else {
          vid.addEventListener("loadedmetadata", applySeek, { once: true });
          vid.load();
        }
      });
    });
  });

  // Carousels with equal desktop height, touch swipe (guarded on controls), keyboard support
  var carousels = Array.prototype.slice.call(document.querySelectorAll(".carousel-shell"));

  function pauseSlideVideos(slide) {
    slide.querySelectorAll("video").forEach(function (v) { v.pause(); });
  }
  function playSlideVideos(slide) {
    if (reducedMotion) return;
    slide.querySelectorAll("video").forEach(function (v) {
      if (v.hasAttribute("data-no-autoplay")) return;
      v.play().catch(function () { updateToggleBtn(v); });
    });
  }

  carousels.forEach(function (shell) {
    var slides = Array.prototype.slice.call(shell.querySelectorAll(".carousel-slide"));
    var dots = Array.prototype.slice.call(shell.querySelectorAll(".carousel-dot"));
    var countEl = shell.querySelector(".carousel-count");
    var idx = 0;

    function go(nextIdx, shouldPlay) {
      if (!slides.length) return;
      pauseSlideVideos(slides[idx]);
      slides[idx].classList.remove("is-active");
      slides[idx].setAttribute("aria-hidden", "true");
      slides[idx].setAttribute("inert", "");
      if (dots[idx]) {
        dots[idx].classList.remove("is-active");
        dots[idx].removeAttribute("aria-current");
      }
      idx = (nextIdx + slides.length) % slides.length;
      slides[idx].classList.add("is-active");
      slides[idx].removeAttribute("aria-hidden");
      slides[idx].removeAttribute("inert");
      if (dots[idx]) {
        dots[idx].classList.add("is-active");
        dots[idx].setAttribute("aria-current", "true");
      }
      if (countEl) countEl.textContent = (idx + 1) + " / " + slides.length;
      if (shouldPlay) playSlideVideos(slides[idx]);
    }

    var prevBtn = shell.querySelector(".carousel-prev");
    var nextBtn = shell.querySelector(".carousel-next");
    if (prevBtn) prevBtn.addEventListener("click", function () { go(idx - 1, true); });
    if (nextBtn) nextBtn.addEventListener("click", function () { go(idx + 1, true); });
    dots.forEach(function (d, di) {
      d.addEventListener("click", function () { go(di, true); });
    });

    shell.addEventListener("keydown", function (e) {
      if (document.activeElement && (document.activeElement.tagName === "VIDEO" || document.activeElement.classList.contains("clip-toggle-btn"))) return;
      if (e.key === "ArrowLeft") { e.preventDefault(); go(idx - 1, true); }
      else if (e.key === "ArrowRight") { e.preventDefault(); go(idx + 1, true); }
    });

    // Touch swipe (ignore swipes starting on a video with native controls so scrubbing works cleanly)
    var touchStartX = null;
    var touchStartY = null;
    shell.addEventListener("touchstart", function (e) {
      if (e.target && e.target.tagName === "VIDEO" && e.target.hasAttribute("controls")) {
        touchStartX = null;
        return;
      }
      if (e.touches && e.touches.length === 1) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      }
    }, { passive: true });
    shell.addEventListener("touchend", function (e) {
      if (touchStartX === null || !e.changedTouches || !e.changedTouches.length) return;
      var dx = e.changedTouches[0].clientX - touchStartX;
      var dy = e.changedTouches[0].clientY - touchStartY;
      touchStartX = null;
      touchStartY = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.2) {
        go(dx < 0 ? idx + 1 : idx - 1, true);
      }
    }, { passive: true });
  });

  // Observe every clip so off-screen clips always pause (and only non-stepped clips auto-play when motion is allowed)
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var v = en.target;
        var slide = v.closest(".carousel-slide");
        if (slide && !slide.classList.contains("is-active")) return;
        if (en.isIntersecting) {
          if (!reducedMotion && !v.hasAttribute("data-no-autoplay")) {
            v.play().catch(function () { updateToggleBtn(v); });
          }
        } else {
          v.pause();
        }
      });
    }, { threshold: 0.25 });
    document.querySelectorAll("video.example-clip").forEach(function (v) { io.observe(v); });
  }

  // Phone full-screen play for method trace video
  var traceBtn = document.querySelector(".trace-play-btn");
  var traceFallback = document.querySelector(".trace-phone-fallback");
  var traceVideo = document.querySelector(".trace-video-desktop");
  if (traceBtn && traceFallback && traceVideo) {
    traceBtn.addEventListener("click", function () {
      traceFallback.classList.add("is-playing");
      traceVideo.classList.add("is-playing");
      traceVideo.play().catch(function () {});
      try {
        if (traceVideo.requestFullscreen) traceVideo.requestFullscreen().catch(function () {});
        else if (traceVideo.webkitEnterFullscreen) traceVideo.webkitEnterFullscreen();
      } catch (e) {}
    });
  }

  // Citation copy
  var copyBtn = document.querySelector(".copy-btn");
  var citePre = document.querySelector(".cite-pre");
  if (copyBtn && citePre) {
    copyBtn.addEventListener("click", function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(citePre.textContent.trim()).then(function () {
          copyBtn.textContent = "Copied";
          setTimeout(function () { copyBtn.textContent = "Copy"; }, 1800);
        });
      }
    });
  }

  window.addEventListener("load", syncClipControls);
  window.addEventListener("resize", syncClipControls);
  syncClipControls();
})();
