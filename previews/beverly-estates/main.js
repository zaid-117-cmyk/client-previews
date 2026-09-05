document.addEventListener("DOMContentLoaded", async () => {
  // Load dynamic data
  let config = {};
  try {
    const res = await fetch("./siteConfig.json");
    if (res.ok) {
      config = await res.json();
    }
  } catch (err) {
    console.warn("Could not load siteConfig.json", err);
  }

  // Populate Hero
  if (config.companyName) document.title = config.companyName + " | Exclusive Estates";
  if (config.baseLocation) document.getElementById("location").textContent = config.baseLocation;
  if (config.heroTitle) document.getElementById("hero-title").textContent = config.heroTitle;
  if (config.heroSubtitle) document.getElementById("hero-subtitle").textContent = config.heroSubtitle;
  
  if (config.companyName) document.getElementById("company-name").textContent = config.companyName;

  if (config.bookingCtaUrl) {
    document.getElementById("book-btn").onclick = () => {
      window.open(config.bookingCtaUrl, "_blank");
    };
  }

  // Populate Properties Showcase
  const showcase = document.getElementById("properties-section");
  if (config.services && config.services.length > 0) {
    config.services.forEach(prop => {
      const card = document.createElement("div");
      card.className = "property-card";
      card.innerHTML = `
        <h3>${prop.title}</h3>
        <p>${prop.desc}</p>
      `;
      showcase.appendChild(card);
    });
  }

  initAnimations();
});

function initAnimations() {
  // 1. Lenis Smooth Scroll Setup
  const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    direction: 'vertical',
    gestureDirection: 'vertical',
    smooth: true,
  });

  function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  }
  requestAnimationFrame(raf);

  // Keep GSAP in sync with Lenis
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => {
    lenis.raf(time * 1000);
  });
  gsap.ticker.lagSmoothing(0, 0);

  // 2. Hide loader
  const loader = document.querySelector(".loader");
  gsap.to(loader, {
    opacity: 0,
    duration: 1.5,
    delay: 1,
    ease: "power2.inOut",
    onComplete: () => {
      loader.style.display = "none";
      playInitialAnimations();
    }
  });

  // 3. Setup Video Scrubbing 
  const video = document.getElementById("bg-video");
  
  // Only scrub if video metadata is loaded
  video.addEventListener("loadedmetadata", () => {
    // Apple-style video scrub tied strictly to scroll
    let tl = gsap.timeline({
      defaults: { duration: 1 },
      scrollTrigger: {
        trigger: ".content",
        start: "top top",
        end: "bottom bottom",
        scrub: 1.5 // Smooth interpolation for the scrub
      }
    });

    tl.fromTo(video, 
      { currentTime: 0 }, 
      { currentTime: video.duration || 1, ease: "none" }
    );
    
    // Scale up slightly as user scrolls down for parallax feel
    tl.fromTo(".video-container", 
      { scale: 1 }, 
      { scale: 1.1, ease: "none" }, 
      0
    );
  });
}

function playInitialAnimations() {
  // Stagger in the glass cards
  const cards = gsap.utils.toArray(".glass-card, .property-card");
  
  cards.forEach(card => {
    gsap.to(card, {
      y: 0,
      opacity: 1,
      duration: 1,
      ease: "power3.out",
      scrollTrigger: {
        trigger: card,
        start: "top 85%",
        toggleActions: "play none none reverse"
      }
    });
  });
}
