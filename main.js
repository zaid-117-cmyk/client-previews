gsap.registerPlugin(ScrollTrigger);

// Initialize Lenis for Momentum Scrolling
const lenis = new Lenis({
  duration: 1.0, // Slightly faster for a lighter feel
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smooth: true
});

lenis.on('scroll', ScrollTrigger.update);

gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});
gsap.ticker.lagSmoothing(0);

// Animations once DOM is loaded
document.addEventListener("DOMContentLoaded", () => {

  // Hero Text Animation (SplitText style fade up)
  gsap.from(".reveal-text", {
    y: 30, // Reduced from 50px for a more subtle, minimal entrance
    opacity: 0,
    duration: 1.0, // Faster
    stagger: 0.15,
    ease: "power3.out",
    delay: 0.1
  });

  // Scroll Reveal Animations for all cards and text
  const revealElements = document.querySelectorAll(".scroll-reveal");

  revealElements.forEach((el) => {
    gsap.from(el, {
      y: 40, // Reduced from 60px
      opacity: 0,
      duration: 0.8, // Faster, snappier reveal
      ease: "power2.out",
      scrollTrigger: {
        trigger: el,
        start: "top 90%", // Trigger slightly earlier
        toggleActions: "play none none reverse"
      }
    });
  });

});
