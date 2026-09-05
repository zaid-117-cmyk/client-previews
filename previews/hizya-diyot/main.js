gsap.registerPlugin(ScrollTrigger);

// Initialize Lenis for Momentum Scrolling
const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smooth: true
});

lenis.on('scroll', ScrollTrigger.update);

gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});
gsap.ticker.lagSmoothing(0);


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
  
  if (config.services && config.services.length >= 2) {
    document.getElementById('service-1-title').innerHTML = config.services[0].title;
    document.getElementById('service-1-desc').innerHTML = config.services[0].desc;
    document.getElementById('service-2-title').innerHTML = config.services[1].title;
    document.getElementById('service-2-desc').innerHTML = config.services[1].desc;
  }
  
  if (config.companyName) {
    document.getElementById('footer-biz-name').innerHTML = config.companyName;
    document.title = config.companyName + " - Private Yacht Charters";
  }
  
  if (config.bookingCtaUrl) {
    document.getElementById('contact-btn').href = config.bookingCtaUrl;
  }
  
  document.getElementById('year').textContent = new Date().getFullYear();

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
        scrub: 1,
      }
    });

    // The user requested explicit video scroll scrubbing:
    tl.to(video, {
      currentTime: video.duration,
      ease: "none"
    }, 0);

    // Luxurious Scroll Effects: Scale up slightly as the user scrolls down
    tl.fromTo(".video-container", 
      { scale: 1, filter: "brightness(1)" }, 
      { scale: 1.15, filter: "brightness(0.6)", ease: "none" }, 
      0
    );
  }

  // Fallback in case loadedmetadata doesn't fire (e.g. cached video)
  if (video.readyState >= 1) {
    setupScrollAnimation();
  } else {
    video.addEventListener("loadedmetadata", setupScrollAnimation);
  }

  // Animate the text sections fading in and out
  const sections = gsap.utils.toArray(".section");
  
  sections.forEach((sec) => {
    const elements = sec.querySelectorAll("h1, h2, p, .contact-card");
    
    // Fade in
    gsap.fromTo(elements, 
      { y: 60, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: 1,
        stagger: 0.2,
        scrollTrigger: {
          trigger: sec,
          start: "top 75%",
          end: "center center",
          scrub: 1
        }
      }
    );
    
    // Fade out (skip for the contact section so it remains visible at the bottom)
    if (!sec.classList.contains("contact-section")) {
      gsap.to(elements, {
        y: -60,
        opacity: 0,
        scrollTrigger: {
          trigger: sec,
          start: "center center",
          end: "bottom 25%",
          scrub: 1
        }
      });
    }
  });
}
