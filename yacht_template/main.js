gsap.registerPlugin(ScrollTrigger);

document.addEventListener("DOMContentLoaded", async () => {
  // Load dynamic data
  let config = {};
  try {
    const response = await fetch('./siteConfig.json');
    if (response.ok) {
      config = await response.json();
    }
  } catch (e) {
    console.warn("Could not load siteConfig.json, using defaults.");
  }
  
  // Populate DOM
  if (config.heroTitle) document.getElementById('hero-title').innerHTML = config.heroTitle;
  if (config.heroSubtitle) document.getElementById('hero-subtitle').innerHTML = config.heroSubtitle;
  
  const services = config.services || (config.fleet ? config.fleet.map(f => ({ title: f.name, desc: f.specs ? `${f.specs} - ${f.dayRate || ''}` : f.dayRate })) : null);
  if (services && services.length >= 2) {
    document.getElementById('service-1-title').innerHTML = services[0].title;
    document.getElementById('service-1-desc').innerHTML = services[0].desc;
    document.getElementById('service-2-title').innerHTML = services[1].title;
    document.getElementById('service-2-desc').innerHTML = services[1].desc;
  }
  
  if (config.companyName) {
    document.getElementById('footer-biz-name').innerHTML = config.companyName;
    document.title = config.companyName + " - Private Yacht Charters";
  }
  
  if (config.bookingCtaUrl) {
    document.getElementById('contact-btn').href = config.bookingCtaUrl;
  }
  
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  initAnimations();
});

function initAnimations() {
  const video = document.getElementById("hero-video");

  // Force video to load
  video.load();

  let isVideoSetup = false;

  function setupScrollAnimation() {
    if (isVideoSetup) return;
    
    // Wait until we have a valid duration
    if (!video.duration || isNaN(video.duration)) {
      setTimeout(setupScrollAnimation, 100);
      return;
    }
    
    isVideoSetup = true;
    
    // Pause the video immediately so it doesn't play naturally
    video.pause();

    let tl = gsap.timeline({
      scrollTrigger: {
        trigger: ".content-overlay",
        start: "top top",
        end: "bottom bottom",
        scrub: 1, // Smooth scrubbing
      }
    });

    // Animate video current time from 0 to duration
    tl.to(video, {
      currentTime: video.duration,
      ease: "none"
    });
  }

  // Fallback in case loadedmetadata doesn't fire (e.g. cached video)
  if (video.readyState >= 1) {
    setupScrollAnimation();
  } else {
    video.addEventListener("loadedmetadata", setupScrollAnimation);
  }

  // Animate the text sections fading in and out
  const sections = document.querySelectorAll(".section");
  
  sections.forEach((sec, i) => {
    // Fade in
    gsap.fromTo(sec.children, 
      { y: 50, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        scrollTrigger: {
          trigger: sec,
          start: "top 80%",
          end: "center center",
          scrub: true
        }
      }
    );
    
    // Fade out (skip for the contact section so it remains visible at the bottom)
    if (!sec.classList.contains("contact-section")) {
      gsap.to(sec.children, {
        y: -50,
        opacity: 0,
        scrollTrigger: {
          trigger: sec,
          start: "center center",
          end: "bottom 20%",
          scrub: true
        }
      });
    }
  });
}
